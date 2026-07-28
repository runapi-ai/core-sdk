// Package pricing provides access to live RunAPI Price Schedules and Quotes.
package pricing

import (
	"context"

	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/option"
)

const schedulesPath = "/api/v1/price_schedules"
const quotesPath = "/api/v1/price_quotes"

// Client reads the runtime-owned Pricing Resource.
type Client struct{ http core.HTTPClient }

// NewClient creates a Pricing client. An API key is optional for public Price
// Schedule and Quote requests, and is used only when a quote names a protected
// Account-owned source task.
func NewClient(opts ...option.ClientOption) (*Client, error) {
	resolved, err := option.ResolveClientOptions(opts...)
	if err != nil {
		return nil, err
	}
	httpClient, err := core.NewPublicHTTPClient(resolved)
	if err != nil {
		return nil, err
	}
	return NewClientWithHTTP(httpClient), nil
}

// NewClientWithHTTP creates a Pricing client with a shared HTTP transport.
func NewClientWithHTTP(httpClient core.HTTPClient) *Client { return &Client{http: httpClient} }

// List returns the current Price Schedule, optionally filtered by public
// service, action, and model identity.
func (c *Client) List(ctx context.Context, params ListParams, opts ...option.RequestOption) (*ListResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	payload, err := c.http.Request(ctx, "GET", schedulesPath, &core.HTTPRequestOptions{
		Query:   map[string]string{"service": params.Service, "action": params.Action, "model": params.Model},
		Headers: requestOptions.Headers,
		Request: requestOptions,
	})
	if err != nil {
		return nil, err
	}
	return core.DecodeResponse[ListResponse](payload)
}

// Quote estimates the reservation for one endpoint identity and params. Quotes
// with source_task_id may require an Account-scoped standard API key.
func (c *Client) Quote(ctx context.Context, params QuoteParams, opts ...option.RequestOption) (*QuoteResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	return core.PostJSON[QuoteResponse](ctx, c.http, quotesPath, core.CompactParams(params), requestOptions)
}
