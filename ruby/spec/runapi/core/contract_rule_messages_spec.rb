# frozen_string_literal: true

require "json"
require "spec_helper"

# Rule messages must match every other SDK (sdk/contract_rule_messages.json).
RSpec.describe "Input Contract rule messages" do
  sdk_root = File.expand_path("../../../..", __dir__)
  contract = JSON.parse(File.read(File.join(sdk_root, "contract.json")))
  cases = JSON.parse(File.read(File.join(sdk_root, "contract_rule_messages.json")))["cases"]

  let(:helper) { Class.new { include RunApi::Core::ResourceHelpers }.new }

  cases.each do |example|
    it example["name"] do
      schema = contract["actions"].fetch(example["action"])

      expect { helper.send(:validate_contract!, schema, example["params"]) }
        .to raise_error(RunApi::Core::ValidationError, example["message"])
    end
  end
end
