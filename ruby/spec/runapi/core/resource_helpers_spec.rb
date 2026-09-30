# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::ResourceHelpers do
  subject(:helper) do
    Class.new { include RunApi::Core::ResourceHelpers }.new
  end

  describe "#compact_params" do
    it "removes nil values" do
      expect(helper.send(:compact_params, a: "hello", b: nil)).to eq(a: "hello")
    end

    it "removes empty string values" do
      expect(helper.send(:compact_params, a: "hello", b: "")).to eq(a: "hello")
    end

    it "removes whitespace-only string values" do
      expect(helper.send(:compact_params, a: "hello", b: "  ", c: "\t")).to eq(a: "hello")
    end

    it "keeps valid string values" do
      expect(helper.send(:compact_params, a: "hello", b: "world")).to eq(a: "hello", b: "world")
    end

    it "keeps numeric values including zero" do
      expect(helper.send(:compact_params, a: 0, b: 42, c: -1)).to eq(a: 0, b: 42, c: -1)
    end

    it "keeps boolean values including false" do
      expect(helper.send(:compact_params, a: true, b: false)).to eq(a: true, b: false)
    end

    it "keeps arrays" do
      expect(helper.send(:compact_params, a: [1, 2], b: [])).to eq(a: [1, 2], b: [])
    end

    it "keeps hashes" do
      expect(helper.send(:compact_params, a: {nested: true})).to eq(a: {nested: true})
    end

    it "handles mixed types correctly" do
      result = helper.send(:compact_params,
        prompt: "hello",
        vocal_gender: "",
        model: "v4",
        instrumental: false,
        count: 0,
        empty: nil,
        spaces: "   ")

      expect(result).to eq(
        prompt: "hello",
        model: "v4",
        instrumental: false,
        count: 0
      )
    end

    it "returns empty hash when all values are empty" do
      expect(helper.send(:compact_params, a: "", b: nil)).to eq({})
    end

    it "returns same values when nothing to compact" do
      input = {a: "valid", b: 42, c: true}
      expect(helper.send(:compact_params, input)).to eq(input)
    end
  end

  describe "#request" do
    let(:http) { instance_double(RunApi::Core::HttpClient) }
    let(:resource_class) do
      Class.new do
        include RunApi::Core::ResourceHelpers

        def initialize(http)
          @http = http
        end

        public :request
      end
    end
    let(:resource) { resource_class.new(http) }

    it "coerces hash responses into TaskResponse objects" do
      expect(http).to receive(:request).with(:get, "/api/v1/test")
        .and_return("id" => "task-1", "status" => "completed", "audios" => [{"url" => "https://media.example.test/a.mp3"}])

      result = resource.request(:get, "/api/v1/test")

      expect(result).to be_a(RunApi::Core::TaskResponse)
      expect(result.id).to eq("task-1")
      expect(result.audios.first.url).to eq("https://media.example.test/a.mp3")
      expect(result["status"]).to eq("completed")
    end

    it "attaches response headers to typed responses" do
      expect(http).to receive(:request).with(:get, "/api/v1/test")
        .and_return(RunApi::Core::Response.new(
          body: {"id" => "task-1", "status" => "completed"},
          headers: {"X-RunAPI-Task-Id" => "task-ref-1"}
        ))

      result = resource.request(:get, "/api/v1/test")

      expect(result).to be_a(RunApi::Core::TaskResponse)
      expect(result.runapi_task_id).to eq("task-ref-1")
      expect(result.response_headers["X-RunAPI-Task-Id"]).to eq("task-ref-1")
      expect(result.to_h).to eq("id" => "task-1", "status" => "completed")
    end

    it "attaches response headers to typed array response items" do
      expect(http).to receive(:request).with(:get, "/api/v1/test")
        .and_return(RunApi::Core::Response.new(
          body: [{"id" => "task-1", "status" => "completed"}],
          headers: {"X-RunAPI-Task-Id" => "task-ref-1"}
        ))

      result = resource.request(:get, "/api/v1/test")

      expect(result).to contain_exactly(an_instance_of(RunApi::Core::TaskResponse))
      expect(result.first.runapi_task_id).to eq("task-ref-1")
      expect(result.first.response_headers["X-RunAPI-Task-Id"]).to eq("task-ref-1")
      expect(result.first.to_h).to eq("id" => "task-1", "status" => "completed")
    end

    it "keeps POST signature with body only" do
      expect(http).to receive(:request).with(:post, "/api/v1/test", body: {prompt: "hello"})
        .and_return("id" => "task-2")

      result = resource.request(:post, "/api/v1/test", body: {prompt: "hello"})
      expect(result.id).to eq("task-2")
    end

    it "returns non-hash responses unchanged" do
      expect(http).to receive(:request).with(:get, "/api/v1/test")
        .and_return("plain text")

      expect(resource.request(:get, "/api/v1/test")).to eq("plain text")
    end
  end
end
