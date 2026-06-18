package core

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
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
			Fields: map[string]string{"file_name": "image.png"},
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
