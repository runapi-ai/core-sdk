// Package account provides access to RunAPI account info and balance endpoints.
package account

import (
	"context"

	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/option"
)

// InfoResponse holds the authenticated user's profile and the account they
// belong to. A single user may belong to multiple accounts; this returns
// whichever account the API key is scoped to.
type InfoResponse struct {
	ID      int64         `json:"id"`
	Name    string        `json:"name"`
	Email   string        `json:"email"`
	Account AccountRecord `json:"account"`
}

// AccountRecord contains the account details nested in InfoResponse.
type AccountRecord struct {
	ID   int64  `json:"id"`
	Name string `json:"name"`
}

// BalanceResponse reports the account's remaining credits and cumulative spend.
// All monetary values are in cents (1/100 of a credit unit). Use BalanceCents
// to check available credits before submitting a task.
type BalanceResponse struct {
	// BalanceCents is the remaining credit balance available for new tasks.
	BalanceCents int64 `json:"balance_cents"`
	// PaidBalanceCents is the portion of the balance from purchased credits.
	PaidBalanceCents int64 `json:"paid_balance_cents"`
	// BonusBalanceCents is the portion of the balance from promotional credits.
	BonusBalanceCents int64 `json:"bonus_balance_cents"`
	// SpentCentsToday is the credits consumed today since midnight in the
	// authenticated user's timezone.
	SpentCentsToday int64 `json:"spent_cents_today"`
	// SpentCentsTotal is the lifetime credit spend for this account.
	SpentCentsTotal int64 `json:"spent_cents_total"`
}

// Client provides read-only queries for account identity and credit balance.
// None of its methods consume credits.
type Client struct {
	http core.HTTPClient
}

// NewClient creates an account client. At minimum, an API key must be provided
// via [option.WithAPIKey] or the RUNAPI_API_KEY environment variable.
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

// NewClientWithHTTP creates an account client that reuses an existing HTTP
// transport. This is useful when sharing a single authenticated transport
// across multiple service clients.
func NewClientWithHTTP(httpClient core.HTTPClient) *Client {
	return &Client{http: httpClient}
}

// Info returns the profile of the authenticated user and the account the API
// key belongs to. Use it to verify credentials or display the current identity.
func (c *Client) Info(ctx context.Context, opts ...option.RequestOption) (*InfoResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	return core.GetJSON[InfoResponse](ctx, c.http, "/api/v1/me", requestOptions)
}

// Balance returns the account's remaining credits and spend totals. Call this
// before submitting expensive tasks to ensure sufficient credits are available;
// a task submitted with insufficient balance will fail with HTTP 402.
func (c *Client) Balance(ctx context.Context, opts ...option.RequestOption) (*BalanceResponse, error) {
	requestOptions, _ := option.ResolveRequestOptions(opts...)
	return core.GetJSON[BalanceResponse](ctx, c.http, "/api/v1/me/balance", requestOptions)
}
