# frozen_string_literal: true

require "securerandom"
require_relative "hybrid_lifecycle"

module RunApi
  module Core
    module ResourceHelpers
      include HybridLifecycle

      private

      # Performs an HTTP request and coerces JSON responses into typed model objects.
      # Keeps existing request signatures so current stubs and custom transports keep working.
      def request(method, path, body: :__runapi_no_body__, options: nil, response_class: default_response_class)
        response = if body == :__runapi_no_body__
          if options
            @http.request(method, path, options: options)
          else
            @http.request(method, path)
          end
        else
          kwargs = {body: body}
          kwargs[:options] = options if options
          @http.request(method, path, **kwargs)
        end

        payload = response.is_a?(Core::Response) ? response.body : response
        result = Core::BaseModel.coerce(payload, as: response_class)
        attach_response_headers(result, response.response_headers) if response.is_a?(Core::Response)
        result
      end

      def compact_params(params)
        params.reject { |_, v| v.nil? || (v.is_a?(String) && v.strip.empty?) }
      end

      def param(params, key)
        return params[key] if params.key?(key)
        params[key.to_s] if params.key?(key.to_s)
      end

      def default_response_class
        if self.class.const_defined?(:RESPONSE_CLASS, false)
          self.class::RESPONSE_CLASS
        else
          Core::TaskResponse
        end
      end

      # Run polling and, once the task reports `completed`, re-coerce the payload
      # into the resource's narrowed response class (when defined). This lets
      # `run()` callers rely on result fields being present without a nil check.
      def poll_until_complete(polling_opts = Core::PollingOptions.new, &block)
        response = Core::Polling.poll_until_complete(polling_opts, &block)
        return response unless self.class.const_defined?(:COMPLETED_RESPONSE_CLASS, false)

        completed_class = self.class::COMPLETED_RESPONSE_CLASS
        return response if response.is_a?(completed_class)

        payload = response.is_a?(Core::BaseModel) ? response.to_h : response
        completed = completed_class.from_hash(payload)
        completed.with_response_headers(response.response_headers) if response.is_a?(Core::BaseModel)
        completed
      end
    end
  end
end
