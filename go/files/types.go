// Package files manages persistent File resources and temporary URL uploads.
package files

// Source specifies a remote URL or inline base64 payload to upload.
// Set Type to "url" and populate URL, or set Type to "base64" and populate Data.
type Source struct {
	Type string `json:"type" help:"required; url or base64"`
	URL  string `json:"url,omitempty" help:"required when type is url"`
	Data string `json:"data,omitempty" help:"required when type is base64"`
}

// CreateParams configures a file upload. Exactly one source must be provided:
// either File (a local path, sent as multipart form data) or Source (a remote
// URL or base64 payload, sent as JSON). Supplying both or neither is an error.
type CreateParams struct {
	File     string `json:"-" help:"local file path for multipart upload"`
	Source   Source `json:"source,omitempty" help:"JSON source object for URL or base64 upload"`
	FileName string `json:"file_name,omitempty" help:"optional file name"`
}

// UploadResponse contains the metadata for a successfully uploaded file.
// Use URL in subsequent generation requests to reference this file.
// The file is available until ExpiresAt, after which the URL becomes invalid.
type UploadResponse struct {
	FileName  string `json:"file_name"`
	URL       string `json:"url"`
	SizeBytes int64  `json:"size_bytes"`
	MIMEType  string `json:"mime_type"`
	CreatedAt string `json:"created_at"`
	ExpiresAt string `json:"expires_at"`
}

// File is a File resource stored for use by RunAPI requests.
type File struct {
	ID        string `json:"id"`
	Object    string `json:"object"`
	Bytes     int64  `json:"bytes"`
	CreatedAt int64  `json:"created_at"`
	ExpiresAt *int64 `json:"expires_at,omitempty"`
	Filename  string `json:"filename"`
	Purpose   string `json:"purpose"`
}

// ListResponse is a cursor-paginated collection of Files.
type ListResponse struct {
	Object  string `json:"object"`
	Data    []File `json:"data"`
	FirstID string `json:"first_id,omitempty"`
	LastID  string `json:"last_id,omitempty"`
	HasMore bool   `json:"has_more"`
}

// DeletedFile confirms that a File was deleted.
type DeletedFile struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Deleted bool   `json:"deleted"`
}

// ProtocolCreateParams configures an OpenAI-compatible File upload.
type ProtocolCreateParams struct {
	File     string `json:"-" help:"required; local file path"`
	FileName string `json:"-" help:"optional file name"`
	Purpose  string `json:"-" help:"optional; defaults to user_data"`
}

// ListParams filters and paginates Files.
type ListParams struct {
	After   string `json:"after,omitempty" help:"cursor File id"`
	Limit   int    `json:"limit,omitempty" help:"number of Files to return"`
	Order   string `json:"order,omitempty" help:"asc or desc"`
	Purpose string `json:"purpose,omitempty" help:"user_data"`
}
