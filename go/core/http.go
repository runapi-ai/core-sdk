package core

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

// HTTPRequestOptions holds options for a single HTTP request.
type HTTPRequestOptions struct {
	Body    any
	Query   map[string]string
	Headers map[string]string
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
		if apiErr, ok := errors.AsType[*Error](err); ok && apiErr.Code == ErrRateLimit && apiErr.RetryAfter > 0 {
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
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return nil, nil, NewError(ErrValidation, "request body must be valid JSON", http.StatusUnprocessableEntity, "", nil, err)
		}
		requestBody = bytes.NewReader(data)
	}

	req, err := http.NewRequestWithContext(ctx, method, fullURL, requestBody)
	if err != nil {
		return nil, nil, NewError(ErrNetwork, "failed to create request", 0, "", nil, err)
	}
	req.Header.Set("Authorization", "Bearer "+c.apiKey)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", c.userAgent)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
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
