# frozen_string_literal: true

module RunApi
  module Core
    module ResourceHelpers
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

        Core::BaseModel.coerce(response, as: response_class)
      end

      def compact_params(params)
        params.reject { |_, v| v.nil? || (v.is_a?(String) && v.strip.empty?) }
      end

      def param(params, key)
        return params[key] if params.key?(key)
        params[key.to_s] if params.key?(key.to_s)
      end

      def validate_optional!(params, key, allowed)
        value = param(params, key)
        return unless value

        unless allowed.include?(value)
          raise Core::ValidationError, "Invalid #{key}: #{value}. Must be one of: #{allowed.join(", ")}"
        end
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
        completed_class.from_hash(payload)
      end
    end
  end
end
