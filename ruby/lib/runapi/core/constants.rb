# frozen_string_literal: true

module RunApi
  module Core
    module Constants
      TIMEOUTS = {
        http_request: 900,
        polling_interval: 2,
        polling_max_wait: 900
      }.freeze

      RETRY_CONFIG = {
        max_retries: 2,
        base_delay: 0.5,
        max_delay: 5.0
      }.freeze

      DEFAULT_BASE_URL = "https://runapi.ai"

      SDK_USER_AGENT = "runapi-sdk-ruby/#{RunApi::VERSION}".freeze

      IDEMPOTENT_METHODS = %w[GET HEAD PUT DELETE OPTIONS].freeze

      RETRYABLE_STATUS_CODES = [ 429, 500, 502, 503, 504 ].freeze
    end
  end
end
