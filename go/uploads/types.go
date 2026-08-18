// Package uploads manages multipart Upload resources.
package uploads

import "github.com/runapi-ai/core-sdk/go/files"

// Upload is a multipart upload lifecycle resource.
type Upload struct {
	ID        string      `json:"id"`
	Object    string      `json:"object"`
	Bytes     int64       `json:"bytes"`
	CreatedAt int64       `json:"created_at"`
	Filename  string      `json:"filename"`
	Purpose   string      `json:"purpose"`
	Status    string      `json:"status"`
	ExpiresAt int64       `json:"expires_at"`
	File      *files.File `json:"file,omitempty"`
}

// Part identifies one uploaded Upload segment.
type Part struct {
	ID        string `json:"id"`
	Object    string `json:"object"`
	CreatedAt int64  `json:"created_at"`
	UploadID  string `json:"upload_id"`
}

// CreateParams declares the final Upload metadata.
type CreateParams struct {
	Bytes    int64  `json:"bytes" help:"required final byte size"`
	Filename string `json:"filename" help:"required final file name"`
	MIMEType string `json:"mime_type" help:"required MIME type"`
	Purpose  string `json:"purpose,omitempty" help:"optional; defaults to user_data"`
}

// AddPartParams configures one local file Part.
type AddPartParams struct {
	File        string `json:"-" help:"required local part path"`
	FileName    string `json:"-" help:"optional part file name"`
	ContentType string `json:"-" help:"optional part MIME type"`
}
