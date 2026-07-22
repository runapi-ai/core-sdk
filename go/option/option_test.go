package option

import (
	"net/http"
	"testing"
	"time"

	"github.com/runapi-ai/core-sdk/go/core"
)

func TestWithAPIKey(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithAPIKey("sk-test"))
	if cfg.APIKey != "sk-test" {
		t.Fatalf("expected sk-test, got %s", cfg.APIKey)
	}
}

func TestWithBaseURL(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithBaseURL("https://runapi.ai"))
	if cfg.BaseURL != "https://runapi.ai" {
		t.Fatalf("expected custom URL, got %s", cfg.BaseURL)
	}
}

func TestWithHTTPClient(t *testing.T) {
	custom := &http.Client{Timeout: 99 * time.Second}
	cfg, _ := ResolveClientOptions(WithHTTPClient(custom))
	if cfg.HTTPClient != custom {
		t.Fatal("expected custom HTTP client")
	}
}

func TestWithUserAgent(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithUserAgent("my-app/1.0"))
	if cfg.UserAgent != "my-app/1.0" {
		t.Fatalf("expected my-app/1.0, got %s", cfg.UserAgent)
	}
}

func TestWithTimeoutAppliesClientAndRequest(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithTimeout(30 * time.Second))
	if cfg.Timeout != 30*time.Second {
		t.Fatalf("expected 30s client timeout, got %s", cfg.Timeout)
	}

	reqOpts, _ := ResolveRequestOptions(WithTimeout(15 * time.Second))
	if reqOpts.Timeout != 15*time.Second {
		t.Fatalf("expected 15s request timeout, got %s", reqOpts.Timeout)
	}
}

func TestWithMaxRetriesAppliesClientAndRequest(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithMaxRetries(5))
	if cfg.MaxRetries != 5 {
		t.Fatalf("expected 5, got %d", cfg.MaxRetries)
	}

	reqOpts, _ := ResolveRequestOptions(WithMaxRetries(2))
	if reqOpts.MaxRetries == nil || *reqOpts.MaxRetries != 2 {
		t.Fatalf("expected 2, got %v", reqOpts.MaxRetries)
	}
}

func TestWithRetryDelays(t *testing.T) {
	cfg, _ := ResolveClientOptions(
		WithRetryBaseDelay(100*time.Millisecond),
		WithRetryMaxDelay(5*time.Second),
	)
	if cfg.RetryBaseDelay != 100*time.Millisecond {
		t.Fatalf("expected 100ms base delay, got %s", cfg.RetryBaseDelay)
	}
	if cfg.RetryMaxDelay != 5*time.Second {
		t.Fatalf("expected 5s max delay, got %s", cfg.RetryMaxDelay)
	}
}

func TestWithHeaderAppliesClientAndRequest(t *testing.T) {
	cfg, _ := ResolveClientOptions(WithHeader("X-Custom", "val"))
	if cfg.Headers["X-Custom"] != "val" {
		t.Fatalf("expected header on client, got %v", cfg.Headers)
	}

	reqOpts, _ := ResolveRequestOptions(WithHeader("X-Req", "req-val"))
	if reqOpts.Headers["X-Req"] != "req-val" {
		t.Fatalf("expected header on request, got %v", reqOpts.Headers)
	}
}

func TestWithHeadersMergesMultiple(t *testing.T) {
	reqOpts, _ := ResolveRequestOptions(
		WithHeaders(map[string]string{"A": "1", "B": "2"}),
		WithHeader("C", "3"),
	)
	for _, pair := range []struct{ k, v string }{{"A", "1"}, {"B", "2"}, {"C", "3"}} {
		if reqOpts.Headers[pair.k] != pair.v {
			t.Fatalf("expected header %s=%s, got %v", pair.k, pair.v, reqOpts.Headers)
		}
	}
}

func TestWithPollIntervalAndMaxWait(t *testing.T) {
	_, pollingOpts := ResolveRequestOptions(
		WithPollInterval(2*time.Second),
		WithMaxWait(60*time.Second),
	)
	if pollingOpts.PollInterval != 2*time.Second {
		t.Fatalf("expected 2s poll interval, got %s", pollingOpts.PollInterval)
	}
	if pollingOpts.MaxWait != 60*time.Second {
		t.Fatalf("expected 60s max wait, got %s", pollingOpts.MaxWait)
	}
}

func TestResolveClientOptionsDefaults(t *testing.T) {
	cfg, _ := ResolveClientOptions()
	defaults := core.DefaultClientOptions()
	if cfg.BaseURL != defaults.BaseURL {
		t.Fatalf("expected default base URL %s, got %s", defaults.BaseURL, cfg.BaseURL)
	}
	if cfg.Timeout != defaults.Timeout {
		t.Fatalf("expected default timeout %s, got %s", defaults.Timeout, cfg.Timeout)
	}
}

func TestResolveClientOptionsSkipsNil(t *testing.T) {
	cfg, _ := ResolveClientOptions(nil, WithAPIKey("sk-test"), nil)
	if cfg.APIKey != "sk-test" {
		t.Fatalf("expected sk-test, got %s", cfg.APIKey)
	}
}

func TestResolveRequestOptionsSkipsNil(t *testing.T) {
	reqOpts, _ := ResolveRequestOptions(nil, WithTimeout(5*time.Second), nil)
	if reqOpts.Timeout != 5*time.Second {
		t.Fatalf("expected 5s, got %s", reqOpts.Timeout)
	}
}
