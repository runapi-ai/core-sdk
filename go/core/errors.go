// Package core provides the shared HTTP client, error types, polling,
// and retry logic used by all RunAPI service packages.
package core

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// ErrorCode identifies the category of an API error.
type ErrorCode string

const (
	// ErrAuthentication indicates a missing or invalid API key (HTTP 401).
	ErrAuthentication ErrorCode = "authentication"
	// ErrInsufficientCredits indicates the account has insufficient credits (HTTP 402).
	ErrInsufficientCredits ErrorCode = "insufficient_credits"
	// ErrNotFound indicates the requested resource does not exist (HTTP 404).
	ErrNotFound ErrorCode = "not_found"
	// ErrValidation indicates request validation failed (HTTP 400, 422).
	ErrValidation ErrorCode = "validation"
	// ErrConflict indicates the request conflicts with current resource state (HTTP 409).
	ErrConflict ErrorCode = "conflict"
	// ErrRateLimit indicates the rate limit was exceeded (HTTP 429).
	ErrRateLimit ErrorCode = "rate_limit"
	// ErrServiceUnavailable indicates the service is temporarily unavailable (HTTP 503).
	ErrServiceUnavailable ErrorCode = "service_unavailable"
	// ErrServer indicates an internal server error (HTTP 5xx).
	ErrServer ErrorCode = "server"
	// ErrNetwork indicates a network connection failure.
	ErrNetwork ErrorCode = "network"
	// ErrTimeout indicates the HTTP request exceeded the configured timeout.
	ErrTimeout ErrorCode = "timeout"
	// ErrTaskTimeout indicates polling for task completion exceeded the maximum wait time.
	ErrTaskTimeout ErrorCode = "task_timeout"
	// ErrTaskFailed indicates the async task failed during processing.
	ErrTaskFailed ErrorCode = "task_failed"
)

// Error is the base error type for all RunAPI SDK errors.
// It includes HTTP status, request ID, and response details.
type Error struct {
	Message    string
	Code       ErrorCode
	Status     int
	RequestID  string
	Details    any
	RetryAfter time.Duration
	Err        error
}

func (e *Error) Error() string {
	if e == nil {
		return ""
	}
	return e.Message
}

func (e *Error) Unwrap() error {
	if e == nil {
		return nil
	}
	return e.Err
}

// NewError creates a new Error with the given fields.
func NewError(code ErrorCode, message string, status int, requestID string, details any, err error) *Error {
	return &Error{Message: message, Code: code, Status: status, RequestID: requestID, Details: details, Err: err}
}

// IsAuthentication reports whether err is an authentication error.
func IsAuthentication(err error) bool { return hasCode(err, ErrAuthentication) }

// IsInsufficientCredits reports whether err is an insufficient credits error.
func IsInsufficientCredits(err error) bool { return hasCode(err, ErrInsufficientCredits) }

// IsNotFound reports whether err is a not found error.
func IsNotFound(err error) bool { return hasCode(err, ErrNotFound) }

// IsValidation reports whether err is a validation error.
func IsValidation(err error) bool { return hasCode(err, ErrValidation) }

// IsConflict reports whether err is a conflict error.
func IsConflict(err error) bool { return hasCode(err, ErrConflict) }

// IsRateLimit reports whether err is a rate limit error.
func IsRateLimit(err error) bool { return hasCode(err, ErrRateLimit) }

// IsServiceUnavailable reports whether err is a service unavailable error.
func IsServiceUnavailable(err error) bool { return hasCode(err, ErrServiceUnavailable) }

// IsServer reports whether err is a server error.
func IsServer(err error) bool { return hasCode(err, ErrServer) }

// IsNetwork reports whether err is a network error.
func IsNetwork(err error) bool { return hasCode(err, ErrNetwork) }

// IsTimeout reports whether err is an HTTP request timeout error.
func IsTimeout(err error) bool { return hasCode(err, ErrTimeout) }

// IsTaskTimeout reports whether err is a task polling timeout error.
func IsTaskTimeout(err error) bool { return hasCode(err, ErrTaskTimeout) }

// IsTaskFailed reports whether err is a task failed error.
func IsTaskFailed(err error) bool { return hasCode(err, ErrTaskFailed) }

func hasCode(err error, code ErrorCode) bool {
	target, ok := errors.AsType[*Error](err)
	return ok && target.Code == code
}

// ErrorFromResponse constructs an appropriate Error from an HTTP response.
// It maps status codes to error codes and extracts error messages from the body.
func ErrorFromResponse(response *http.Response, body []byte) error {
	status := response.StatusCode
	requestID := response.Header.Get("x-request-id")
	details := parseBody(body)
	message := extractErrorMessage(details)
	if message == "" {
		message = defaultMessageForStatus(status)
	}
	if message == "" {
		message = "Request failed"
	}

	apiErr := &Error{
		Message:   message,
		Code:      codeForStatus(status),
		Status:    status,
		RequestID: requestID,
		Details:   details,
	}
	if apiErr.Code == ErrRateLimit {
		apiErr.RetryAfter = ParseRetryAfter(response.Header.Get("retry-after"))
	}
	return apiErr
}

func codeForStatus(status int) ErrorCode {
	switch {
	case status == 400 || status == 422:
		return ErrValidation
	case status == 401:
		return ErrAuthentication
	case status == 402:
		return ErrInsufficientCredits
	case status == 404:
		return ErrNotFound
	case status == 409:
		return ErrConflict
	case status == 429:
		return ErrRateLimit
	case status == 503:
		return ErrServiceUnavailable
	case status >= 500 && status <= 505:
		return ErrServer
	default:
		return ErrServer
	}
}

func defaultMessageForStatus(status int) string {
	switch status {
	case 400:
		return "Bad request"
	case 401:
		return "Unauthorized"
	case 402:
		return "Insufficient credits"
	case 404:
		return "Not found"
	case 409:
		return "Conflict"
	case 422:
		return "Validation failed"
	case 429:
		return "Too many requests"
	case 503:
		return "Service unavailable"
	default:
		if status >= 500 {
			return "Server error"
		}
		return ""
	}
}

func extractErrorMessage(body any) string {
	switch value := body.(type) {
	case string:
		return strings.TrimSpace(value)
	case map[string]any:
		if nested, ok := value["error"].(map[string]any); ok {
			if message, _ := nested["message"].(string); strings.TrimSpace(message) != "" {
				return strings.TrimSpace(message)
			}
		}
		for _, key := range []string{"error", "message", "detail", "errorMessage", "msg"} {
			if message, ok := value[key].(string); ok && strings.TrimSpace(message) != "" {
				return strings.TrimSpace(message)
			}
		}
		if errorsList, ok := value["errors"].([]any); ok && len(errorsList) > 0 {
			return extractErrorMessage(errorsList[0])
		}
	case []any:
		if len(value) > 0 {
			return extractErrorMessage(value[0])
		}
	}
	return ""
}

func parseBody(body []byte) any {
	trimmed := strings.TrimSpace(string(body))
	if trimmed == "" {
		return nil
	}
	if looksLikeHTML(trimmed) {
		return map[string]any{"message": "Server returned HTML error page"}
	}
	var parsed any
	if err := json.Unmarshal(body, &parsed); err == nil {
		return parsed
	}
	return trimmed
}

func looksLikeHTML(text string) bool {
	lower := strings.ToLower(text)
	return strings.Contains(lower, "<!doctype") || strings.Contains(lower, "<html")
}

// ParseRetryAfter parses the Retry-After header value as seconds or HTTP-date.
func ParseRetryAfter(header string) time.Duration {
	header = strings.TrimSpace(header)
	if header == "" {
		return 0
	}
	if seconds, err := strconv.Atoi(header); err == nil {
		return time.Duration(seconds) * time.Second
	}
	if when, err := http.ParseTime(header); err == nil {
		if wait := time.Until(when); wait > 0 {
			return wait
		}
	}
	return 0
}

// FormatError returns a human-readable error message, including retry-after info for rate limits.
func FormatError(err error) string {
	if target, ok := errors.AsType[*Error](err); ok {
		if target.Code == ErrRateLimit && target.RetryAfter > 0 {
			return fmt.Sprintf("%s (retry after %s)", target.Message, target.RetryAfter.Round(time.Second))
		}
		return target.Message
	}
	return err.Error()
}
