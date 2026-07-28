# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::ClientOptions do
  after do
    RunApi.api_key = nil
    RunApi.base_url = RunApi::Core::Constants::DEFAULT_BASE_URL
  end

  it "inherits base_url from RunApi.base_url" do
    RunApi.base_url = "https://custom.runapi.ai"
    opts = described_class.new(api_key: "key")

    expect(opts.base_url).to eq("https://custom.runapi.ai")
  end

  it "allows explicit base_url override" do
    RunApi.base_url = "https://global.runapi.ai"
    opts = described_class.new(api_key: "key", base_url: "https://override.runapi.ai")

    expect(opts.base_url).to eq("https://override.runapi.ai")
  end

  it "sets default timeout from constants" do
    opts = described_class.new(api_key: "key")

    expect(opts.timeout).to eq(RunApi::Core::Constants::TIMEOUTS[:http_request])
  end

  it "sets default retry config from constants" do
    opts = described_class.new(api_key: "key")

    expect(opts.max_retries).to eq(RunApi::Core::Constants::RETRY_CONFIG[:max_retries])
    expect(opts.retry_base_delay).to eq(RunApi::Core::Constants::RETRY_CONFIG[:base_delay])
    expect(opts.retry_max_delay).to eq(RunApi::Core::Constants::RETRY_CONFIG[:max_delay])
  end
end

RSpec.describe RunApi::Core::PollingOptions do
  it "defaults max_wait to polling_max_wait" do
    opts = described_class.new
    expect(opts.max_wait).to eq(RunApi::Core::Constants::TIMEOUTS[:polling_max_wait])
  end

  it "defaults poll_interval to polling_interval" do
    opts = described_class.new
    expect(opts.poll_interval).to eq(RunApi::Core::Constants::TIMEOUTS[:polling_interval])
  end

  it "allows explicit max_wait override" do
    opts = described_class.new(max_wait: 60)
    expect(opts.max_wait).to eq(60)
  end
end

RSpec.describe RunApi::Core::TaskResponse do
  it "coerces billing facts while preserving unknown fields" do
    task = described_class.new(
      "status" => "failed",
      "provider_extension" => "preserved",
      "billing" => {
        "reservation" => {"amount_cents" => 120},
        "settlement" => {"charged_amount_cents" => 95, "amount_micro_cents" => 9_500_000},
        "refund" => {"refunded_at" => "2026-07-23T00:00:00.000000Z"}
      }
    )

    expect(task.billing).to be_a(RunApi::Core::TaskBillingFacts)
    expect(task.billing.settlement).to be_a(RunApi::Core::TaskSettlement)
    expect(task.billing.settlement.charged_amount_cents).to eq(95)
    expect(task.provider_extension).to eq("preserved")
  end
end
