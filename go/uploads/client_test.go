package uploads

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/runapi-ai/core-sdk/go/core"
)

type stubHTTP struct {
	methods []string
	paths   []string
	bodies  []any
}

func (s *stubHTTP) Request(_ context.Context, method, path string, opts *core.HTTPRequestOptions) (json.RawMessage, error) {
	s.methods = append(s.methods, method)
	s.paths = append(s.paths, path)
	s.bodies = append(s.bodies, opts.Body)
	if path == "/v1/uploads/upload_123/parts" {
		return json.RawMessage(`{"id":"part_123","object":"upload.part","created_at":1,"upload_id":"upload_123"}`), nil
	}
	return json.RawMessage(`{"id":"upload_123","object":"upload","bytes":3,"created_at":1,"filename":"data.bin","purpose":"user_data","status":"pending","expires_at":2}`), nil
}

func TestLifecycleUsesCanonicalPathsAndBodies(t *testing.T) {
	path := filepath.Join(t.TempDir(), "part.bin")
	if err := os.WriteFile(path, []byte("abc"), 0o600); err != nil {
		t.Fatal(err)
	}
	stub := &stubHTTP{}
	client := NewClientWithHTTP(stub)
	ctx := context.Background()

	if _, err := client.Create(ctx, CreateParams{Bytes: 3, Filename: "data.bin", MIMEType: "application/octet-stream"}); err != nil {
		t.Fatal(err)
	}
	if _, err := client.AddPart(ctx, "upload_123", AddPartParams{File: path}); err != nil {
		t.Fatal(err)
	}
	if _, err := client.Complete(ctx, "upload_123", []string{"part_123"}); err != nil {
		t.Fatal(err)
	}
	if _, err := client.Cancel(ctx, "upload_123"); err != nil {
		t.Fatal(err)
	}

	if stub.paths[0] != "/v1/uploads" || stub.paths[1] != "/v1/uploads/upload_123/parts" ||
		stub.paths[2] != "/v1/uploads/upload_123/complete" || stub.paths[3] != "/v1/uploads/upload_123/cancel" {
		t.Fatalf("unexpected paths: %#v", stub.paths)
	}
	create := stub.bodies[0].(CreateParams)
	if create.Purpose != "user_data" {
		t.Fatalf("unexpected purpose: %q", create.Purpose)
	}
	part := stub.bodies[1].(core.MultipartBody)
	if part.Files["data"].Path != path {
		t.Fatalf("unexpected part body: %#v", part)
	}
	complete := stub.bodies[2].(map[string]any)
	if complete["part_ids"].([]string)[0] != "part_123" {
		t.Fatalf("unexpected completion body: %#v", complete)
	}
}
