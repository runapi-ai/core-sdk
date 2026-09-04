package core

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// TaskCreateResponse is the response returned when an async task is created.
type TaskCreateResponse struct {
	TaskBillingFacts
	// ID is the task ID for tracking and retrieval.
	ID string `json:"id"`
	// Status is the initial task status, typically "processing".
	Status string `json:"status,omitempty"`
	// TaskReplayed is true when this idempotency key reused the original task.
	TaskReplayed bool `json:"task_replayed,omitempty"`
}

// HybridAcceptance is the accepted branch of a hybrid POST. Location must be
// treated as an opaque URL when subscribing for the terminal result.
type HybridAcceptance struct {
	TaskCreateResponse
	Location       string
	RetryAfter     time.Duration
	IdempotencyKey string
}

// HybridCreateResponse is either a direct terminal result or an accepted Task.
type HybridCreateResponse[T any] struct {
	Terminal   *T
	Acceptance *HybridAcceptance
}

type hybridTaskResult struct {
	ID       string `json:"id"`
	Status   string `json:"status"`
	Response *struct {
		Status      int               `json:"status"`
		ContentType string            `json:"content_type"`
		Headers     map[string]string `json:"headers"`
		Body        json.RawMessage   `json:"body"`
	} `json:"response"`
}

// TaskBillingFacts contains the persisted billing facts for a task. Each fact
// is nil when it was not recorded, including tasks created before billing facts
// were persisted; a recorded zero is represented by a non-nil fact with
// zero-valued amounts.
type TaskBillingFacts struct {
	Billing *TaskBilling `json:"billing"`
}

// TaskBilling contains persisted reservation, settlement, and refund facts.
type TaskBilling struct {
	Reservation *Reservation `json:"reservation"`
	Settlement  *Settlement  `json:"settlement"`
	Refund      *Refund      `json:"refund"`
}

// Reservation is the accepted task's estimated charge in cents.
type Reservation struct {
	AmountCents int64 `json:"amount_cents"`
}

// Settlement is the final task charge. AmountMicroCents preserves sub-cent
// precision and ChargedAmountCents is the amount drained from balance.
type Settlement struct {
	ChargedAmountCents int64 `json:"charged_amount_cents"`
	AmountMicroCents   int64 `json:"amount_micro_cents"`
}

// Refund records when a task charge was reversed in UTC RFC 3339 form.
type Refund struct {
	RefundedAt string `json:"refunded_at"`
}

// GetID returns the task ID assigned by the server.
func (r TaskCreateResponse) GetID() string { return r.ID }

// GetStatus returns the initial task status.
func (r TaskCreateResponse) GetStatus() string { return r.Status }

// GetError always returns empty; creation responses do not carry error details.
func (r TaskCreateResponse) GetError() string { return "" }

// PostJSON sends a POST request with a JSON body and decodes the response into T.
func PostJSON[T any](ctx context.Context, httpClient HTTPClient, path string, body any, requestOptions RequestOptions) (*T, error) {
	payload, err := httpClient.Request(ctx, "POST", path, &HTTPRequestOptions{Body: body, Headers: requestOptions.Headers, Request: requestOptions})
	if err != nil {
		return nil, err
	}
	return DecodeResponse[T](payload)
}

// GetJSON sends a GET request and decodes the response into T.
func GetJSON[T any](ctx context.Context, httpClient HTTPClient, path string, requestOptions RequestOptions) (*T, error) {
	payload, err := httpClient.Request(ctx, "GET", path, &HTTPRequestOptions{Headers: requestOptions.Headers, Request: requestOptions})
	if err != nil {
		return nil, err
	}
	return DecodeResponse[T](payload)
}

// CreateHybrid sends a hybrid POST and returns its terminal response or its
// accepted Task. It generates an Idempotency-Key before the initial request.
func CreateHybrid[T any](ctx context.Context, httpClient HTTPClient, path string, body any, requestOptions RequestOptions) (*HybridCreateResponse[T], error) {
	headers := make(map[string]string, len(requestOptions.Headers)+1)
	for name, value := range requestOptions.Headers {
		if strings.EqualFold(name, "Idempotency-Key") {
			if strings.TrimSpace(value) == "" {
				continue
			}
			if existing := headers["Idempotency-Key"]; existing != "" && existing != value {
				return nil, NewError(ErrValidation, "conflicting Idempotency-Key headers", http.StatusUnprocessableEntity, "", nil, nil)
			}
			headers["Idempotency-Key"] = value
			continue
		}
		headers[name] = value
	}
	key := headers["Idempotency-Key"]
	if key == "" {
		var err error
		key, err = newIdempotencyKey()
		if err != nil {
			return nil, err
		}
		headers["Idempotency-Key"] = key
	}
	client, ok := httpClient.(ResponseHTTPClient)
	if !ok {
		payload, err := httpClient.Request(ctx, http.MethodPost, path, &HTTPRequestOptions{Body: body, Headers: headers, Request: requestOptions})
		if err != nil {
			return nil, err
		}
		var acceptance TaskCreateResponse
		if json.Unmarshal(payload, &acceptance) == nil {
			status := strings.ToLower(strings.TrimSpace(acceptance.Status))
			if acceptance.ID != "" && (status == "pending" || status == "processing") {
				return nil, NewError(ErrNetwork, "accepted hybrid Task requires response-aware HTTP client", http.StatusAccepted, "", acceptance, nil)
			}
		}
		terminal, err := DecodeResponse[T](payload)
		if err != nil {
			return nil, err
		}
		return &HybridCreateResponse[T]{Terminal: terminal}, nil
	}
	response, err := client.RequestWithResponse(ctx, http.MethodPost, path, &HTTPRequestOptions{Body: body, Headers: headers, Request: requestOptions})
	if err != nil {
		return nil, err
	}
	if response.StatusCode != http.StatusAccepted {
		terminal, err := DecodeResponse[T](response.Body)
		if err != nil {
			return nil, err
		}
		return &HybridCreateResponse[T]{Terminal: terminal}, nil
	}
	acceptance, err := DecodeResponse[TaskCreateResponse](response.Body)
	if err != nil {
		return nil, err
	}
	location := response.Header.Get("Location")
	if strings.TrimSpace(location) == "" {
		return nil, NewError(ErrTaskFailed, "accepted task is missing Location", http.StatusAccepted, "", acceptance, nil)
	}
	return &HybridCreateResponse[T]{Acceptance: &HybridAcceptance{TaskCreateResponse: *acceptance, Location: location, RetryAfter: ParseRetryAfter(response.Header.Get("Retry-After")), IdempotencyKey: key}}, nil
}

// SubscribeHybrid follows an accepted Task Location until its stored terminal
// response is available. Retry-After from each response controls the next poll.
func SubscribeHybrid[T any](ctx context.Context, httpClient HTTPClient, acceptance *HybridAcceptance, requestOptions RequestOptions, pollingOptions PollingOptions) (*T, error) {
	client, ok := httpClient.(ResponseHTTPClient)
	if !ok {
		return nil, NewError(ErrNetwork, "hybrid lifecycle requires response-aware HTTP client", 0, "", nil, nil)
	}
	if acceptance == nil || strings.TrimSpace(acceptance.Location) == "" {
		return nil, NewError(ErrValidation, "accepted task Location is required", http.StatusUnprocessableEntity, "", nil, nil)
	}
	if pollingOptions.MaxWait <= 0 {
		pollingOptions.MaxWait = DefaultMaxWait
	}
	if pollingOptions.PollInterval <= 0 {
		pollingOptions.PollInterval = DefaultPollInterval
	}
	deadline := time.Now().Add(pollingOptions.MaxWait)
	wait := acceptance.RetryAfter
	for {
		if wait > 0 {
			if remaining := time.Until(deadline); remaining <= 0 {
				return nil, NewError(ErrTaskTimeout, "Task polling timed out", 0, "", nil, context.DeadlineExceeded)
			} else if wait > remaining {
				wait = remaining
			}
			select {
			case <-ctx.Done():
				return nil, NewError(ErrTaskTimeout, "Task polling timed out", 0, "", nil, ctx.Err())
			case <-time.After(wait):
			}
		}
		response, err := client.RequestWithResponse(ctx, http.MethodGet, acceptance.Location, &HTTPRequestOptions{Headers: requestOptions.Headers, Request: requestOptions})
		if err != nil {
			return nil, err
		}
		var task hybridTaskResult
		if err := json.Unmarshal(response.Body, &task); err != nil {
			return nil, NewError(ErrNetwork, "task result must be valid JSON", response.StatusCode, "", nil, err)
		}
		switch NormalizeStatus(task.Status) {
		case "completed":
			if task.Response == nil {
				return nil, NewError(ErrTaskFailed, "completed task is missing stored response", 0, "", task, nil)
			}
			return decodeStoredHybridResponse[T](task.Response.Body, task.Response.ContentType)
		case "failed":
			if task.Response == nil {
				return nil, NewError(ErrTaskFailed, "Task failed", 0, "", task, nil)
			}
			headers := make(http.Header, len(task.Response.Headers))
			for name, value := range task.Response.Headers {
				headers.Set(name, value)
			}
			if task.Response.ContentType != "" {
				headers.Set("Content-Type", task.Response.ContentType)
			}
			return nil, ErrorFromResponse(&http.Response{StatusCode: task.Response.Status, Header: headers}, task.Response.Body)
		}
		wait = ParseRetryAfter(response.Header.Get("Retry-After"))
		if wait <= 0 {
			wait = pollingOptions.PollInterval
		}
	}
}

// RunHybrid sends a hybrid POST and follows an accepted Task until its stored
// terminal response is available.
func RunHybrid[T any](ctx context.Context, httpClient HTTPClient, path string, body any, requestOptions RequestOptions, pollingOptions PollingOptions) (*T, error) {
	created, err := CreateHybrid[T](ctx, httpClient, path, body, requestOptions)
	if err != nil {
		return nil, err
	}
	if created.Terminal != nil {
		return created.Terminal, nil
	}
	return SubscribeHybrid[T](ctx, httpClient, created.Acceptance, requestOptions, pollingOptions)
}

func decodeStoredHybridResponse[T any](body json.RawMessage, contentType string) (*T, error) {
	var response T
	raw, ok := any(&response).(*json.RawMessage)
	if !ok {
		return DecodeResponse[T](body)
	}

	mediaType := strings.ToLower(strings.TrimSpace(strings.SplitN(contentType, ";", 2)[0]))
	if mediaType == "application/json" || strings.HasSuffix(mediaType, "+json") {
		*raw = append((*raw)[:0], body...)
		return &response, nil
	}

	var text string
	if err := json.Unmarshal(body, &text); err != nil {
		return nil, fmt.Errorf("decode stored raw response: %w", err)
	}
	*raw = append((*raw)[:0], text...)
	return &response, nil
}

func newIdempotencyKey() (string, error) {
	bytes := make([]byte, 16)
	if _, err := rand.Read(bytes); err != nil {
		return "", NewError(ErrNetwork, "failed to generate idempotency key", 0, "", nil, err)
	}
	return hex.EncodeToString(bytes), nil
}

// RunAsync creates an async task and polls until completion.
func RunAsync[T TaskResponse](ctx context.Context, create func(context.Context) (*TaskCreateResponse, error), get func(context.Context, string) (*T, error), pollingOptions PollingOptions) (*T, error) {
	created, err := create(ctx)
	if err != nil {
		return nil, err
	}
	if created.ID == "" {
		return nil, NewError(ErrTaskFailed, "task id missing from create response", 0, "", created, nil)
	}
	result, err := PollUntilComplete(ctx, func(ctx context.Context) (T, error) {
		response, err := get(ctx, created.ID)
		if err != nil {
			var zero T
			return zero, err
		}
		return *response, nil
	}, pollingOptions)
	if err != nil {
		return nil, err
	}
	return &result, nil
}

// ResourcePath joins a base API path with a resource ID.
func ResourcePath(basePath, id string) string {
	return fmt.Sprintf("%s/%s", basePath, id)
}
