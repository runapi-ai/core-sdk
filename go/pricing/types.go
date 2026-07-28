package pricing

// ListParams filters a Price Schedule by public endpoint identity.
type ListParams struct {
	Service string
	Action  string
	Model   string
}

// ListResponse is the current Price Schedule response.
type ListResponse struct {
	AsOf           string          `json:"as_of"`
	PriceSchedules []PriceSchedule `json:"price_schedules"`
}

// PriceSchedule is one publicly priced endpoint identity.
type PriceSchedule struct {
	Service                     string         `json:"service"`
	Action                      string         `json:"action"`
	Model                       *string        `json:"model"`
	PricingStatus               string         `json:"pricing_status"`
	CatalogStatus               string         `json:"catalog_status"`
	Currency                    string         `json:"currency"`
	BillingUnit                 string         `json:"billing_unit"`
	BillingStrategy             string         `json:"billing_strategy"`
	UnitPriceCents              *int64         `json:"unit_price_cents"`
	InputPricePer1MCents        *int64         `json:"input_price_per_1m_cents"`
	OutputPricePer1MCents       *int64         `json:"output_price_per_1m_cents"`
	CacheReadPricePer1MCents    *int64         `json:"cache_read_price_per_1m_cents"`
	CacheWrite5MPricePer1MCents *int64         `json:"cache_write_5m_price_per_1m_cents"`
	CacheWrite1HPricePer1MCents *int64         `json:"cache_write_1h_price_per_1m_cents"`
	BillingConfig               map[string]any `json:"billing_config"`
}

// QuoteParams selects an endpoint and supplies its Pricing Inputs.
type QuoteParams struct {
	Service string         `json:"service"`
	Action  string         `json:"action"`
	Model   string         `json:"model,omitempty"`
	Params  map[string]any `json:"params"`
}

// QuoteResponse is a parameter-specific reservation estimate.
type QuoteResponse struct {
	PriceQuote PriceQuote `json:"price_quote"`
}

// PriceQuote contains the runtime-derived reservation amount and basis.
type PriceQuote struct {
	Service                string  `json:"service"`
	Action                 string  `json:"action"`
	Model                  *string `json:"model"`
	PricingStatus          string  `json:"pricing_status"`
	Currency               string  `json:"currency"`
	ReservationAmountCents int64   `json:"reservation_amount_cents"`
	EstimateBasis          string  `json:"estimate_basis"`
	AsOf                   string  `json:"as_of"`
}
