package core

import (
	"context"
	"fmt"
)

// TaskCreateResponse is the response returned when an async task is created.
type TaskCreateResponse struct {
	// ID is the task ID for tracking and retrieval.
	ID string `json:"id"`
	// Status is the initial task status, typically "processing".
	Status string `json:"status,omitempty"`
}

func (r TaskCreateResponse) GetID() string     { return r.ID }
func (r TaskCreateResponse) GetStatus() string { return r.Status }
func (r TaskCreateResponse) GetError() string  { return "" }

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
