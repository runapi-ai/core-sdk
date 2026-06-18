package core

// MultipartFile describes a file part in a multipart/form-data request.
type MultipartFile struct {
	// Path is the local filesystem path to the file. Required.
	Path string
	// FileName overrides the filename sent in the Content-Disposition header.
	// When empty, the base name of Path is used.
	FileName string
	// ContentType sets the MIME type of the file part. When empty, the
	// multipart writer's default (application/octet-stream) is used.
	ContentType string
}

// MultipartBody describes fields and file parts for a multipart/form-data request.
type MultipartBody struct {
	// Fields are plain text form fields keyed by field name.
	Fields map[string]string
	// Files are file attachments keyed by the form field name.
	Files map[string]MultipartFile
}
