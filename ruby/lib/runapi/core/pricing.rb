# frozen_string_literal: true

module RunApi
  module Core
    class Pricing
      include RunApi::Core::ResourceHelpers

      SCHEDULES_ENDPOINT = "/api/v1/price_schedules"
      QUOTES_ENDPOINT = "/api/v1/price_quotes"

      class Schedule < RunApi::Core::BaseModel
        required :service, String
        required :action, String
        optional :model, String
        required :pricing_status, String
        required :catalog_status, String
        required :currency, String
        required :billing_unit, String
        required :billing_strategy, String
        optional :unit_price_cents, Numeric
        optional :input_price_per_1m_cents, Numeric
        optional :output_price_per_1m_cents, Numeric
        optional :cache_read_price_per_1m_cents, Numeric
        optional :cache_write_5m_price_per_1m_cents, Numeric
        optional :cache_write_1h_price_per_1m_cents, Numeric
        required :billing_config, Hash
      end

      class ScheduleListResponse < RunApi::Core::BaseModel
        required :as_of, String
        required :price_schedules, [Schedule]
      end

      class ScheduleNotModifiedResponse < RunApi::Core::BaseModel
        required :not_modified, TrueClass
      end

      class QuoteResponse < RunApi::Core::BaseModel
        required :service, String
        required :action, String
        optional :model, String
        required :pricing_status, String
        required :currency, String
        required :reservation_amount_cents, Numeric
        required :estimate_basis, String
        required :as_of, String
      end

      class QuoteEnvelope < RunApi::Core::BaseModel
        required :price_quote, QuoteResponse
      end

      def initialize(http)
        @http = http
      end

      def list(service: nil, action: nil, model: nil, options: nil)
        query = URI.encode_www_form(compact_params(service:, action:, model:))
        path = query.empty? ? SCHEDULES_ENDPOINT : "#{SCHEDULES_ENDPOINT}?#{query}"
        request_options = (options || RequestOptions.new).dup
        request_options.allow_not_modified = true
        response = @http.request(:get, path, options: request_options)
        payload = response.is_a?(Core::Response) ? response.body : response
        response_class = payload["not_modified"] ? ScheduleNotModifiedResponse : ScheduleListResponse
        result = RunApi::Core::BaseModel.coerce(payload, as: response_class)
        result.with_response_headers(response.response_headers) if response.is_a?(Core::Response)
        result
      end

      def quote(service:, action:, model: nil, params: {}, options: nil)
        response = request(
          :post,
          QUOTES_ENDPOINT,
          body: compact_params(service:, action:, model:, params:),
          options:,
          response_class: QuoteEnvelope
        )
        response.price_quote
      end
    end

    # Standalone live Pricing client with optional API authentication.
    class PricingClient < Pricing
      def initialize(api_key: nil, **options)
        client_options = Core::ClientOptions.new(
          api_key: Core::Auth.resolve_optional_api_key(api_key),
          **options
        )
        @owns_http_client = client_options.http_client.nil?
        super(client_options.http_client || Core::HttpClient.new(client_options))
      end

      # Closes the SDK-created HTTP client. Injected clients remain caller-owned.
      def close
        @http.close if @owns_http_client
      end
    end
  end
end
