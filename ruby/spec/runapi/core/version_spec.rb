# frozen_string_literal: true

require "spec_helper"

RSpec.describe "Version" do
  it "defines RunApi::Core::VERSION" do
    expect(RunApi::Core::VERSION).to match(/\A\d+\.\d+\.\d+/)
  end

  it "aliases RunApi::VERSION to Core::VERSION" do
    expect(RunApi::VERSION).to eq(RunApi::Core::VERSION)
  end
end
