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
	"os"
	"path/filepath"

	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/option"
)

const createPath = "/api/v1/files"
const preparePath = createPath + "/prepare"
const confirmPath = createPath + "/confirm"

// Client uploads files to RunAPI's temporary storage. The returned URLs can be
// passed to generation endpoints that accept media inputs (images, audio, video).
type Client struct {
	http core.HTTPClient
	// uploader sends the raw bytes to the pre-authorized upload URL, which lives
	// outside the API host and takes no auth. Kept separate from the core client.
	uploader *http.Client
}

// NewClient creates a file upload client with the given options.
func NewClient(opts ...option.ClientOption) (*Client, error) {
	resolved, err := option.ResolveClientOptions(opts...)
	if err != nil {
		return nil, err
	}
	httpClient, err := core.NewHTTPClient(resolved)
	if err != nil {
		return nil, err
	}
	client := NewClientWithHTTP(httpClient)
	if resolved.Timeout > 0 {
		client.uploader.Timeout = resolved.Timeout
	}
	return client, nil
}

// NewClientWithHTTP creates a file upload client with a pre-configured HTTP transport.
func NewClientWithHTTP(httpClient core.HTTPClient) *Client {
	// Bound the direct-upload PUT with the default request timeout so it cannot
	// hang forever when the caller's context carries no deadline. NewClient
	// overrides this with the configured timeout.
	return &Client{http: httpClient, uploader: &http.Client{Timeout: core.DefaultTimeout}}
}

// Create uploads a file and returns its temporary URL for use in generation
// requests. The file can come from a local path (uploaded straight to storage),
// a remote URL, or an inline base64 payload -- see [CreateParams] for the mutual
// exclusivity constraint.
func (c *Client) Create(ctx context.Context, params CreateParams, opts ...option.RequestOption) (*UploadResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	if err := validateCreateParams(params); err != nil {
		return nil, err
	}

	if params.File != "" {
		return c.uploadDirect(ctx, params, requestOptions)
	}

	payload, err := c.http.Request(ctx, "POST", createPath, &core.HTTPRequestOptions{
		Body:    core.CompactParams(params),
		Headers: requestOptions.Headers,
		Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[UploadResponse](payload)
}

func validateCreateParams(params CreateParams) error {
	sourceCount := 0
	if params.File != "" {
		sourceCount++
	}
	if params.Source.Type != "" {
		sourceCount++
	}
	if sourceCount == 1 {
		return nil
	}
	return core.NewError(core.ErrValidation, "Exactly one source is required: file or source", http.StatusUnprocessableEntity, "", nil, nil)
}

type prepareResponse struct {
	SignedID  string            `json:"signed_id"`
	UploadURL string            `json:"upload_url"`
	Headers   map[string]string `json:"headers"`
}

// uploadDirect keeps the single Create call for the caller while sending the
// bytes straight to storage: ask for a pre-authorized target, PUT the bytes
// there (never through the API), then confirm.
func (c *Client) uploadDirect(ctx context.Context, params CreateParams, requestOptions core.RequestOptions) (*UploadResponse, error) {
	data, err := os.ReadFile(params.File)
	if err != nil {
		return nil, core.NewError(core.ErrValidation, "failed to read file: "+err.Error(), http.StatusUnprocessableEntity, "", nil, err)
	}

	filename := params.FileName
	if filename == "" {
		filename = filepath.Base(params.File)
	}
	sum := md5.Sum(data)

	prepared, err := c.http.Request(ctx, "POST", preparePath, &core.HTTPRequestOptions{
		Body: map[string]any{
			"filename":  filename,
			"byte_size": len(data),
			"checksum":  base64.StdEncoding.EncodeToString(sum[:]),
		},
		Headers: requestOptions.Headers,
		Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}

	var prep prepareResponse
	if err := json.Unmarshal(prepared, &prep); err != nil {
		return nil, core.NewError(core.ErrNetwork, "failed to decode upload target", 0, "", nil, err)
	}

	if err := c.put(ctx, prep.UploadURL, prep.Headers, data); err != nil {
		return nil, err
	}

	payload, err := c.http.Request(ctx, "POST", confirmPath, &core.HTTPRequestOptions{
		Body:    map[string]any{"signed_id": prep.SignedID},
		Headers: requestOptions.Headers,
		Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[UploadResponse](payload)
}

func (c *Client) put(ctx context.Context, url string, headers map[string]string, data []byte) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodPut, url, bytes.NewReader(data))
	if err != nil {
		return core.NewError(core.ErrNetwork, "failed to create upload request", 0, "", nil, err)
	}
	for key, value := range headers {
		req.Header.Set(key, value)
	}

	resp, err := c.uploader.Do(req)
	if err != nil {
		return core.NewError(core.ErrNetwork, "Direct upload network error", 0, "", nil, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		body, _ := io.ReadAll(resp.Body)
		return core.NewError(core.ErrNetwork, fmt.Sprintf("Direct upload failed with status %d: %s", resp.StatusCode, string(body)), resp.StatusCode, "", nil, nil)
	}
	return nil
}
