# frozen_string_literal: true

require "spec_helper"

RSpec.describe RunApi::Core::Account do
  let(:http) { instance_double(RunApi::Core::HttpClient) }
  let(:account) { described_class.new(http) }

  describe "#info" do
    it "GETs the account info endpoint" do
      expect(http).to receive(:request)
        .with(:get, "/api/v1/me")
        .and_return(
          "id" => 1,
          "name" => "test",
          "email" => "developer@runapi.ai",
          "account" => {"id" => 2, "name" => "acme"}
        )

      result = account.info
      expect(result).to be_a(RunApi::Core::Account::InfoResponse)
      expect(result.email).to eq("developer@runapi.ai")
      expect(result.account.name).to eq("acme")
    end
  end

  describe "#balance" do
    it "GETs the balance endpoint with all fidelity fields" do
      expect(http).to receive(:request)
        .with(:get, "/api/v1/me/balance")
        .and_return(
          "balance_cents" => 5000,
          "paid_balance_cents" => 4000,
          "bonus_balance_cents" => 1000,
          "spent_cents_today" => 100,
          "spent_cents_total" => 2000
        )

      result = account.balance
      expect(result).to be_a(RunApi::Core::Account::BalanceResponse)
      expect(result.balance_cents).to eq(5000)
      expect(result.paid_balance_cents).to eq(4000)
      expect(result.bonus_balance_cents).to eq(1000)
    end
  end
end
