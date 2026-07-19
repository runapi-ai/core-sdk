# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::Auth do
  before do
    @previous_env = ENV.delete("RUNAPI_API_KEY")
    @previous_global = RunApi.api_key
    RunApi.api_key = nil
  end

  after do
    ENV["RUNAPI_API_KEY"] = @previous_env
    RunApi.api_key = @previous_global
  end

  describe ".resolve_api_key" do
    it "returns the explicit key when provided" do
      expect(described_class.resolve_api_key("explicit-key")).to eq("explicit-key")
    end

    it "reads RUNAPI_API_KEY when explicit is blank" do
      ENV["RUNAPI_API_KEY"] = "env-key"
      expect(described_class.resolve_api_key(nil)).to eq("env-key")
    end

    it "falls back to RunApi.api_key when explicit and env are blank" do
      RunApi.api_key = "global-key"
      expect(described_class.resolve_api_key(nil)).to eq("global-key")
    end

    it "prefers explicit over global and env" do
      RunApi.api_key = "global-key"
      ENV["RUNAPI_API_KEY"] = "env-key"
      expect(described_class.resolve_api_key("explicit-key")).to eq("explicit-key")
    end

    it "prefers global over env when explicit is blank" do
      RunApi.api_key = "global-key"
      ENV["RUNAPI_API_KEY"] = "env-key"
      expect(described_class.resolve_api_key(nil)).to eq("global-key")
    end

    it "trims surrounding whitespace on explicit, global, and env values" do
      expect(described_class.resolve_api_key("  explicit-key  ")).to eq("explicit-key")

      RunApi.api_key = "  global-key  "
      expect(described_class.resolve_api_key(nil)).to eq("global-key")

      RunApi.api_key = nil
      ENV["RUNAPI_API_KEY"] = "  env-key  "
      expect(described_class.resolve_api_key(nil)).to eq("env-key")
    end

    it "treats blank explicit values as missing and falls back" do
      ENV["RUNAPI_API_KEY"] = "env-key"
      expect(described_class.resolve_api_key("")).to eq("env-key")
      expect(described_class.resolve_api_key("   ")).to eq("env-key")
    end

    it "raises AuthenticationError when no source yields a value" do
      expect { described_class.resolve_api_key(nil) }
        .to raise_error(RunApi::Core::AuthenticationError, /RUNAPI_API_KEY/)
    end

    it "raises AuthenticationError when every source is blank" do
      RunApi.api_key = "  "
      ENV["RUNAPI_API_KEY"] = "  "
      expect { described_class.resolve_api_key("") }
        .to raise_error(RunApi::Core::AuthenticationError)
    end
  end
end
