package core

import (
	"context"
	"fmt"
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
