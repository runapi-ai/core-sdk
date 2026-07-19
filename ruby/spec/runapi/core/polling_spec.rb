# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::Polling do
  let(:options) do
    RunApi::Core::PollingOptions.new(
      poll_interval: 0.01,
      max_wait: 1
    )
  end

  before { allow(described_class).to receive(:sleep) }

  describe ".poll_until_complete" do
    it "returns immediately when status is completed" do
      response = {"status" => "completed", "images" => [{"url" => "https://cdn.runapi.ai/public/samples/input.png"}]}

      result = described_class.poll_until_complete(options) { response }
      expect(result).to eq(response)
    end

    it "supports typed model responses" do
      response = RunApi::Core::TaskResponse.new(
        "status" => "completed",
        "audios" => [{"audio_url" => "https://cdn.runapi.ai/public/samples/audio.mp3"}]
      )

      result = described_class.poll_until_complete(options) { response }
      expect(result).to be_a(RunApi::Core::TaskResponse)
      expect(result.audios.first.audio_url).to eq("https://cdn.runapi.ai/public/samples/audio.mp3")
    end

    it "polls until completed" do
      responses = [
        {"status" => "pending"},
        {"status" => "processing"},
        {"status" => "completed", "images" => [{"url" => "https://cdn.runapi.ai/public/samples/input.png"}]}
      ]
      call_index = 0

      result = described_class.poll_until_complete(options) do
        r = responses[call_index]
        call_index += 1
        r
      end

      expect(result["status"]).to eq("completed")
      expect(call_index).to eq(3)
    end

    it "raises TaskFailedError when status is failed" do
      response = {"status" => "failed", "error" => "Generation failed"}

      expect {
        described_class.poll_until_complete(options) { response }
      }.to raise_error(RunApi::Core::TaskFailedError, "Generation failed")
    end

    it "includes details in TaskFailedError" do
      response = {"status" => "failed", "error" => "oops", "code" => 500}

      begin
        described_class.poll_until_complete(options) { response }
      rescue RunApi::Core::TaskFailedError => e
        expect(e.details).to eq(response)
      end
    end

    it "serializes model details in TaskFailedError" do
      response = RunApi::Core::TaskResponse.new("status" => "failed", "error" => "oops", "code" => 500)

      begin
        described_class.poll_until_complete(options) { response }
      rescue RunApi::Core::TaskFailedError => e
        expect(e.details).to eq({"status" => "failed", "error" => "oops", "code" => 500})
      end
    end

    it "copies model response headers to TaskFailedError" do
      response = RunApi::Core::TaskResponse.new("status" => "failed", "error" => "oops")
        .with_response_headers("X-RunAPI-Task-Id" => "task-ref-1")

      expect {
        described_class.poll_until_complete(options) { response }
      }.to raise_error(RunApi::Core::TaskFailedError) { |error|
        expect(error.runapi_task_id).to eq("task-ref-1")
        expect(error.response_headers["x-runapi-task-id"]).to eq("task-ref-1")
      }
    end

    it "raises TaskTimeoutError when max_wait exceeded" do
      short_opts = RunApi::Core::PollingOptions.new(poll_interval: 0.01, max_wait: 0)

      expect {
        described_class.poll_until_complete(short_opts) { {"status" => "processing"} }
      }.to raise_error(RunApi::Core::TaskTimeoutError)
    end

    it "copies last response headers to TaskTimeoutError" do
      short_opts = RunApi::Core::PollingOptions.new(poll_interval: 0.01, max_wait: 0)
      response = RunApi::Core::TaskResponse.new("status" => "processing")
        .with_response_headers("X-RunAPI-Task-Id" => "task-ref-1")

      expect {
        described_class.poll_until_complete(short_opts) { response }
      }.to raise_error(RunApi::Core::TaskTimeoutError) { |error|
        expect(error.details).to eq("status" => "processing")
        expect(error.runapi_task_id).to eq("task-ref-1")
        expect(error.response_headers["x-runapi-task-id"]).to eq("task-ref-1")
      }
    end

    it "normalizes uppercase status" do
      response = {"status" => "COMPLETED", "images" => [{"url" => "https://cdn.runapi.ai/public/samples/input.png"}]}

      result = described_class.poll_until_complete(options) { response }
      expect(result.dig("images", 0, "url")).to eq("https://cdn.runapi.ai/public/samples/input.png")
    end

    it "normalizes mixed case status" do
      response = {"status" => "Failed", "error" => "bad"}

      expect {
        described_class.poll_until_complete(options) { response }
      }.to raise_error(RunApi::Core::TaskFailedError)
    end

    it "raises TaskFailedError on unknown status" do
      response = {"status" => "cancelled"}

      expect {
        described_class.poll_until_complete(options) { response }
      }.to raise_error(RunApi::Core::TaskFailedError, /Unknown task status/)
    end
  end
end
