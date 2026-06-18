// Package files uploads local or remote media to RunAPI's temporary storage
// so they can be referenced by URL in generation requests (e.g. image-to-video,
// audio-to-audio). Uploaded files expire automatically after a short retention
// period.
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
