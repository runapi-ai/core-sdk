package core

import (
	"context"
	"strings"
	"time"
)

// TaskResponse is implemented by async task result types.
type TaskResponse interface {
	GetID() string
	GetStatus() string
	GetError() string
}

// PollUntilComplete repeatedly calls fetcher until the task completes, fails, or times out.
func PollUntilComplete[T TaskResponse](ctx context.Context, fetcher func(context.Context) (T, error), opts PollingOptions) (T, error) {
	var zero T
	if opts.PollInterval <= 0 {
		opts.PollInterval = DefaultPollInterval
	}
	if opts.MaxWait <= 0 {
		opts.MaxWait = DefaultMaxWait
	}

	ctx, cancel := context.WithTimeout(ctx, opts.MaxWait)
	defer cancel()

	timer := time.NewTimer(0)
	defer timer.Stop()
	// Drain the initial fire so the first iteration fetches immediately.
	<-timer.C

	for {
		response, err := fetcher(ctx)
		if err != nil {
			return zero, err
		}
		switch NormalizeStatus(response.GetStatus()) {
		case "completed":
			return response, nil
		case "failed":
			message := response.GetError()
			if message == "" {
				message = "Task failed"
			}
			return zero, NewError(ErrTaskFailed, message, 0, "", response, nil)
		}
		timer.Reset(opts.PollInterval)
		select {
		case <-ctx.Done():
			return zero, NewError(ErrTaskTimeout, "Task polling timed out", 0, "", nil, ctx.Err())
		case <-timer.C:
		}
	}
}

// NormalizeStatus maps backend status strings to "completed", "failed", or "processing".
func NormalizeStatus(status string) string {
	switch strings.ToLower(status) {
	case "completed", "success":
		return "completed"
	case "failed", "error", "generate_failed", "create_task_failed":
		return "failed"
	default:
		return "processing"
	}
}
