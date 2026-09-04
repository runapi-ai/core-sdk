# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::HybridLifecycle do
  let(:http) { instance_double(RunApi::Core::HttpClient) }
  let(:resource_class) do
    Class.new do
      include RunApi::Core::ResourceHelpers

      def initialize(http)
        @http = http
      end

      public :poll_hybrid_task
    end
  end
  let(:resource) { resource_class.new(http) }

  it "rejects a task response without status" do
    response = RunApi::Core::Response.new(
      body: {"id" => "task-1"},
      headers: {"Content-Type" => "application/json"}
    )
    allow(http).to receive(:request).and_return(response)

    expect {
      resource.poll_hybrid_task(
        "/api/v1/tasks/task-1/result",
        options: RunApi::Core::RequestOptions.new,
        response_class: RunApi::Core::TaskResponse,
        subscriber: []
      )
    }.to raise_error(RunApi::Core::TaskFailedError, "Unknown task status: ")
  end
end
