# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::BaseModel do
  let(:model_class) do
    Class.new(described_class) do
      required :id, String
      optional :status, String
      optional :items, [RunApi::Core::DynamicModel]
      optional :meta, -> { RunApi::Core::DynamicModel }
      optional :kind, String, enum: %w[a b]
    end
  end

  describe ".from_hash" do
    it "builds an instance from a Hash" do
      model = model_class.from_hash("id" => "abc")

      expect(model).to be_a(model_class)
      expect(model.id).to eq("abc")
    end

    it "raises TypeError for non-Hash payloads" do
      expect { model_class.from_hash("bad") }.to raise_error(TypeError)
    end
  end

  describe "#initialize" do
    it "raises ValidationError when required field is missing" do
      expect { model_class.new("status" => "ok") }
        .to raise_error(RunApi::Core::ValidationError, /id is required/)
    end

    it "supports Hash-style and dot-style access" do
      model = model_class.new("id" => "abc", "status" => "completed")

      expect(model["id"]).to eq("abc")
      expect(model.status).to eq("completed")
    end

    it "coerces nested hashes and arrays to DynamicModel" do
      model = model_class.new(
        "id" => "abc",
        "meta" => {"count" => 2},
        "items" => [{"name" => "first"}],
        "extra_field" => {"nested" => true}
      )

      expect(model.meta).to be_a(RunApi::Core::DynamicModel)
      expect(model.meta.count).to eq(2)
      expect(model.items.first.name).to eq("first")
      expect(model.extra_field.nested).to eq(true)
      expect(model.dig("extra_field", "nested")).to eq(true)
    end

    it "validates enum fields" do
      expect { model_class.new("id" => "abc", "kind" => "invalid") }
        .to raise_error(RunApi::Core::ValidationError, /Invalid kind/)
    end
  end

  describe "#to_h" do
    it "serializes recursively to plain hashes" do
      model = model_class.new("id" => "abc", "meta" => {"flag" => true})

      expect(model.to_h).to eq({"id" => "abc", "meta" => {"flag" => true}})
    end

    it "supports equality with hash payloads" do
      model = model_class.new("id" => "abc", "status" => "completed")

      expect(model).to eq({"id" => "abc", "status" => "completed"})
    end
  end

  describe "response headers" do
    it "stores case-insensitive response headers outside the serialized body" do
      model = model_class.new("id" => "abc")
      model.with_response_headers("X-RunAPI-Task-Id" => "task-ref-1")

      expect(model.response_header("x-runapi-task-id")).to eq("task-ref-1")
      expect(model.runapi_task_id).to eq("task-ref-1")
      expect(model.to_h).to eq("id" => "abc")
    end
  end
end
