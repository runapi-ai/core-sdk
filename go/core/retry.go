package core

import (
	"math"
	"math/rand"
	"net/http"
	"strings"
	"time"
)

// RetryDelay computes an exponential backoff delay with jitter for the given attempt.
func RetryDelay(attempt int, baseDelay, maxDelay time.Duration) time.Duration {
	if attempt < 1 {
		attempt = 1
	}
	if baseDelay <= 0 {
		baseDelay = DefaultRetryBaseDelay
	}
	if maxDelay <= 0 {
		maxDelay = DefaultRetryMaxDelay
	}
	delay := time.Duration(math.Pow(2, float64(attempt-1))) * baseDelay
	jitter := time.Duration(rand.Float64() * float64(delay) * 0.5)
	delay += jitter
	if delay > maxDelay {
		return maxDelay
	}
	return delay
}

// IsRetryableStatus reports whether the HTTP status code is retryable (429 or 5xx).
func IsRetryableStatus(status int) bool {
	return status == http.StatusTooManyRequests || status >= 500
}

// IsIdempotentMethod reports whether the HTTP method is safe to retry.
func IsIdempotentMethod(method string) bool {
	switch strings.ToUpper(method) {
	case http.MethodGet, http.MethodHead, http.MethodPut, http.MethodDelete, http.MethodOptions:
		return true
	default:
		return false
	}
}
