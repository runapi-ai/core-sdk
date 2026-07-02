package files

import (
	"bytes"
	"context"
	"crypto/md5"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
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

// directStub returns a prepare response pointing at uploadURL, then a resource
// for confirm, recording every call so the sequence can be asserted.
type directStub struct {
	uploadURL string
	paths     []string
	bodies    []any
}

func (s *directStub) Request(_ context.Context, _ string, path string, opts *core.HTTPRequestOptions) (json.RawMessage, error) {
	s.paths = append(s.paths, path)
	if opts != nil {
		s.bodies = append(s.bodies, opts.Body)
	}
	if path == preparePath {
		return json.RawMessage(fmt.Sprintf(`{"signed_id":"signed-blob-id","upload_url":%q,"headers":{"Content-Type":"application/octet-stream"}}`, s.uploadURL)), nil
	}
	return json.RawMessage(`{"file_name":"image.png","url":"https://file.runapi.ai/temp/image.png","size_bytes":9,"mime_type":"image/png","created_at":"2026-06-08T10:30:00Z","expires_at":"2026-06-08T11:30:00Z"}`), nil
}

func TestCreateFromURLSendsJSONSource(t *testing.T) {
	stub := &stubHTTPClient{}
	client := NewClientWithHTTP(stub)

	resp, err := client.Create(context.Background(), CreateParams{
		Source: Source{
			Type: "url",
			URL:  "https://cdn.runapi.ai/public/samples/mask.png",
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
	if source["type"] != "url" || source["url"] != "https://cdn.runapi.ai/public/samples/mask.png" {
		t.Fatalf("unexpected source: %#v", source)
	}
	if resp.URL != "https://file.runapi.ai/temp/image.png" || resp.ExpiresAt == "" {
		t.Fatalf("unexpected response: %#v", resp)
	}
}

func TestCreateFromFileUploadsDirectly(t *testing.T) {
	content := []byte("png-bytes")
	path := filepath.Join(t.TempDir(), "image.png")
	if err := os.WriteFile(path, content, 0o600); err != nil {
		t.Fatal(err)
	}

	var putBody []byte
	uploadSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPut {
			t.Errorf("expected PUT, got %s", r.Method)
		}
		putBody, _ = io.ReadAll(r.Body)
		w.WriteHeader(http.StatusOK)
	}))
	defer uploadSrv.Close()

	stub := &directStub{uploadURL: uploadSrv.URL}
	client := NewClientWithHTTP(stub)

	resp, err := client.Create(context.Background(), CreateParams{File: path, FileName: "image.png"})
	if err != nil {
		t.Fatal(err)
	}

	// prepare then confirm, and no file bytes through the API
	if len(stub.paths) != 2 || stub.paths[0] != preparePath || stub.paths[1] != confirmPath {
		t.Fatalf("unexpected call sequence: %#v", stub.paths)
	}
	prep, ok := stub.bodies[0].(map[string]any)
	if !ok {
		t.Fatalf("expected prepare map, got %T", stub.bodies[0])
	}
	if prep["filename"] != "image.png" || prep["byte_size"] != len(content) {
		t.Fatalf("unexpected prepare body: %#v", prep)
	}
	sum := md5.Sum(content)
	if prep["checksum"] != base64.StdEncoding.EncodeToString(sum[:]) {
		t.Fatalf("unexpected checksum: %#v", prep["checksum"])
	}

	// bytes went straight to the pre-authorized upload URL
	if !bytes.Equal(putBody, content) {
		t.Fatalf("upload body mismatch: %q", putBody)
	}

	confirm, ok := stub.bodies[1].(map[string]any)
	if !ok || confirm["signed_id"] != "signed-blob-id" {
		t.Fatalf("unexpected confirm body: %#v", stub.bodies[1])
	}
	if resp.FileName != "image.png" {
		t.Fatalf("unexpected response: %#v", resp)
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
			URL:  "https://cdn.runapi.ai/public/samples/mask.png",
		},
	})
	if err == nil {
		t.Fatal("expected validation error")
	}
	if stub.method != "" {
		t.Fatalf("expected no request, got %s %s", stub.method, stub.path)
	}
}

func TestUploaderHasBoundedTimeout(t *testing.T) {
	// The direct-upload PUT must not hang forever when the caller's context has
	// no deadline. base.Base builds the client via NewClientWithHTTP.
	client := NewClientWithHTTP(&stubHTTPClient{})
	if client.uploader.Timeout != core.DefaultTimeout {
		t.Fatalf("expected uploader timeout %v, got %v", core.DefaultTimeout, client.uploader.Timeout)
	}
}
