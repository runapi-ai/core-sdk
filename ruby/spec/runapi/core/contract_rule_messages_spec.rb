# frozen_string_literal: true

require "json"
require "spec_helper"

# Rule messages must match every other SDK (sdk/contract_rule_messages.json).
RSpec.describe "Input Contract rule messages" do
  sdk_root = File.expand_path("../../../..", __dir__)
  fixture_path = File.join(sdk_root, "contract_rule_messages.json")

  # The shared fixture lives in the SDK monorepo; the public gem repo does not ship it.
  if File.exist?(fixture_path)
    contract = JSON.parse(File.read(File.join(sdk_root, "contract.json")))
    cases = JSON.parse(File.read(fixture_path))["cases"]

    let(:helper) { Class.new { include RunApi::Core::ResourceHelpers }.new }

    cases.each do |example|
      it example["name"] do
        schema = contract["actions"].fetch(example["action"])

        expect { helper.send(:validate_contract!, schema, example["params"]) }
          .to raise_error(RunApi::Core::ValidationError, example["message"])
      end
    end
  else
    it "runs only inside the SDK monorepo" do
      skip "shared SDK fixture not available"
    end
  end
end
