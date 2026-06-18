package files

import (
	"context"
	"net/http"
	"path/filepath"

	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/option"
)

const createPath = "/api/v1/files"

// Client uploads files to RunAPI's temporary storage. The returned URLs can be
// passed to generation endpoints that accept media inputs (images, audio, video).
type Client struct {
	http core.HTTPClient
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
	return NewClientWithHTTP(httpClient), nil
}

// NewClientWithHTTP creates a file upload client with a pre-configured HTTP transport.
func NewClientWithHTTP(httpClient core.HTTPClient) *Client {
	return &Client{http: httpClient}
}

// Create uploads a file and returns its temporary URL for use in generation
// requests. The file can come from a local path (multipart upload), a remote
// URL, or an inline base64 payload -- see [CreateParams] for the mutual
// exclusivity constraint.
func (c *Client) Create(ctx context.Context, params CreateParams, opts ...option.RequestOption) (*UploadResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	if err := validateCreateParams(params); err != nil {
		return nil, err
	}
	body := createBody(params)
	payload, err := c.http.Request(ctx, "POST", createPath, &core.HTTPRequestOptions{
		Body:    body,
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

func createBody(params CreateParams) any {
	if params.File == "" {
		return core.CompactParams(params)
	}

	filename := params.FileName
	if filename == "" {
		filename = filepath.Base(params.File)
	}
	fields := map[string]string{}
	if params.FileName != "" {
		fields["file_name"] = params.FileName
	}
	return core.MultipartBody{
		Fields: fields,
		Files: map[string]core.MultipartFile{
			"file": {
				Path:     params.File,
				FileName: filename,
			},
		},
	}
}
