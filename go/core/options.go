package core

import (
	"net/http"
	"time"
)

// ClientOptions configures the HTTP client shared across all service operations.
type ClientOptions struct {
	// APIKey for authentication. Required.
	APIKey string
	// BaseURL for API requests. Defaults to "https://runapi.ai".
	BaseURL string
	// Timeout for each HTTP request. Defaults to 15 minutes.
	Timeout time.Duration
	// MaxRetries is the maximum number of retry attempts. Defaults to 2.
	MaxRetries int
	// RetryBaseDelay is the base delay between retries. Defaults to 500ms.
	RetryBaseDelay time.Duration
	// RetryMaxDelay is the maximum delay between retries. Defaults to 5s.
	RetryMaxDelay time.Duration
	// HTTPClient is an optional custom *http.Client. When set, Timeout is ignored.
	HTTPClient *http.Client
	// UserAgent overrides the default User-Agent header.
	UserAgent string
	// Headers are extra HTTP headers sent with every request.
	Headers map[string]string
}

// RequestOptions are per-request overrides that take precedence over client-level defaults.
type RequestOptions struct {
	// Headers are additional HTTP headers merged with client-level headers.
	Headers map[string]string
	// Timeout overrides the client-level timeout for this request.
	Timeout time.Duration
	// MaxRetries overrides the client-level max retries for this request.
	MaxRetries *int
}

// PollingOptions controls async task polling behavior.
type PollingOptions struct {
	// PollInterval is the delay between poll requests. Defaults to 2s.
	PollInterval time.Duration
	// MaxWait is the maximum total wait time. Defaults to 15 minutes.
	MaxWait time.Duration
}

// CallConfig holds resolved request and polling options for a single API call.
// Service methods build one via ResolveCallOptions before issuing the request.
type CallConfig struct {
	// Request holds per-call HTTP overrides (timeout, retries, extra headers).
	Request RequestOptions
	// Polling controls async task polling intervals and maximum wait time.
	Polling PollingOptions
}

// CallOption is implemented by options that configure per-call behavior.
type CallOption interface {
	ApplyCall(*CallConfig)
}

// DefaultClientOptions returns ClientOptions with production defaults.
func DefaultClientOptions() ClientOptions {
	return ClientOptions{
		BaseURL:        DefaultBaseURL,
		Timeout:        DefaultTimeout,
		MaxRetries:     DefaultMaxRetries,
		RetryBaseDelay: DefaultRetryBaseDelay,
		RetryMaxDelay:  DefaultRetryMaxDelay,
	}
}

// DefaultPollingOptions returns PollingOptions with production defaults.
func DefaultPollingOptions() PollingOptions {
	return PollingOptions{PollInterval: DefaultPollInterval, MaxWait: DefaultMaxWait}
}

// ResolveCallOptions applies the given options to a CallConfig with default polling settings.
func ResolveCallOptions(options ...CallOption) CallConfig {
	cfg := CallConfig{Polling: DefaultPollingOptions()}
	for _, option := range options {
		if option != nil {
			option.ApplyCall(&cfg)
		}
	}
	return cfg
}
