package uploads

import (
	"context"
	"net/http"
	"net/url"
	"strings"

	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/option"
)

const endpoint = "/v1/uploads"

// Client manages multipart Upload resources.
type Client struct{ http core.HTTPClient }

// NewClient creates an Upload client with the given options.
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

// NewClientWithHTTP creates an Upload client with a shared transport.
func NewClientWithHTTP(httpClient core.HTTPClient) *Client { return &Client{http: httpClient} }

// Create starts an Upload.
func (c *Client) Create(ctx context.Context, params CreateParams, opts ...option.RequestOption) (*Upload, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	if params.Purpose == "" {
		params.Purpose = "user_data"
	}
	payload, err := c.http.Request(ctx, "POST", endpoint, &core.HTTPRequestOptions{
		Body: params, Headers: requestOptions.Headers, Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[Upload](payload)
}

// AddPart uploads one local file Part.
func (c *Client) AddPart(ctx context.Context, uploadID string, params AddPartParams, opts ...option.RequestOption) (*Part, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	path, err := uploadPath(uploadID)
	if err != nil {
		return nil, err
	}
	if strings.TrimSpace(params.File) == "" {
		return nil, core.NewError(core.ErrValidation, "file is required", http.StatusUnprocessableEntity, "", nil, nil)
	}
	payload, err := c.http.Request(ctx, "POST", path+"/parts", &core.HTTPRequestOptions{
		Body: core.MultipartBody{Files: map[string]core.MultipartFile{"data": {
			Path: params.File, FileName: params.FileName, ContentType: params.ContentType,
		}}},
		Headers: requestOptions.Headers, Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[Part](payload)
}

// Complete composes the specified Parts in order.
func (c *Client) Complete(ctx context.Context, uploadID string, partIDs []string, opts ...option.RequestOption) (*Upload, error) {
	return c.post(ctx, uploadID, "complete", map[string]any{"part_ids": partIDs}, opts...)
}

// Cancel cancels an Upload.
func (c *Client) Cancel(ctx context.Context, uploadID string, opts ...option.RequestOption) (*Upload, error) {
	return c.post(ctx, uploadID, "cancel", map[string]any{}, opts...)
}

func (c *Client) post(ctx context.Context, uploadID, suffix string, body any, opts ...option.RequestOption) (*Upload, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	path, err := uploadPath(uploadID)
	if err != nil {
		return nil, err
	}
	payload, err := c.http.Request(ctx, "POST", path+"/"+suffix, &core.HTTPRequestOptions{
		Body: body, Headers: requestOptions.Headers, Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[Upload](payload)
}

func uploadPath(uploadID string) (string, error) {
	if strings.TrimSpace(uploadID) == "" {
		return "", core.NewError(core.ErrValidation, "upload_id is required", http.StatusUnprocessableEntity, "", nil, nil)
	}
	return endpoint + "/" + url.PathEscape(uploadID), nil
}
