# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::Client do
  after { RunApi.api_key = nil }

  describe "#close" do
    it "closes the SDK-created HTTP client" do
      http = instance_double(RunApi::Core::HttpClient, close: nil)
      allow(RunApi::Core::HttpClient).to receive(:new).and_return(http)

      described_class.new(api_key: "test-key").close

      expect(http).to have_received(:close).once
    end

    it "does not close an injected HTTP client" do
      http = instance_double(RunApi::Core::HttpClient, close: nil)

      described_class.new(api_key: "test-key", http_client: http).close

      expect(http).not_to have_received(:close)
    end
  end
end
