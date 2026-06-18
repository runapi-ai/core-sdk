// Package base provides the Universal Resources available on every RunAPI
// client. Provider clients embed Base so callers reach file upload and account
// operations (client.Files, client.Account) regardless of which model package
// they imported.
package base

import (
	"github.com/runapi-ai/core-sdk/go/account"
	"github.com/runapi-ai/core-sdk/go/core"
	"github.com/runapi-ai/core-sdk/go/files"
)

// Base holds the Universal Resources shared by every client.
type Base struct {
	// Files provides temporary file upload operations.
	Files *files.Client
	// Account provides account info and balance operations.
	Account *account.Client
}

// New builds the Universal Resources from a shared HTTP transport.
func New(httpClient core.HTTPClient) Base {
	return Base{
		Files:   files.NewClientWithHTTP(httpClient),
		Account: account.NewClientWithHTTP(httpClient),
	}
}
