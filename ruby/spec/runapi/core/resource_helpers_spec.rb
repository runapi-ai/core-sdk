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

  describe "#validate_optional!" do
    it "does nothing when key is absent" do
      expect { helper.send(:validate_optional!, {}, :style, %w[pop rock]) }.not_to raise_error
    end

    it "does nothing when value is allowed (symbol key)" do
      expect { helper.send(:validate_optional!, {style: "pop"}, :style, %w[pop rock]) }.not_to raise_error
    end

    it "does nothing when value is allowed (string key)" do
      expect { helper.send(:validate_optional!, {"style" => "pop"}, :style, %w[pop rock]) }.not_to raise_error
    end

    it "raises ValidationError when value is not allowed" do
      expect {
        helper.send(:validate_optional!, {style: "jazz"}, :style, %w[pop rock])
      }.to raise_error(RunApi::Core::ValidationError, /Invalid style: jazz/)
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

  describe "#validate_contract! integer fields" do
    let(:schema) do
      {
        "models" => ["m"],
        "fields_by_model" => {
          "m" => {
            "duration_int" => {"type" => "integer", "min" => 4, "max" => 12},
            "tolerance" => {"type" => "integer"}
          }
        }
      }
    end

    def validate(params)
      helper.send(:validate_contract!, schema, params)
    end

    it "rejects a non-integer value within range" do
      expect { validate("model" => "m", "duration_int" => 11.5) }
        .to raise_error(RunApi::Core::ValidationError, "duration_int must be an integer between 4 and 12")
    end

    it "reports the integer error before the range error" do
      expect { validate("model" => "m", "duration_int" => 2.5) }
        .to raise_error(RunApi::Core::ValidationError, "duration_int must be an integer between 4 and 12")
    end

    it "omits the range detail for a bare integer field" do
      expect { validate("model" => "m", "tolerance" => 3.5) }
        .to raise_error(RunApi::Core::ValidationError, "tolerance must be an integer")
    end

    it "still enforces the range for a valid integer" do
      expect { validate("model" => "m", "duration_int" => 13) }
        .to raise_error(RunApi::Core::ValidationError, "duration_int must be between 4 and 12")
    end

    it "accepts an integer in range and rejects a whole-valued float" do
      expect { validate("model" => "m", "tolerance" => 5) }.not_to raise_error
      # Ruby keeps the Float/Integer distinction (mirrors the gateway).
      expect { validate("model" => "m", "tolerance" => 5.0) }
        .to raise_error(RunApi::Core::ValidationError, "tolerance must be an integer")
    end
  end

  describe "#validate_contract! functional actions" do
    let(:schema) do
      {
        "models" => [],
        "fields_by_model" => {
          "_" => {
            "prompt" => {"required" => true},
            "mode" => {"enum" => ["fast", "quality"]}
          }
        }
      }
    end

    def validate_functional(params)
      helper.send(:validate_contract!, schema, params)
    end

    it "uses underscore fields without requiring model" do
      expect { validate_functional("prompt" => "hello", "mode" => "fast") }.not_to raise_error
      expect { validate_functional("mode" => "fast") }
        .to raise_error(RunApi::Core::ValidationError, "prompt is required")
      expect { validate_functional("prompt" => "hello", "mode" => "slow") }
        .to raise_error(RunApi::Core::ValidationError, "mode must be one of: fast, quality")
    end
  end

  describe "#validate_contract! rule ordering" do
    let(:schema) do
      {
        "models" => ["m"],
        "rules" => [{"when" => {"model" => "m"}, "forbidden" => ["source_task_id"]}],
        "fields_by_model" => {
          "m" => {
            "source_image_urls" => {"required" => true}
          }
        }
      }
    end

    it "reports forbidden rules before missing required fields" do
      expect {
        helper.send(:validate_contract!, schema, "model" => "m", "source_task_id" => "src_1")
      }.to raise_error(RunApi::Core::ValidationError, "source_task_id is not allowed when model is m")
    end
  end
end
