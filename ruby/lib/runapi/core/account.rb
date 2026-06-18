# frozen_string_literal: true

module RunApi
  module Core
    class Account
      include RunApi::Core::ResourceHelpers

      INFO_ENDPOINT = "/api/v1/me"
      BALANCE_ENDPOINT = "/api/v1/me/balance"

      class AccountRecord < RunApi::Core::BaseModel
        required :id, Integer
        required :name, String
      end

      class InfoResponse < RunApi::Core::BaseModel
        required :id, Integer
        required :name, String
        required :email, String
        required :account, AccountRecord
      end

      class BalanceResponse < RunApi::Core::BaseModel
        required :balance_cents, Integer
        required :paid_balance_cents, Integer
        required :bonus_balance_cents, Integer
        required :spent_cents_today, Integer
        required :spent_cents_total, Integer
      end

      def initialize(http)
        @http = http
      end

      def info(options: nil)
        request(:get, INFO_ENDPOINT, options:, response_class: InfoResponse)
      end

      def balance(options: nil)
        request(:get, BALANCE_ENDPOINT, options:, response_class: BalanceResponse)
      end
    end
  end
end
