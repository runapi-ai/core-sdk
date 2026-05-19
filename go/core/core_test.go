package core

import (
	"net/http"
	"testing"
)

func TestErrorFromResponseMapsRateLimit(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusTooManyRequests, Header: make(http.Header)}
	response.Header.Set("retry-after", "3")
	err := ErrorFromResponse(response, []byte(`{"message":"slow down"}`))
	apiErr, ok := err.(*Error)
	if !ok {
		t.Fatalf("expected *Error, got %T", err)
	}
	if apiErr.Code != ErrRateLimit {
		t.Fatalf("unexpected error code: %s", apiErr.Code)
	}
	if apiErr.RetryAfter.Seconds() != 3 {
		t.Fatalf("unexpected retry-after: %s", apiErr.RetryAfter)
	}
}

func TestCompactParamsDropsOnlyNilAndEmptyString(t *testing.T) {
	falseValue := false
	params := map[string]any{"prompt": "hi", "empty": "", "nil": nil, "zero": 0, "false": falseValue, "list": []any{0, false, ""}}
	result := CompactParams(params)
	if _, ok := result["empty"]; ok {
		t.Fatal("expected empty string to be removed")
	}
	if _, ok := result["nil"]; ok {
		t.Fatal("expected nil to be removed")
	}
	if result["zero"] != float64(0) {
		t.Fatalf("expected zero to be preserved: %#v", result)
	}
	if result["false"] != false {
		t.Fatalf("expected false to be preserved: %#v", result)
	}
}
