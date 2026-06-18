package files

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/runapi-ai/core-sdk/go/core"
)

type stubHTTPClient struct {
	method string
	path   string
	body   any
}

func (s *stubHTTPClient) Request(_ context.Context, method, path string, opts *core.HTTPRequestOptions) (json.RawMessage, error) {
	s.method = method
	s.path = path
	if opts != nil {
		s.body = opts.Body
	}
	return json.RawMessage(`{"file_name":"image.png","url":"https://file.runapi.ai/temp/image.png","size_bytes":204800,"mime_type":"image/png","created_at":"2026-06-08T10:30:00Z","expires_at":"2026-06-08T11:30:00Z"}`), nil
}

func TestCreateFromURLSendsJSONSource(t *testing.T) {
	stub := &stubHTTPClient{}
	client := NewClientWithHTTP(stub)

	resp, err := client.Create(context.Background(), CreateParams{
		Source: Source{
			Type: "url",
			URL:  "https://example.com/image.png",
		},
		FileName: "image.png",
	})
	if err != nil {
		t.Fatal(err)
	}
	if stub.method != "POST" || stub.path != "/api/v1/files" {
		t.Fatalf("unexpected request: %s %s", stub.method, stub.path)
	}
	body, ok := stub.body.(map[string]any)
	if !ok {
		t.Fatalf("expected compact JSON map, got %T", stub.body)
	}
	source, ok := body["source"].(map[string]any)
	if !ok {
		t.Fatalf("expected source map, got %#v", body["source"])
	}
	if source["type"] != "url" || source["url"] != "https://example.com/image.png" {
		t.Fatalf("unexpected source: %#v", source)
	}
	if resp.URL != "https://file.runapi.ai/temp/image.png" || resp.ExpiresAt == "" {
		t.Fatalf("unexpected response: %#v", resp)
	}
}

func TestCreateFromFileSendsMultipartBody(t *testing.T) {
	stub := &stubHTTPClient{}
	client := NewClientWithHTTP(stub)

	_, err := client.Create(context.Background(), CreateParams{
		File:     "testdata/image.png",
		FileName: "image.png",
	})
	if err != nil {
		t.Fatal(err)
	}
	body, ok := stub.body.(core.MultipartBody)
	if !ok {
		t.Fatalf("expected MultipartBody, got %T", stub.body)
	}
	if body.Fields["file_name"] != "image.png" {
		t.Fatalf("unexpected fields: %#v", body.Fields)
	}
	file := body.Files["file"]
	if file.Path != "testdata/image.png" || file.FileName != "image.png" || file.ContentType != "" {
		t.Fatalf("unexpected file part: %#v", file)
	}
}

func TestCreateRejectsMissingSourceBeforeRequest(t *testing.T) {
	stub := &stubHTTPClient{}
	client := NewClientWithHTTP(stub)

	_, err := client.Create(context.Background(), CreateParams{})
	if err == nil {
		t.Fatal("expected validation error")
	}
	if stub.method != "" {
		t.Fatalf("expected no request, got %s %s", stub.method, stub.path)
	}
}

func TestCreateRejectsMultipleSourcesBeforeRequest(t *testing.T) {
	stub := &stubHTTPClient{}
	client := NewClientWithHTTP(stub)

	_, err := client.Create(context.Background(), CreateParams{
		File: "testdata/image.png",
		Source: Source{
			Type: "url",
			URL:  "https://example.com/image.png",
		},
	})
	if err == nil {
		t.Fatal("expected validation error")
	}
	if stub.method != "" {
		t.Fatalf("expected no request, got %s %s", stub.method, stub.path)
	}
}
