package core

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"reflect"
	"testing"
)

type pollingTask struct {
	id     string
	status string
	error  string
}

func (task pollingTask) GetID() string     { return task.id }
func (task pollingTask) GetStatus() string { return task.status }
func (task pollingTask) GetError() string  { return task.error }

func TestErrorFromResponseMapsRateLimit(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusTooManyRequests, Header: make(http.Header)}
	response.Header.Set("retry-after", "3")
	err := ErrorFromResponse(response, []byte(`{"message":"slow down"}`))
	apiErr, ok := err.(*Error)
	if !ok {
		t.Fatalf("expected *Error, got %T", err)
	}
	if apiErr.Code != "" {
		t.Fatalf("expected missing HTTP code to remain empty, got %q", apiErr.Code)
	}
	if !IsRateLimit(apiErr) {
		t.Fatal("expected HTTP status to retain rate-limit classification")
	}
	if apiErr.RetryAfter.Seconds() != 3 {
		t.Fatalf("unexpected retry-after: %s", apiErr.RetryAfter)
	}
}

func TestBuildURLRejectsCrossOriginAbsoluteLocation(t *testing.T) {
	_, err := buildURL("https://runapi.ai", "https://attacker.example/tasks/task-1", nil)
	if err == nil {
		t.Fatal("expected cross-origin URL to be rejected")
	}
}

func TestBuildURLAcceptsRelativeAndSameOriginLocations(t *testing.T) {
	for _, location := range []string{"/api/v1/tasks/task-1", "https://runapi.ai/api/v1/tasks/task-1"} {
		resolved, err := buildURL("https://runapi.ai", location, nil)
		if err != nil {
			t.Fatalf("buildURL(%q): %v", location, err)
		}
		if resolved != "https://runapi.ai/api/v1/tasks/task-1" {
			t.Fatalf("unexpected URL: %s", resolved)
		}
	}
}

func TestContinuationErrorsPreserveCodeAndClassifyByStatus(t *testing.T) {
	tests := []struct {
		status int
		code   ErrorCode
		class  func(error) bool
	}{
		{http.StatusBadRequest, "invalid_resource_id", IsValidation},
		{http.StatusConflict, "request_conflict", IsConflict},
		{http.StatusConflict, "source_task_not_ready", IsConflict},
		{http.StatusUnprocessableEntity, "source_task_unusable", IsValidation},
		{http.StatusUnprocessableEntity, "continuation_not_supported", IsValidation},
		{http.StatusTooManyRequests, "rate_limited", IsRateLimit},
		{http.StatusServiceUnavailable, "continuation_unavailable", IsServiceUnavailable},
	}

	for _, tt := range tests {
		t.Run(string(tt.code), func(t *testing.T) {
			response := &http.Response{StatusCode: tt.status, Header: make(http.Header)}
			body := []byte(`{"error":{"code":"` + string(tt.code) + `","message":"failed"}}`)
			err := ErrorFromResponse(response, body)
			apiErr := err.(*Error)

			if apiErr.Code != tt.code {
				t.Fatalf("unexpected code: %q", apiErr.Code)
			}
			if apiErr.Status != tt.status || !tt.class(err) {
				t.Fatalf("unexpected classification: status=%d error=%#v", apiErr.Status, apiErr)
			}
		})
	}
}

func TestErrorFromResponsePreservesOnlyExplicitCode(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusConflict, Header: make(http.Header)}
	explicit := ErrorFromResponse(response, []byte(`{"error":{"code":"source_task_not_ready","message":"wait"}}`)).(*Error)
	missing := ErrorFromResponse(response, []byte(`{"error":{"message":"wait"}}`)).(*Error)

	if explicit.Code != ErrorCode("source_task_not_ready") {
		t.Fatalf("unexpected explicit code: %q", explicit.Code)
	}
	if missing.Code != "" {
		t.Fatalf("expected missing code to remain empty, got %q", missing.Code)
	}
}

func TestErrorFromResponseDoesNotUseLegacyErrorsArrayAsMessage(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusBadRequest, Header: make(http.Header)}
	apiErr := ErrorFromResponse(response, []byte(`{"errors":["First error"]}`)).(*Error)

	if apiErr.Message != "Bad request" {
		t.Fatalf("unexpected message: %q", apiErr.Message)
	}
}

func TestErrorFromResponseKeepsResourceValidationDetails(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusUnprocessableEntity, Header: make(http.Header)}
	apiErr := ErrorFromResponse(response, []byte(`{"error":"Validation failed","errors":{"prompt":["is required"]}}`)).(*Error)

	if apiErr.Message != "Validation failed" {
		t.Fatalf("unexpected message: %q", apiErr.Message)
	}
	details := apiErr.Details.(map[string]any)
	if !reflect.DeepEqual(details["errors"], map[string]any{"prompt": []any{"is required"}}) {
		t.Fatalf("unexpected details: %#v", details)
	}
}

func TestPollUntilCompleteKeepsTerminalTaskErrorString(t *testing.T) {
	task := pollingTask{id: "task_123", status: "failed", error: "Generation failed"}
	_, err := PollUntilComplete(
		context.Background(),
		func(context.Context) (pollingTask, error) { return task, nil },
		DefaultPollingOptions(),
	)
	apiErr := err.(*Error)

	if apiErr.Message != "Generation failed" || !IsTaskFailed(apiErr) {
		t.Fatalf("unexpected task failure: %#v", apiErr)
	}
	if !reflect.DeepEqual(apiErr.Details, task) {
		t.Fatalf("unexpected task details: %#v", apiErr.Details)
	}
}

func TestErrorFromResponseClassifiesPayloadTooLargeAsValidation(t *testing.T) {
	response := &http.Response{StatusCode: http.StatusRequestEntityTooLarge, Header: make(http.Header)}
	err := ErrorFromResponse(response, nil)
	apiErr, ok := err.(*Error)
	if !ok {
		t.Fatalf("expected *Error, got %T", err)
	}
	if apiErr.Code != "" {
		t.Fatalf("expected missing HTTP code to remain empty, got %q", apiErr.Code)
	}
	if !IsValidation(apiErr) {
		t.Fatal("expected HTTP status to retain validation classification")
	}
	if apiErr.Message != "Payload too large" {
		t.Fatalf("unexpected message: %q", apiErr.Message)
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

func TestDefaultHTTPClientSendsMultipartBody(t *testing.T) {
	tmp, err := os.CreateTemp(t.TempDir(), "image-*.png")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := tmp.WriteString("png"); err != nil {
		t.Fatal(err)
	}
	if err := tmp.Close(); err != nil {
		t.Fatal(err)
	}

	var sawMultipart bool
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" || r.URL.Path != "/api/v1/files" {
			t.Fatalf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		if got := r.Header.Get("Authorization"); got != "Bearer test-key" {
			t.Fatalf("unexpected authorization: %s", got)
		}
		if got := r.Header.Get("Content-Type"); got == "" || got == "application/json" {
			t.Fatalf("expected multipart content type, got %q", got)
		}
		if err := r.ParseMultipartForm(1024); err != nil {
			t.Fatal(err)
		}
		if got := r.FormValue("file_name"); got != "image.png" {
			t.Fatalf("unexpected file_name: %s", got)
		}
		if got := r.MultipartForm.Value["languages[]"]; !reflect.DeepEqual(got, []string{"en", "zh"}) {
			t.Fatalf("unexpected languages: %#v", got)
		}
		file, header, err := r.FormFile("file")
		if err != nil {
			t.Fatal(err)
		}
		defer file.Close()
		if header.Filename != "image.png" || header.Header.Get("Content-Type") != "image/png" {
			t.Fatalf("unexpected file header: %#v", header)
		}
		sawMultipart = true
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"url": "https://file.runapi.ai/temp/image.png"})
	}))
	defer server.Close()

	client, err := NewHTTPClient(ClientOptions{APIKey: "test-key", BaseURL: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.Request(context.Background(), "POST", "/api/v1/files", &HTTPRequestOptions{
		Body: MultipartBody{
			Fields:         map[string]string{"file_name": "image.png"},
			RepeatedFields: map[string][]string{"languages[]": {"en", "zh"}},
			Files: map[string]MultipartFile{
				"file": {Path: tmp.Name(), FileName: "image.png", ContentType: "image/png"},
			},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	if !sawMultipart {
		t.Fatal("server did not receive multipart request")
	}
}

func TestDefaultHTTPClientSendsMultipartBodyPointer(t *testing.T) {
	tmp, err := os.CreateTemp(t.TempDir(), "image-*.png")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := tmp.WriteString("png"); err != nil {
		t.Fatal(err)
	}
	if err := tmp.Close(); err != nil {
		t.Fatal(err)
	}

	var sawMultipart bool
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Content-Type"); got == "" || got == "application/json" {
			t.Fatalf("expected multipart content type, got %q", got)
		}
		if err := r.ParseMultipartForm(1024); err != nil {
			t.Fatal(err)
		}
		if _, _, err := r.FormFile("file"); err != nil {
			t.Fatal(err)
		}
		sawMultipart = true
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"url": "https://file.runapi.ai/temp/image.png"})
	}))
	defer server.Close()

	client, err := NewHTTPClient(ClientOptions{APIKey: "test-key", BaseURL: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	body := &MultipartBody{
		Fields: map[string]string{"file_name": "image.png"},
		Files: map[string]MultipartFile{
			"file": {Path: tmp.Name(), FileName: "image.png", ContentType: "image/png"},
		},
	}
	if _, err = client.Request(context.Background(), "POST", "/api/v1/files", &HTTPRequestOptions{Body: body}); err != nil {
		t.Fatal(err)
	}
	if !sawMultipart {
		t.Fatal("server did not receive multipart request")
	}
}

func TestEscapeQuotesEscapesBackslashesAndQuotes(t *testing.T) {
	got := escapeQuotes(`dir\image"name.png`)
	want := `dir\\image\"name.png`
	if got != want {
		t.Fatalf("escapeQuotes() = %q, want %q", got, want)
	}
}
