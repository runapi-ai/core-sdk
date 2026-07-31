# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::Pricing do
  let(:http) { instance_double(RunApi::Core::HttpClient) }
  let(:pricing) { described_class.new(http) }

  it "lists live schedules with filters and request options" do
    options = RunApi::Core::RequestOptions.new(headers: {"If-None-Match" => '"schedule-v1"'})
    expect(http).to receive(:request)
      .with(:get, "/api/v1/price_schedules?service=kling&action=text_to_video&model=kling-3.0", options: instance_of(RunApi::Core::RequestOptions))
      .and_return({
        "as_of" => "2026-07-23T00:00:00.000000Z",
        "price_schedules" => [{
          "service" => "kling", "action" => "text_to_video", "model" => "kling-3.0",
          "pricing_status" => "available", "catalog_status" => "active", "currency" => "USD",
          "billing_unit" => "per_1k_tokens", "billing_strategy" => "flat",
          "cache_write_price_per_1m_cents" => 125, "billing_config" => {}
        }]
      })

    result = pricing.list(service: "kling", action: "text_to_video", model: "kling-3.0", options:)

    expect(result).to be_a(described_class::ScheduleListResponse)
    expect(result.as_of).to eq("2026-07-23T00:00:00.000000Z")
    expect(result.price_schedules.first.cache_write_price_per_1m_cents).to eq(125)
  end

  it "returns a typed not-modified result for a revalidated schedule" do
    response = RunApi::Core::Response.new(
      body: {"not_modified" => true},
      headers: {"ETag" => '"schedule-v1"'}
    )
    expect(http).to receive(:request)
      .with(:get, "/api/v1/price_schedules", options: instance_of(RunApi::Core::RequestOptions))
      .and_return(response)

    result = pricing.list

    expect(result).to be_a(described_class::ScheduleNotModifiedResponse)
    expect(result.not_modified).to be(true)
    expect(result.response_header("ETag")).to eq('"schedule-v1"')
  end

  it "creates a quote with optional authentication request options" do
    options = RunApi::Core::RequestOptions.new(headers: {"Authorization" => "Bearer standard-key"})
    expect(http).to receive(:request)
      .with(:post, "/api/v1/price_quotes", body: {
        service: "kling", action: "text_to_video", model: "kling-3.0", params: {prompt: "Night city"}
      }, options:)
      .and_return({
        "price_quote" => {
          "service" => "kling", "action" => "text_to_video", "model" => "kling-3.0",
          "pricing_status" => "available", "currency" => "USD", "reservation_amount_cents" => 120,
          "estimate_basis" => "exact", "as_of" => "2026-07-23T00:00:00.000000Z"
        }
      })

    result = pricing.quote(service: "kling", action: "text_to_video", model: "kling-3.0", params: {prompt: "Night city"}, options:)

    expect(result).to be_a(described_class::QuoteResponse)
    expect(result.reservation_amount_cents).to eq(120)
  end
end

RSpec.describe RunApi::Core::PricingClient do
  let(:base_url) { "https://runapi.ai" }

  around do |example|
    previous_env = ENV.delete("RUNAPI_API_KEY")
    previous_global = RunApi.api_key
    RunApi.api_key = nil

    example.run
  ensure
    ENV["RUNAPI_API_KEY"] = previous_env
    RunApi.api_key = previous_global
  end

  it "lists public schedules without an Authorization header" do
    stub = stub_request(:get, "#{base_url}/api/v1/price_schedules")
      .with { |request| !request.headers.key?("Authorization") }
      .to_return(status: 200, body: '{"as_of":"2026-07-23T00:00:00.000000Z","price_schedules":[]}')

    described_class.new(base_url:).list

    expect(stub).to have_been_requested
  end

  it "uses a configured API key when one is available" do
    stub = stub_request(:get, "#{base_url}/api/v1/price_schedules")
      .with(headers: {"Authorization" => "Bearer test-key"})
      .to_return(status: 200, body: '{"as_of":"2026-07-23T00:00:00.000000Z","price_schedules":[]}')

    described_class.new(api_key: "test-key", base_url:).list

    expect(stub).to have_been_requested
  end

  describe "#close" do
    it "closes the SDK-created HTTP client" do
      http = instance_double(RunApi::Core::HttpClient, close: nil)
      allow(RunApi::Core::HttpClient).to receive(:new).and_return(http)

      described_class.new.close

      expect(http).to have_received(:close).once
    end

    it "does not close an injected HTTP client" do
      http = instance_double(RunApi::Core::HttpClient, close: nil)

      described_class.new(http_client: http).close

      expect(http).not_to have_received(:close)
    end
  end
end
