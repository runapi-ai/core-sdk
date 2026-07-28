# frozen_string_literal: true

module RunApi
  module Core
    # HTTP methods supported by the SDK.
    HTTP_METHODS = %i[get post put patch delete head options].freeze

    # Task status values returned by async operations.
    TASK_STATUSES = %w[pending processing completed failed].freeze

    # Status values for async task results (excludes 'pending').
    ASYNC_TASK_STATUSES = %w[processing completed failed].freeze

    # Configuration options for API clients.
    #
    # @example
    #   options = ClientOptions.new(
    #     api_key: "your-api-key",
    #     base_url: "https://runapi.ai",
    #     timeout: 60,
    #     max_retries: 3
    #   )
    #
    # @!attribute [rw] api_key
    #   @return [String, nil] API key for authenticated resources and protected Price Quotes.
    # @!attribute [rw] base_url
    #   @return [String] Base URL for API requests. Defaults to RunApi.base_url.
    # @!attribute [rw] timeout
    #   @return [Integer] Request timeout in seconds. Defaults to 900 (15 minutes).
    # @!attribute [rw] max_retries
    #   @return [Integer] Maximum number of retry attempts. Defaults to 2.
    # @!attribute [rw] retry_base_delay
    #   @return [Float] Base delay between retries in seconds. Defaults to 0.5.
    # @!attribute [rw] retry_max_delay
    #   @return [Float] Maximum delay between retries in seconds. Defaults to 5.0.
    # @!attribute [rw] http_client
    #   @return [Object, nil] Custom HTTP transport object. Must respond to
    #     `#request(method, path, body:, options:)` with the same interface as {HttpClient}.
    #     When set, the SDK skips building its own {HttpClient} and delegates all HTTP calls
    #     to this object.
    ClientOptions = Struct.new(
      :api_key,
      :base_url,
      :timeout,
      :max_retries,
      :retry_base_delay,
      :retry_max_delay,
      :http_client,
      keyword_init: true
    ) do
      def initialize(**kwargs)
        super
        self.base_url ||= RunApi.base_url
        self.timeout ||= Constants::TIMEOUTS[:http_request]
        self.max_retries ||= Constants::RETRY_CONFIG[:max_retries]
        self.retry_base_delay ||= Constants::RETRY_CONFIG[:base_delay]
        self.retry_max_delay ||= Constants::RETRY_CONFIG[:max_delay]
      end
    end

    # Per-request options that override client-level defaults.
    #
    # @example
    #   client.text_to_image.run(
    #     prompt: "A sunset",
    #     model: "z-image",
    #     aspect_ratio: "1:1",
    #     options: RequestOptions.new(timeout: 30, headers: { "X-Custom" => "value" })
    #   )
    #
    # @!attribute [rw] headers
    #   @return [Hash<String, String>, nil] Additional HTTP headers. Merged with client-level headers.
    # @!attribute [rw] timeout
    #   @return [Integer, nil] Request timeout in seconds. Overrides client-level timeout.
    # @!attribute [rw] max_retries
    #   @return [Integer, nil] Maximum retry attempts. Overrides client-level max_retries.
    RequestOptions = Struct.new(
      :headers,
      :timeout,
      :max_retries,
      :allow_not_modified,
      keyword_init: true
    )

    # Options for polling async task completion.
    # Used internally by resource `run` methods.
    #
    # @!attribute [rw] poll_interval
    #   @return [Integer] Polling interval in seconds. Defaults to 2.
    # @!attribute [rw] max_wait
    #   @return [Integer] Maximum wait time in seconds. Defaults to 900 (15 minutes).
    PollingOptions = Struct.new(
      :poll_interval,
      :max_wait,
      keyword_init: true
    ) do
      def initialize(**kwargs)
        super
        self.poll_interval ||= Constants::TIMEOUTS[:polling_interval]
        self.max_wait ||= Constants::TIMEOUTS[:polling_max_wait]
      end
    end

    class TaskReservation < BaseModel
      required :amount_cents, Numeric
    end

    class TaskSettlement < BaseModel
      required :charged_amount_cents, Numeric
      required :amount_micro_cents, Numeric
    end

    class TaskRefund < BaseModel
      required :refunded_at, String
    end

    class TaskBillingFacts < BaseModel
      optional :reservation, TaskReservation
      optional :settlement, TaskSettlement
      optional :refund, TaskRefund
    end

    # Typed response structure for async task operations.
    # Additional API-specific fields are preserved and exposed via dot notation.
    #
    # @!attribute [r] id
    #   @return [String, nil] Task ID for tracking and retrieval.
    # @!attribute [r] status
    #   @return [String, nil] Current task status.
    # @!attribute [r] error
    #   @return [String, nil] Error message if task failed.
    class TaskResponse < BaseModel
      module Status
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

        ALL = [PENDING, PROCESSING, COMPLETED, FAILED].freeze
      end

      optional :id, String
      optional :status, String
      optional :error, String
      optional :billing, TaskBillingFacts
    end
  end
end
