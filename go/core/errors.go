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

// ErrorCode is an explicit machine-readable reason supplied by RunAPI or by
// an SDK-local error constructor. HTTP response codes are never inferred into
// this field.
type ErrorCode string

const (
	// ErrAuthentication indicates a missing or invalid API key (HTTP 401).
	ErrAuthentication ErrorCode = "authentication"
	// ErrInsufficientCredits indicates the account has insufficient credits (HTTP 402).
	ErrInsufficientCredits ErrorCode = "insufficient_credits"
	// ErrNotFound indicates the requested resource does not exist (HTTP 404).
	ErrNotFound ErrorCode = "not_found"
	// ErrValidation indicates request validation failed (HTTP 400, 413, 422).
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
// Use the Is* helpers (e.g. IsRateLimit, IsInsufficientCredits) rather than
// switching on Code directly, so your checks survive future error code additions.
type Error struct {
	// Message is a human-readable description of the failure.
	Message string
	// Code classifies the error into a category such as rate_limit or validation.
	Code ErrorCode
	// Status is the HTTP status code, or 0 for non-HTTP errors (network, task timeout).
	Status int
	// RequestID is the server-assigned correlation ID from the x-request-id header.
	RequestID string
	// Details holds the parsed response body (typically map[string]any), if available.
	Details any
	// RetryAfter is the server-suggested wait duration before retrying, populated on 429 responses.
	RetryAfter time.Duration
	// Err is the underlying error, if any, for use with errors.Unwrap.
	Err error
}

func (e *Error) Error() string {
	if e == nil {
		return ""
	}
	return e.Message
}

// Unwrap returns the underlying error, supporting errors.Is and errors.As.
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
func IsAuthentication(err error) bool {
	return hasCodeOrStatus(err, ErrAuthentication, http.StatusUnauthorized)
}

// IsInsufficientCredits reports whether err is an insufficient credits error.
func IsInsufficientCredits(err error) bool {
	return hasCodeOrStatus(err, ErrInsufficientCredits, http.StatusPaymentRequired)
}

// IsNotFound reports whether err is a not found error.
func IsNotFound(err error) bool { return hasCodeOrStatus(err, ErrNotFound, http.StatusNotFound) }

// IsValidation reports whether err is a validation error.
func IsValidation(err error) bool {
	return hasCodeOrStatus(err, ErrValidation, http.StatusBadRequest, http.StatusRequestEntityTooLarge, http.StatusUnprocessableEntity)
}

// IsConflict reports whether err is a conflict error.
func IsConflict(err error) bool { return hasCodeOrStatus(err, ErrConflict, http.StatusConflict) }

// IsRateLimit reports whether err is a rate limit error.
func IsRateLimit(err error) bool {
	return hasCodeOrStatus(err, ErrRateLimit, http.StatusTooManyRequests)
}

// IsServiceUnavailable reports whether err is a service unavailable error.
func IsServiceUnavailable(err error) bool {
	return hasCodeOrStatus(err, ErrServiceUnavailable, http.StatusServiceUnavailable)
}

// IsServer reports whether err is a server error.
func IsServer(err error) bool {
	target, ok := errors.AsType[*Error](err)
	return ok && (target.Code == ErrServer || target.Status >= http.StatusInternalServerError)
}

// IsNetwork reports whether err is a network error.
func IsNetwork(err error) bool { return hasCode(err, ErrNetwork) }

// IsTimeout reports whether err is an HTTP request timeout error.
func IsTimeout(err error) bool {
	return hasCodeOrStatus(err, ErrTimeout, http.StatusRequestTimeout)
}

// IsTaskTimeout reports whether err is a task polling timeout error.
func IsTaskTimeout(err error) bool { return hasCode(err, ErrTaskTimeout) }

// IsTaskFailed reports whether err is a task failed error.
func IsTaskFailed(err error) bool { return hasCode(err, ErrTaskFailed) }

func hasCode(err error, code ErrorCode) bool {
	target, ok := errors.AsType[*Error](err)
	return ok && target.Code == code
}

func hasCodeOrStatus(err error, code ErrorCode, statuses ...int) bool {
	target, ok := errors.AsType[*Error](err)
	if !ok {
		return false
	}
	if target.Code == code {
		return true
	}
	for _, status := range statuses {
		if target.Status == status {
			return true
		}
	}
	return false
}

// ErrorFromResponse constructs an appropriate Error from an HTTP response.
// It preserves an explicit API error code and extracts error messages from the body.
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
		Code:      extractErrorCode(details),
		Status:    status,
		RequestID: requestID,
		Details:   details,
	}
	if status == http.StatusTooManyRequests {
		apiErr.RetryAfter = ParseRetryAfter(response.Header.Get("retry-after"))
	}
	return apiErr
}

func extractErrorCode(body any) ErrorCode {
	value, ok := body.(map[string]any)
	if !ok {
		return ""
	}
	nested, ok := value["error"].(map[string]any)
	if !ok {
		return ""
	}
	code, _ := nested["code"].(string)
	return ErrorCode(code)
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
	case 413:
		return "Payload too large"
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
		if IsRateLimit(target) && target.RetryAfter > 0 {
			return fmt.Sprintf("%s (retry after %s)", target.Message, target.RetryAfter.Round(time.Second))
		}
		return target.Message
	}
	return err.Error()
}
