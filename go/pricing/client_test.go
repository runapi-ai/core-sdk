package pricing

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/runapi-ai/core-sdk/go/core"
)

type stubHTTPClient struct {
	method string
	path   string
	body   any
	query  map[string]string
}

func (s *stubHTTPClient) Request(_ context.Context, method, path string, opts *core.HTTPRequestOptions) (json.RawMessage, error) {
	s.method, s.path = method, path
	if opts != nil {
		s.body, s.query = opts.Body, opts.Query
	}
	if method == "GET" {
		return json.RawMessage(`{"as_of":"2026-07-23T00:00:00.000000Z","price_schedules":[{"service":"suno","action":"convert_audio","model":null,"pricing_status":"available","catalog_status":"active","currency":"USD","billing_unit":"per_call","billing_strategy":"flat","unit_price_cents":10,"billing_config":{}}]}`), nil
	}
	return json.RawMessage(`{"price_quote":{"service":"suno","action":"convert_audio","model":null,"pricing_status":"available","currency":"USD","reservation_amount_cents":10,"estimate_basis":"exact","as_of":"2026-07-23T00:00:00.000000Z"}}`), nil
}

func TestListUsesPublicScheduleContract(t *testing.T) {
	stub := &stubHTTPClient{}
	response, err := NewClientWithHTTP(stub).List(context.Background(), ListParams{Service: "suno", Action: "convert_audio"})
	if err != nil {
		t.Fatal(err)
	}
	if stub.method != "GET" || stub.path != schedulesPath || stub.query["service"] != "suno" || stub.query["action"] != "convert_audio" {
		t.Fatalf("unexpected request: %#v", stub)
	}
	if len(response.PriceSchedules) != 1 || response.PriceSchedules[0].UnitPriceCents == nil || *response.PriceSchedules[0].UnitPriceCents != 10 {
		t.Fatalf("unexpected response: %#v", response)
	}
}

func TestQuoteUsesPublicQuoteContract(t *testing.T) {
	stub := &stubHTTPClient{}
	response, err := NewClientWithHTTP(stub).Quote(context.Background(), QuoteParams{Service: "suno", Action: "convert_audio", Params: map[string]any{}})
	if err != nil {
		t.Fatal(err)
	}
	if stub.method != "POST" || stub.path != quotesPath {
		t.Fatalf("unexpected request: %#v", stub)
	}
	body := stub.body.(map[string]any)
	if body["service"] != "suno" || body["action"] != "convert_audio" {
		t.Fatalf("unexpected body: %#v", body)
	}
	if response.PriceQuote.ReservationAmountCents != 10 || response.PriceQuote.EstimateBasis != "exact" {
		t.Fatalf("unexpected response: %#v", response)
	}
}
