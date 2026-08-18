// Package base provides the Universal Resources available on every RunAPI
// client. Provider clients embed Base so callers reach Files, Uploads, account,
// and Pricing operations (client.Files, client.Uploads, client.Account, client.Pricing)
// regardless of which model package they imported.
package base

import (
	"github.com/runapi-ai/core-sdk/go/account"
	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/files"
	"github.com/runapi-ai/core-sdk/go/pricing"
	"github.com/runapi-ai/core-sdk/go/uploads"
)

// Base holds the Universal Resources shared by every client.
type Base struct {
	// Files provides persistent File lifecycle and temporary URL upload operations.
	Files *files.Client
	// Account provides account info and balance operations.
	Account *account.Client
	// Pricing provides live Price Schedule and Quote operations.
	Pricing *pricing.Client
	// Uploads provides multipart Upload lifecycle operations.
	Uploads *uploads.Client
}

// New builds the Universal Resources from a shared HTTP transport.
func New(httpClient core.HTTPClient) Base {
	return Base{
		Files:   files.NewClientWithHTTP(httpClient),
		Account: account.NewClientWithHTTP(httpClient),
		Pricing: pricing.NewClientWithHTTP(httpClient),
		Uploads: uploads.NewClientWithHTTP(httpClient),
	}
}
