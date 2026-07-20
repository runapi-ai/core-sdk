package core

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"mime/multipart"
	"net"
	"net/http"
	"net/textproto"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// HTTPRequestOptions holds options for a single HTTP request.
type HTTPRequestOptions struct {
	// Body is the request payload, encoded as JSON or multipart depending on type.
	Body any
	// Query contains URL query parameters appended to the request path.
	Query map[string]string
	// Headers are extra HTTP headers merged with client-level defaults.
	Headers map[string]string
	// Request carries per-call overrides for timeout and retry behavior.
	Request RequestOptions
}

// HTTPClient is the interface for sending HTTP requests.
// Implement this to provide a custom HTTP transport.
type HTTPClient interface {
	Request(ctx context.Context, method, path string, opts *HTTPRequestOptions) (json.RawMessage, error)
}

type defaultHTTPClient struct {
	apiKey         string
	baseURL        string
	timeout        time.Duration
	maxRetries     int
	retryBaseDelay time.Duration
	retryMaxDelay  time.Duration
	httpClient     *http.Client
	userAgent      string
	headers        map[string]string
}

// NewHTTPClient creates the default HTTP client from the given options.
// Returns an authentication error if no API key is provided.
func NewHTTPClient(options ClientOptions) (HTTPClient, error) {
	resolved := DefaultClientOptions()
	if options.APIKey != "" {
		resolved.APIKey = options.APIKey
	}
	if resolved.APIKey == "" {
		resolved.APIKey = strings.TrimSpace(os.Getenv("RUNAPI_API_KEY"))
	}
	if options.BaseURL != "" {
		resolved.BaseURL = options.BaseURL
	}
	if resolved.BaseURL == "" {
		resolved.BaseURL = strings.TrimSpace(os.Getenv("RUNAPI_BASE_URL"))
	}
	if options.Timeout != 0 {
		resolved.Timeout = options.Timeout
	}
	if options.MaxRetries != 0 {
		resolved.MaxRetries = options.MaxRetries
	}
	if options.RetryBaseDelay != 0 {
		resolved.RetryBaseDelay = options.RetryBaseDelay
	}
	if options.RetryMaxDelay != 0 {
		resolved.RetryMaxDelay = options.RetryMaxDelay
	}
	resolved.HTTPClient = options.HTTPClient
	resolved.UserAgent = options.UserAgent

	if strings.TrimSpace(resolved.APIKey) == "" {
		return nil, NewError(ErrAuthentication, "API key is required", http.StatusUnauthorized, "", nil, nil)
	}
	if resolved.BaseURL == "" {
		resolved.BaseURL = DefaultBaseURL
	}
	if resolved.UserAgent == "" {
		resolved.UserAgent = SDKUserAgent("dev")
	}
	client := resolved.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: resolved.Timeout}
	}
	return &defaultHTTPClient{
		apiKey:         resolved.APIKey,
		baseURL:        strings.TrimRight(resolved.BaseURL, "/"),
		timeout:        resolved.Timeout,
		maxRetries:     resolved.MaxRetries,
		retryBaseDelay: resolved.RetryBaseDelay,
		retryMaxDelay:  resolved.RetryMaxDelay,
		httpClient:     client,
		userAgent:      resolved.UserAgent,
		headers:        resolved.Headers,
	}, nil
}

func (c *defaultHTTPClient) Request(ctx context.Context, method, path string, opts *HTTPRequestOptions) (json.RawMessage, error) {
	requestOptions := RequestOptions{}
	query := map[string]string(nil)
	headers := map[string]string(nil)
	var body any
	if opts != nil {
		requestOptions = opts.Request
		query = opts.Query
		headers = opts.Headers
		body = opts.Body
	}

	requestTimeout := c.timeout
	if requestOptions.Timeout > 0 {
		requestTimeout = requestOptions.Timeout
	}
	ctx, cancel := context.WithTimeout(ctx, requestTimeout)
	defer cancel()

	maxRetries := c.maxRetries
	if requestOptions.MaxRetries != nil {
		maxRetries = *requestOptions.MaxRetries
	}

	for attempt := 0; ; attempt++ {
		payload, _, err := c.do(ctx, method, path, query, headers, body)
		if err == nil {
			return payload, nil
		}

		if !c.shouldRetry(method, attempt, maxRetries, err) {
			return nil, err
		}

		wait := RetryDelay(attempt+1, c.retryBaseDelay, c.retryMaxDelay)
		if apiErr, ok := errors.AsType[*Error](err); ok && IsRateLimit(apiErr) && apiErr.RetryAfter > 0 {
			wait = apiErr.RetryAfter
		}
		select {
		case <-ctx.Done():
			return nil, NewError(ErrTimeout, "Request timed out", http.StatusRequestTimeout, "", nil, ctx.Err())
		case <-time.After(wait):
		}
	}
}

func (c *defaultHTTPClient) do(ctx context.Context, method, path string, query, extraHeaders map[string]string, body any) (json.RawMessage, *http.Response, error) {
	fullURL, err := buildURL(c.baseURL, path, query)
	if err != nil {
		return nil, nil, NewError(ErrValidation, err.Error(), http.StatusUnprocessableEntity, "", nil, err)
	}
	var requestBody io.Reader
	contentType := ""
	if body != nil {
		if multipartBody, ok := asMultipartBody(body); ok {
			body, multipartContentType, err := newMultipartRequestBody(multipartBody)
			if err != nil {
				return nil, nil, err
			}
			requestBody = body
			contentType = multipartContentType
		} else {
			data, err := json.Marshal(body)
			if err != nil {
				return nil, nil, NewError(ErrValidation, "request body must be valid JSON", http.StatusUnprocessableEntity, "", nil, err)
			}
			requestBody = bytes.NewReader(data)
			contentType = "application/json"
		}
	}

	req, err := http.NewRequestWithContext(ctx, method, fullURL, requestBody)
	if err != nil {
		if closer, ok := requestBody.(io.Closer); ok {
			_ = closer.Close()
		}
		return nil, nil, NewError(ErrNetwork, "failed to create request", 0, "", nil, err)
	}
	if req.Body != nil {
		defer req.Body.Close()
	}
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", c.userAgent)
	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}
	for key, value := range c.headers {
		req.Header.Set(key, value)
	}
	for key, value := range extraHeaders {
		req.Header.Set(key, value)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		if ctx.Err() != nil {
			return nil, nil, NewError(ErrTimeout, "Request timed out", http.StatusRequestTimeout, "", nil, ctx.Err())
		}
		if netErr, ok := errors.AsType[net.Error](err); ok && netErr.Timeout() {
			return nil, nil, NewError(ErrTimeout, "Request timed out", http.StatusRequestTimeout, "", nil, err)
		}
		return nil, nil, NewError(ErrNetwork, "Network error", 0, "", nil, err)
	}
	defer resp.Body.Close()

	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, resp, NewError(ErrNetwork, "failed to read response", 0, "", nil, err)
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, resp, ErrorFromResponse(resp, responseBody)
	}

	return json.RawMessage(responseBody), resp, nil
}

func newMultipartRequestBody(body MultipartBody) (io.Reader, string, error) {
	if err := validateMultipartBody(body); err != nil {
		return nil, "", err
	}

	reader, writer := io.Pipe()
	multipartWriter := multipart.NewWriter(writer)
	contentType := multipartWriter.FormDataContentType()

	go func() {
		err := writeMultipartBody(multipartWriter, body)
		if closeErr := multipartWriter.Close(); err == nil {
			err = closeErr
		}
		_ = writer.CloseWithError(err)
	}()

	return reader, contentType, nil
}

func validateMultipartBody(body MultipartBody) error {
	for _, file := range body.Files {
		if file.Path == "" {
			return NewError(ErrValidation, "multipart file path is required", http.StatusUnprocessableEntity, "", nil, nil)
		}
	}
	return nil
}

func asMultipartBody(body any) (MultipartBody, bool) {
	switch value := body.(type) {
	case MultipartBody:
		return value, true
	case *MultipartBody:
		if value == nil {
			return MultipartBody{}, false
		}
		return *value, true
	default:
		return MultipartBody{}, false
	}
}

func writeMultipartBody(writer *multipart.Writer, body MultipartBody) error {
	for key, value := range body.Fields {
		if err := writer.WriteField(key, value); err != nil {
			return NewError(ErrValidation, "failed to write multipart field", http.StatusUnprocessableEntity, "", nil, err)
		}
	}
	for key, file := range body.Files {
		name := file.FileName
		if name == "" {
			name = filepath.Base(file.Path)
		}
		partHeader := make(textproto.MIMEHeader)
		partHeader.Set("Content-Disposition", fmt.Sprintf(`form-data; name="%s"; filename="%s"`, escapeQuotes(key), escapeQuotes(name)))
		if file.ContentType != "" {
			partHeader.Set("Content-Type", file.ContentType)
		}
		part, err := writer.CreatePart(partHeader)
		if err != nil {
			return NewError(ErrValidation, "failed to create multipart file part", http.StatusUnprocessableEntity, "", nil, err)
		}
		handle, err := os.Open(file.Path)
		if err != nil {
			return NewError(ErrValidation, "failed to open multipart file", http.StatusUnprocessableEntity, "", nil, err)
		}
		_, copyErr := io.Copy(part, handle)
		closeErr := handle.Close()
		if copyErr != nil {
			return NewError(ErrValidation, "failed to read multipart file", http.StatusUnprocessableEntity, "", nil, copyErr)
		}
		if closeErr != nil {
			return NewError(ErrValidation, "failed to close multipart file", http.StatusUnprocessableEntity, "", nil, closeErr)
		}
	}
	return nil
}

func escapeQuotes(value string) string {
	value = strings.ReplaceAll(value, `\`, `\\`)
	return strings.ReplaceAll(value, `"`, `\"`)
}

func (c *defaultHTTPClient) shouldRetry(method string, attempt, maxRetries int, err error) bool {
	if attempt >= maxRetries || !IsIdempotentMethod(method) {
		return false
	}
	if apiErr, ok := errors.AsType[*Error](err); ok {
		return IsRetryableStatus(apiErr.Status)
	}
	return IsNetwork(err) || IsTimeout(err)
}

func buildURL(baseURL, path string, query map[string]string) (string, error) {
	parsed, err := url.Parse(strings.TrimRight(baseURL, "/") + "/" + strings.TrimLeft(path, "/"))
	if err != nil {
		return "", err
	}
	params := parsed.Query()
	for key, value := range query {
		params.Set(key, value)
	}
	parsed.RawQuery = params.Encode()
	return parsed.String(), nil
}

// DecodeResponse unmarshals a JSON payload into T.
func DecodeResponse[T any](payload json.RawMessage) (*T, error) {
	if len(bytes.TrimSpace(payload)) == 0 {
		var empty T
		return &empty, nil
	}
	var response T
	if err := json.Unmarshal(payload, &response); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &response, nil
}
