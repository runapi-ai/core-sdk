// Package option provides functional options for configuring RunAPI clients and requests.
package option

import (
	"net/http"
	"time"

	"github.com/runapi-ai/core-sdk/go/core"
)

// ClientOption configures a client at construction time.
type ClientOption interface {
	applyClient(*core.ClientOptions)
}

// RequestOption configures a single API call, overriding client-level defaults.
type RequestOption = core.CallOption

type apiKeyOption string

func (o apiKeyOption) applyClient(cfg *core.ClientOptions) { cfg.APIKey = string(o) }

// WithAPIKey sets the API key for authentication. Required.
func WithAPIKey(value string) ClientOption { return apiKeyOption(value) }

type baseURLOption string

func (o baseURLOption) applyClient(cfg *core.ClientOptions) { cfg.BaseURL = string(o) }

// WithBaseURL overrides the default API base URL (https://runapi.ai).
func WithBaseURL(value string) ClientOption { return baseURLOption(value) }

type httpClientOption struct{ client *http.Client }

func (o httpClientOption) applyClient(cfg *core.ClientOptions) { cfg.HTTPClient = o.client }

// WithHTTPClient provides a custom *http.Client for the SDK to use.
func WithHTTPClient(client *http.Client) ClientOption { return httpClientOption{client: client} }

type userAgentOption string

func (o userAgentOption) applyClient(cfg *core.ClientOptions) { cfg.UserAgent = string(o) }

// WithUserAgent overrides the default User-Agent header.
func WithUserAgent(value string) ClientOption { return userAgentOption(value) }

type timeoutOption time.Duration

func (o timeoutOption) applyClient(cfg *core.ClientOptions) { cfg.Timeout = time.Duration(o) }
func (o timeoutOption) ApplyCall(cfg *core.CallConfig)      { cfg.Request.Timeout = time.Duration(o) }

// WithTimeout sets the request timeout. Applies at both client and per-request level.
func WithTimeout(d time.Duration) timeoutOption { return timeoutOption(d) }

type maxRetriesOption int

func (o maxRetriesOption) applyClient(cfg *core.ClientOptions) { cfg.MaxRetries = int(o) }
func (o maxRetriesOption) ApplyCall(cfg *core.CallConfig) {
	value := int(o)
	cfg.Request.MaxRetries = &value
}

// WithMaxRetries sets the maximum retry attempts. Applies at both client and per-request level.
func WithMaxRetries(n int) maxRetriesOption { return maxRetriesOption(n) }

type retryBaseDelayOption time.Duration

func (o retryBaseDelayOption) applyClient(cfg *core.ClientOptions) {
	cfg.RetryBaseDelay = time.Duration(o)
}

// WithRetryBaseDelay sets the base delay between retries. Defaults to 500ms.
func WithRetryBaseDelay(d time.Duration) ClientOption { return retryBaseDelayOption(d) }

type retryMaxDelayOption time.Duration

func (o retryMaxDelayOption) applyClient(cfg *core.ClientOptions) {
	cfg.RetryMaxDelay = time.Duration(o)
}

// WithRetryMaxDelay sets the maximum delay between retries. Defaults to 5s.
func WithRetryMaxDelay(d time.Duration) ClientOption { return retryMaxDelayOption(d) }

type headerOption struct{ key, value string }

func (o headerOption) applyClient(cfg *core.ClientOptions) {
	if cfg.Headers == nil {
		cfg.Headers = map[string]string{}
	}
	cfg.Headers[o.key] = o.value
}
func (o headerOption) ApplyCall(cfg *core.CallConfig) {
	if cfg.Request.Headers == nil {
		cfg.Request.Headers = map[string]string{}
	}
	cfg.Request.Headers[o.key] = o.value
}

// WithHeader adds an extra HTTP header. Applies at both client and per-request level.
func WithHeader(key, value string) headerOption { return headerOption{key: key, value: value} }

type headersOption map[string]string

func (o headersOption) ApplyCall(cfg *core.CallConfig) {
	if cfg.Request.Headers == nil {
		cfg.Request.Headers = map[string]string{}
	}
	for key, value := range o {
		cfg.Request.Headers[key] = value
	}
}

// WithHeaders adds multiple extra HTTP headers to a single request.
func WithHeaders(headers map[string]string) RequestOption { return headersOption(headers) }

type pollIntervalOption time.Duration

func (o pollIntervalOption) ApplyCall(cfg *core.CallConfig) {
	cfg.Polling.PollInterval = time.Duration(o)
}

// WithPollInterval sets the delay between poll requests for async operations. Defaults to 2s.
func WithPollInterval(d time.Duration) RequestOption { return pollIntervalOption(d) }

type maxWaitOption time.Duration

func (o maxWaitOption) ApplyCall(cfg *core.CallConfig) { cfg.Polling.MaxWait = time.Duration(o) }

// WithMaxWait sets the maximum total wait time for async polling. Defaults to 15 minutes.
func WithMaxWait(d time.Duration) RequestOption { return maxWaitOption(d) }

// ResolveClientOptions applies client options to a set of production defaults.
func ResolveClientOptions(options ...ClientOption) (core.ClientOptions, error) {
	cfg := core.DefaultClientOptions()
	for _, option := range options {
		if option != nil {
			option.applyClient(&cfg)
		}
	}
	return cfg, nil
}

// ResolveRequestOptions applies request options and returns separate request and polling configs.
func ResolveRequestOptions(options ...RequestOption) (core.RequestOptions, core.PollingOptions) {
	cfg := core.ResolveCallOptions(options...)
	return cfg.Request, cfg.Polling
}
