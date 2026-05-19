package core

import "time"

const (
	DefaultBaseURL        = "https://runapi.ai"
	DefaultTimeout        = 15 * time.Minute
	DefaultMaxRetries     = 2
	DefaultRetryBaseDelay = 500 * time.Millisecond
	DefaultRetryMaxDelay  = 5 * time.Second
	DefaultPollInterval   = 2 * time.Second
	DefaultMaxWait        = 15 * time.Minute
)

func SDKUserAgent(version string) string {
	if version == "" {
		version = "dev"
	}
	return "runapi-sdk-go/" + version
}

func CLIUserAgent(version string) string {
	if version == "" {
		version = "dev"
	}
	return "runapi-cli-go/" + version
}
