# frozen_string_literal: true

require "spec_helper"
require "json"

RSpec.describe RunApi::Core::Error do
  describe ".from_response" do
    def mock_response(code:, body: nil, headers: {})
      response = instance_double(Net::HTTPResponse, code: code.to_s)
      allow(response).to receive(:[]) { |key| headers[key] }
      [response, body]
    end

    it "maps 401 to AuthenticationError" do
      response, body = mock_response(code: 401)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::AuthenticationError)
      expect(error.status).to eq(401)
      expect(error.message).to eq("Unauthorized")
    end

    it "maps 402 to InsufficientCreditsError" do
      response, body = mock_response(code: 402)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::InsufficientCreditsError)
      expect(error.status).to eq(402)
    end

    it "maps 404 to NotFoundError" do
      response, body = mock_response(code: 404)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::NotFoundError)
      expect(error.status).to eq(404)
    end

    it "maps 429 to RateLimitError with retry_after seconds" do
      response, body = mock_response(code: 429, headers: {"retry-after" => "30"})
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::RateLimitError)
      expect(error.status).to eq(429)
      expect(error.retry_after).to eq(30.0)
    end

    it "maps 429 with HTTP-date retry_after" do
      future = (Time.now.utc + 60).httpdate
      response, body = mock_response(code: 429, headers: {"retry-after" => future})
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::RateLimitError)
      expect(error.retry_after).to be_within(2).of(60)
    end

    it "maps 503 to ServiceUnavailableError" do
      response, body = mock_response(code: 503)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::ServiceUnavailableError)
      expect(error.status).to eq(503)
    end

    it "maps 500 to ServerError" do
      response, body = mock_response(code: 500)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::ServerError)
      expect(error.status).to eq(500)
    end

    it "maps 502 to ServerError preserving status" do
      response, body = mock_response(code: 502)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::ServerError)
      expect(error.status).to eq(502)
    end

    it "maps 409 to ConflictError" do
      response, body = mock_response(code: 409)
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::ConflictError)
      expect(error.status).to eq(409)
    end

    it "maps unmapped status to base Error" do
      response, body = mock_response(code: 418)
      error = described_class.from_response(response, body)

      expect(error).to be_an_instance_of(RunApi::Core::Error)
      expect(error.status).to eq(418)
      expect(error.message).to eq("Request failed")
    end

    it "extracts request_id from header" do
      response, body = mock_response(code: 500, headers: {"x-request-id" => "req-123"})
      error = described_class.from_response(response, body)

      expect(error.request_id).to eq("req-123")
    end

    it "extracts message from JSON body with error string" do
      body = {"error" => "Custom error message"}.to_json
      response, = mock_response(code: 400)
      error = described_class.from_response(response, body)

      expect(error.message).to eq("Custom error message")
    end

    it "extracts message from JSON body with nested error" do
      body = {"error" => {"message" => "Nested message"}}.to_json
      response, = mock_response(code: 400)
      error = described_class.from_response(response, body)

      expect(error.message).to eq("Nested message")
    end

    it "preserves explicit HTTP error code and leaves a missing code nil" do
      response, = mock_response(code: 409)

      explicit = described_class.from_response(response, {error: {code: "source_task_not_ready", message: "wait"}}.to_json)
      missing = described_class.from_response(response, {error: {message: "wait"}}.to_json)

      expect(explicit.code).to eq("source_task_not_ready")
      expect(missing.code).to be_nil
    end

    it "preserves continuation codes while classifying by status" do
      cases = [
        [400, "invalid_resource_id", RunApi::Core::ValidationError],
        [409, "request_conflict", RunApi::Core::ConflictError],
        [409, "source_task_not_ready", RunApi::Core::ConflictError],
        [422, "source_task_unusable", RunApi::Core::ValidationError],
        [422, "continuation_not_supported", RunApi::Core::ValidationError],
        [429, "rate_limited", RunApi::Core::RateLimitError],
        [503, "continuation_unavailable", RunApi::Core::ServiceUnavailableError]
      ]

      cases.each do |status, code, error_class|
        response, = mock_response(code: status)
        error = described_class.from_response(response, {error: {code: code, message: "failed"}}.to_json)

        expect(error).to be_a(error_class)
        expect(error.status).to eq(status)
        expect(error.code).to eq(code)
      end
    end

    it "extracts message from JSON body with errors array" do
      body = {"errors" => ["First error"]}.to_json
      response, = mock_response(code: 400)
      error = described_class.from_response(response, body)

      expect(error.message).to eq("First error")
    end

    it "handles HTML error pages" do
      body = "<!DOCTYPE html><html><head><title>502 Bad Gateway</title></head><body><h1>Bad Gateway</h1></body></html>"
      response, = mock_response(code: 502)
      error = described_class.from_response(response, body)

      expect(error.message).to eq("502 Bad Gateway")
      expect(error.details).to include("is_html_error" => true)
    end

    it "handles empty body" do
      response, body = mock_response(code: 500, body: "")
      error = described_class.from_response(response, body)

      expect(error).to be_a(RunApi::Core::ServerError)
      expect(error.message).to eq("Request failed")
    end

    it "handles nil body" do
      response, body = mock_response(code: 500)
      error = described_class.from_response(response, body)

      expect(error.details).to be_nil
    end

    it "handles malformed JSON body" do
      response, = mock_response(code: 400)
      error = described_class.from_response(response, "not json")

      expect(error.details).to eq("not json")
    end
  end

  describe "#to_h" do
    it "returns compact hash" do
      error = RunApi::Core::AuthenticationError.new("Bad key", request_id: "req-1")

      expect(error.to_h).to eq(
        error: "RunApi::Core::AuthenticationError",
        message: "Bad key",
        code: "authentication",
        status: 401,
        request_id: "req-1"
      )
    end
  end
end

RSpec.describe RunApi::Core::ServerError do
  it "defaults to status 500" do
    expect(described_class.new.status).to eq(500)
  end

  it "preserves custom status" do
    expect(described_class.new("Bad gateway", status: 502).status).to eq(502)
  end
end

RSpec.describe RunApi::Core::ServiceUnavailableError do
  it "defaults to status 503" do
    expect(described_class.new.status).to eq(503)
  end
end
