package core

import "time"

const (
	// DefaultBaseURL is the production RunAPI endpoint.
	DefaultBaseURL = "https://runapi.ai"
	// DefaultTimeout is the per-request HTTP timeout, set high to accommodate long-running generation tasks.
	DefaultTimeout = 15 * time.Minute
	// DefaultMaxRetries is the number of automatic retries on transient failures (429, 5xx).
	DefaultMaxRetries = 2
	// DefaultRetryBaseDelay is the initial backoff interval before the first retry.
	DefaultRetryBaseDelay = 500 * time.Millisecond
	// DefaultRetryMaxDelay caps the exponential backoff between retries.
	DefaultRetryMaxDelay = 5 * time.Second
	// DefaultPollInterval is the delay between status checks when polling an async task.
	DefaultPollInterval = 2 * time.Second
	// DefaultMaxWait is the maximum total time to poll an async task before returning a timeout error.
	DefaultMaxWait = 15 * time.Minute
)

// SDKUserAgent returns the User-Agent header value for SDK HTTP requests.
func SDKUserAgent(version string) string {
	if version == "" {
		version = "dev"
	}
	return "runapi-sdk-go/" + version
}

// CLIUserAgent returns the User-Agent header value for CLI HTTP requests.
func CLIUserAgent(version string) string {
	if version == "" {
		version = "dev"
	}
	return "runapi-cli-go/" + version
}
