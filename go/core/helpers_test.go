package core

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestCreateHybridRetriesPostWithSameIdempotencyKey(t *testing.T) {
	requests := 0
	var key string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requests++
		if requests == 1 {
			key = r.Header.Get("Idempotency-Key")
			if key == "" {
				t.Fatal("expected generated idempotency key")
			}
			w.WriteHeader(http.StatusBadGateway)
			_, _ = w.Write([]byte(`{"error":{"message":"temporarily unavailable"}}`))
			return
		}
		if r.Header.Get("Idempotency-Key") != key {
			t.Fatalf("expected retry to preserve idempotency key %q", key)
		}
		_, _ = w.Write([]byte(`{"value":"ok"}`))
	}))
	defer server.Close()

	client, err := NewHTTPClient(ClientOptions{
		APIKey:         "test-key",
		BaseURL:        server.URL,
		Timeout:        time.Second,
		MaxRetries:     1,
		RetryBaseDelay: time.Nanosecond,
		RetryMaxDelay:  time.Nanosecond,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := CreateHybrid[map[string]string](context.Background(), client, "/hybrid", map[string]string{"input": "test"}, RequestOptions{})
	if err != nil {
		t.Fatal(err)
	}
	if requests != 2 || result.Terminal == nil || (*result.Terminal)["value"] != "ok" {
		t.Fatalf("unexpected result after %d requests: %#v", requests, result)
	}
}

func TestCreateHybridPreservesCaseInsensitiveCallerIdempotencyKey(t *testing.T) {
	const callerKey = "caller-key"
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Idempotency-Key"); got != callerKey {
			t.Fatalf("expected caller idempotency key %q, got %q", callerKey, got)
		}
		w.Header().Set("Location", "/api/v1/tasks/task_123")
		w.WriteHeader(http.StatusAccepted)
		_, _ = w.Write([]byte(`{"id":"task_123","status":"processing"}`))
	}))
	defer server.Close()

	client, err := NewHTTPClient(ClientOptions{APIKey: "test-key", BaseURL: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	result, err := CreateHybrid[map[string]string](context.Background(), client, "/hybrid", nil, RequestOptions{
		Headers: map[string]string{"idempotency-key": callerKey},
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Acceptance == nil || result.Acceptance.IdempotencyKey != callerKey {
		t.Fatalf("expected acceptance to retain caller key: %#v", result.Acceptance)
	}
}

func TestCreateHybridRejectsConflictingIdempotencyKeyHeaders(t *testing.T) {
	client := &stubResponseHTTPClient{}
	_, err := CreateHybrid[map[string]string](context.Background(), client, "/hybrid", nil, RequestOptions{
		Headers: map[string]string{"Idempotency-Key": "first", "idempotency-key": "second"},
	})
	if err == nil || !IsValidation(err) {
		t.Fatalf("expected validation error, got %v", err)
	}
}

func TestCreateHybridSupportsDirectResponseFromLegacyHTTPClient(t *testing.T) {
	client := &legacyHTTPClient{response: json.RawMessage(`{"id":"resource_1","value":"ok"}`)}
	result, err := CreateHybrid[map[string]string](context.Background(), client, "/hybrid", nil, RequestOptions{})
	if err != nil {
		t.Fatal(err)
	}
	if result.Terminal == nil || (*result.Terminal)["value"] != "ok" {
		t.Fatalf("unexpected terminal result: %#v", result)
	}
	if client.idempotencyKey == "" {
		t.Fatal("expected generated idempotency key")
	}
}

func TestCreateHybridRejectsAcceptedResponseFromLegacyHTTPClient(t *testing.T) {
	client := &legacyHTTPClient{response: json.RawMessage(`{"id":"task_123","status":"processing"}`)}
	if _, err := CreateHybrid[map[string]string](context.Background(), client, "/hybrid", nil, RequestOptions{}); err == nil {
		t.Fatal("expected response-aware transport error")
	}
}

func TestDecodeStoredHybridRawResponse(t *testing.T) {
	tests := []struct {
		name        string
		body        json.RawMessage
		contentType string
		want        string
	}{
		{name: "text with charset", body: json.RawMessage(`"hello\n"`), contentType: "text/plain; charset=utf-8", want: "hello\n"},
		{name: "json", body: json.RawMessage(`{"text":"hello"}`), contentType: "application/json", want: `{"text":"hello"}`},
		{name: "structured json", body: json.RawMessage(`{"text":"hello"}`), contentType: "application/vnd.runapi+json", want: `{"text":"hello"}`},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			result, err := decodeStoredHybridResponse[json.RawMessage](test.body, test.contentType)
			if err != nil {
				t.Fatal(err)
			}
			if string(*result) != test.want {
				t.Fatalf("expected %q, got %q", test.want, *result)
			}
		})
	}
}

func TestDecodeStoredHybridRawResponseRejectsNonStringTextBody(t *testing.T) {
	if _, err := decodeStoredHybridResponse[json.RawMessage](json.RawMessage(`{"text":"hello"}`), "text/plain"); err == nil {
		t.Fatal("expected non-string stored text body to fail")
	}
}

type stubResponseHTTPClient struct{}

func (s *stubResponseHTTPClient) Request(context.Context, string, string, *HTTPRequestOptions) (json.RawMessage, error) {
	return nil, nil
}

func (s *stubResponseHTTPClient) RequestWithResponse(context.Context, string, string, *HTTPRequestOptions) (*HTTPResponse, error) {
	return nil, nil
}

type legacyHTTPClient struct {
	response       json.RawMessage
	idempotencyKey string
}

func (c *legacyHTTPClient) Request(_ context.Context, _, _ string, opts *HTTPRequestOptions) (json.RawMessage, error) {
	c.idempotencyKey = opts.Headers["Idempotency-Key"]
	return c.response, nil
}
