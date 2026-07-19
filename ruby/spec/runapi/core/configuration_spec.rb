# frozen_string_literal: true

require "spec_helper"

RSpec.describe "RunApi configuration" do
  after do
    RunApi.api_key = nil
    RunApi.base_url = RunApi::Core::Constants::DEFAULT_BASE_URL
  end

  describe ".configure" do
    it "sets api_key and base_url via block" do
      RunApi.configure do |c|
        c.api_key = "test-key"
        c.base_url = "https://custom.runapi.ai"
      end

      expect(RunApi.api_key).to eq("test-key")
      expect(RunApi.base_url).to eq("https://custom.runapi.ai")
    end
  end

  describe ".api_key" do
    it "defaults to nil" do
      expect(RunApi.api_key).to be_nil
    end

    it "is settable directly" do
      RunApi.api_key = "direct-key"
      expect(RunApi.api_key).to eq("direct-key")
    end
  end

  describe ".base_url" do
    it "defaults to https://runapi.ai" do
      expect(RunApi.base_url).to eq("https://runapi.ai")
    end
  end
end
