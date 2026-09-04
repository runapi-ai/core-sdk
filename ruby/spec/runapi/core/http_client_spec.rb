# frozen_string_literal: true

require "spec_helper"
require "tempfile"

RSpec.describe RunApi::Core::HttpClient do
  let(:options) do
    RunApi::Core::ClientOptions.new(
      api_key: "test-key",
      base_url: "https://runapi.ai",
      max_retries: 2,
      retry_base_delay: 0.01,
      retry_max_delay: 0.05
    )
  end
  let(:client) { described_class.new(options) }
  let(:base) { "https://runapi.ai" }

  before do
    allow_any_instance_of(Net::HTTP).to receive(:start).and_return(true)
  end

  describe "connection pool lifecycle" do
    it "creates the configured connection pool" do
      expect(ConnectionPool).to receive(:new).with(size: 5, timeout: 5).and_call_original

      described_class.new(options)
    end

    it "reuses and closes its connection" do
      response = Net::HTTPOK.new("1.1", "200", "OK")
      response.instance_variable_set(:@body, '{"ok":true}')
      response.instance_variable_set(:@read, true)
      connection = instance_double(Net::HTTP, started?: true, request: response, finish: nil)

      allow(client).to receive(:build_connection).and_return(connection)

      2.times { client.request(:get, "/api/v1/test") }
      client.close

      expect(client).to have_received(:build_connection).once
      expect(connection).to have_received(:request).twice
      expect(connection).to have_received(:finish).once
    end
  end

  describe "#request" do
    it "rejects a cross-origin absolute URL before sending credentials" do
      expect {
        client.request(:get, "https://attacker.example/tasks/task-1")
      }.to raise_error(RunApi::Core::ValidationError, "Request URL must use the configured RunAPI origin")

      expect(a_request(:get, "https://attacker.example/tasks/task-1")).not_to have_been_made
    end

    it "accepts an absolute URL on the configured origin" do
      stub_request(:get, "#{base}/api/v1/tasks/task-1").to_return(status: 200, body: "{}")

      expect(client.request(:get, "#{base}/api/v1/tasks/task-1")).to eq({})
    end

    it "returns parsed JSON on success" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 200, body: '{"id":"123"}')

      result = client.request(:get, "/api/v1/test")
      expect(result).to eq("id" => "123")
    end

    it "keeps response headers on successful JSON responses" do
      stub_request(:post, "#{base}/api/v1/test")
        .to_return(status: 200, body: '{"id":"task-1"}', headers: {"X-RunAPI-Task-Id" => "task-ref-1"})

      result = client.request(:post, "/api/v1/test", body: {prompt: "hello"})

      expect(result).to eq("id" => "task-1")
      expect(result.response_headers["X-RunAPI-Task-Id"]).to eq("task-ref-1")
      expect(result.response_headers["x-runapi-task-id"]).to eq("task-ref-1")
    end

    it "keeps response headers on successful JSON array responses" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 200, body: '[{"id":"task-1"}]', headers: {"X-RunAPI-Task-Id" => "task-ref-1"})

      result = client.request(:get, "/api/v1/test")

      expect(result).to be_a(RunApi::Core::Response)
      expect(result).to eq([{"id" => "task-1"}])
      expect(result.body).to eq([{"id" => "task-1"}])
      expect(result[0]).to eq("id" => "task-1")
      expect(result.response_headers["x-runapi-task-id"]).to eq("task-ref-1")
    end

    it "keeps successful response objects hash-compatible after mutation" do
      stub_request(:post, "#{base}/api/v1/test")
        .to_return(status: 200, body: '{"id":"task-1"}')

      result = client.request(:post, "/api/v1/test", body: {prompt: "hello"})
      result["status"] = "completed"

      expect(result["status"]).to eq("completed")
      expect(result.fetch("status")).to eq("completed")
      expect(result.to_h).to eq("id" => "task-1", "status" => "completed")
    end

    it "sends Bearer token and User-Agent headers" do
      stub_request(:get, "#{base}/api/v1/test")
        .with(headers: {
          "Authorization" => "Bearer test-key",
          "User-Agent" => RunApi::Core::Constants::SDK_USER_AGENT
        })
        .to_return(status: 200, body: "{}")

      client.request(:get, "/api/v1/test")
    end

    it "sends custom headers from request options" do
      options = RunApi::Core::RequestOptions.new(headers: {"X-Client-Request-Id" => "req-123"})

      stub_request(:get, "#{base}/api/v1/test")
        .with(headers: {"X-Client-Request-Id" => "req-123"})
        .to_return(status: 200, body: "{}")

      client.request(:get, "/api/v1/test", options: options)
    end

    it "sends JSON body for POST" do
      stub_request(:post, "#{base}/api/v1/test")
        .with(body: '{"prompt":"hello"}')
        .to_return(status: 200, body: '{"id":"1"}')

      result = client.request(:post, "/api/v1/test", body: {prompt: "hello"})
      expect(result).to eq("id" => "1")
    end

    it "sends multipart form data without a JSON content type" do
      tempfile = Tempfile.new(["image", ".png"])
      tempfile.write("png")
      tempfile.close

      request = client.send(:build_request, :post, URI("#{base}/api/v1/files"), RunApi::Core::MultipartBody.new(
        fields: {file_name: "image.png", "languages[]": ["en", "zh"]},
        files: {
          file: RunApi::Core::MultipartFile.new(
            path: tempfile.path,
            filename: "image.png",
            content_type: "image/png"
          )
        }
      ), nil)

      expect(request["Content-Type"]).to eq("multipart/form-data")
      expect(request["Accept"]).to eq("application/json")
      expect(request.body).to be_nil

      body_data = request.instance_variable_get(:@body_data)
      expect(body_data.first).to eq(["file_name", "image.png"])
      expect(body_data[1, 2]).to eq([["languages[]", "en"], ["languages[]", "zh"]])
      key, file_part, options = body_data[3]
      expect(key).to eq("file")
      expect(file_part).to be_a(File)
      expect(file_part.binmode?).to be(true)
      expect(file_part.read).to eq("png")
      expect(options).to eq({filename: "image.png", content_type: "image/png"})
    ensure
      file_part&.close
      tempfile.unlink
    end

    it "returns nil for empty body" do
      stub_request(:delete, "#{base}/api/v1/test")
        .to_return(status: 204, body: "")

      expect(client.request(:delete, "/api/v1/test")).to be_nil
    end

    it "returns raw string for non-JSON body" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 200, body: "plain text")

      expect(client.request(:get, "/api/v1/test")).to eq("plain text")
    end

    it "keeps text, SRT, and VTT responses raw" do
      {
        "text/plain" => "transcript",
        "application/x-subrip" => "1\n00:00:00,000 --> 00:00:01,000\nHello\n",
        "text/vtt" => "WEBVTT\n\n00:00.000 --> 00:01.000\nHello\n"
      }.each do |content_type, body|
        path = "/api/v1/#{content_type.delete("^a-z")}"
        stub_request(:get, "#{base}#{path}")
          .to_return(status: 200, body:, headers: {"Content-Type" => content_type})

        expect(client.request(:get, path)).to eq(body)
      end
    end

    it "returns a response for an allowed 304 revalidation" do
      request_options = RunApi::Core::RequestOptions.new(
        headers: {"If-None-Match" => '"schedule-v1"'},
        allow_not_modified: true
      )
      stub_request(:get, "#{base}/api/v1/price_schedules")
        .with(headers: {"If-None-Match" => '"schedule-v1"'})
        .to_return(status: 304, body: "", headers: {"ETag" => '"schedule-v1"'})

      result = client.request(:get, "/api/v1/price_schedules", options: request_options)

      expect(result).to be_a(RunApi::Core::Response)
      expect(result.body).to eq("not_modified" => true)
      expect(result.response_headers["ETag"]).to eq('"schedule-v1"')
    end
  end

  describe "error mapping" do
    {
      401 => RunApi::Core::AuthenticationError,
      402 => RunApi::Core::InsufficientCreditsError,
      404 => RunApi::Core::NotFoundError,
      422 => RunApi::Core::ValidationError,
      429 => RunApi::Core::RateLimitError,
      503 => RunApi::Core::ServiceUnavailableError
    }.each do |status, error_class|
      it "raises #{error_class} for HTTP #{status}" do
        stub_request(:get, "#{base}/api/v1/test")
          .to_return(status: status, body: '{"error":"fail"}')

        expect { client.request(:get, "/api/v1/test") }.to raise_error(error_class)
      end
    end

    it "keeps response headers on HTTP errors" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 500, body: '{"error":"fail"}', headers: {"X-RunAPI-Task-Id" => "task-ref-1"})

      expect {
        client.request(:get, "/api/v1/test")
      }.to raise_error(RunApi::Core::ServerError) { |error|
        expect(error.runapi_task_id).to eq("task-ref-1")
        expect(error.response_headers["x-runapi-task-id"]).to eq("task-ref-1")
      }
    end
  end

  describe "retry behavior" do
    it "retries idempotent GET on 503" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 503, body: '{"error":"down"}')
        .then.to_return(status: 200, body: '{"ok":true}')

      allow(client).to receive(:sleep)
      result = client.request(:get, "/api/v1/test")
      expect(result).to eq("ok" => true)
    end

    it "does NOT retry POST on 503" do
      stub_request(:post, "#{base}/api/v1/test")
        .to_return(status: 503, body: '{"error":"down"}')

      expect { client.request(:post, "/api/v1/test") }
        .to raise_error(RunApi::Core::ServiceUnavailableError)
    end

    it "respects Retry-After header on 429" do
      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 429, body: '{"error":"rate limited"}', headers: {"Retry-After" => "1"})
        .then.to_return(status: 200, body: '{"ok":true}')

      expect(client).to receive(:sleep).with(1.0)
      result = client.request(:get, "/api/v1/test")
      expect(result).to eq("ok" => true)
    end
  end

  describe "stale connection recovery" do
    it "recovers from Errno::EPIPE" do
      call_count = 0
      allow_any_instance_of(ConnectionPool).to receive(:with) do |&block|
        call_count += 1
        raise Errno::EPIPE if call_count == 1

        http = Net::HTTP.new("runapi.ai", 443)
        http.use_ssl = true
        block.call(http)
      end

      stub_request(:get, "#{base}/api/v1/test")
        .to_return(status: 200, body: '{"ok":true}')

      result = client.request(:get, "/api/v1/test")
      expect(result).to eq("ok" => true)
    end
  end

  describe "custom http_client via ClientOptions" do
    it "is accessible on ClientOptions" do
      custom = double("custom_http")
      opts = RunApi::Core::ClientOptions.new(api_key: "key", http_client: custom)
      expect(opts.http_client).to eq(custom)
    end

    it "defaults to nil" do
      opts = RunApi::Core::ClientOptions.new(api_key: "key")
      expect(opts.http_client).to be_nil
    end
  end

  describe "network errors" do
    it "wraps Net::OpenTimeout as TimeoutError" do
      allow_any_instance_of(ConnectionPool).to receive(:with)
        .and_raise(Net::OpenTimeout, "timed out")

      expect { client.request(:get, "/api/v1/test") }
        .to raise_error(RunApi::Core::TimeoutError, "timed out")
    end

    it "wraps SocketError as NetworkError" do
      allow_any_instance_of(ConnectionPool).to receive(:with)
        .and_raise(SocketError, "getaddrinfo failed")

      expect { client.request(:get, "/api/v1/test") }
        .to raise_error(RunApi::Core::NetworkError, "getaddrinfo failed")
    end
  end
end
