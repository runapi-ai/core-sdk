# frozen_string_literal: true

module RunApi
  module Core
    # API key resolution helpers.
    module Auth
      ENV_VAR_NAME = "RUNAPI_API_KEY"

      MISSING_KEY_MESSAGE = "API key is required. Pass api_key or set the RUNAPI_API_KEY environment variable."

      # Resolve the API key from (in priority order):
      #   1. the explicit argument
      #   2. RunApi.api_key (global configuration)
      #   3. the RUNAPI_API_KEY environment variable
      #
      # All sources are trimmed; blank values are treated as missing.
      # Raises {RunApi::Core::AuthenticationError} when no source yields a value.
      #
      # @param explicit [String, nil] API key passed directly to a client constructor.
      # @return [String] the resolved API key
      def self.resolve_api_key(explicit = nil)
        resolved = resolve_optional_api_key(explicit)

        raise AuthenticationError, MISSING_KEY_MESSAGE unless resolved

        resolved
      end

      # Resolve an API key when present without requiring one for public resources.
      def self.resolve_optional_api_key(explicit = nil)
        normalize(explicit) ||
          normalize(RunApi.respond_to?(:api_key) ? RunApi.api_key : nil) ||
          normalize(ENV[ENV_VAR_NAME])
      end

      def self.normalize(value)
        return nil unless value.is_a?(String)

        trimmed = value.strip
        trimmed.empty? ? nil : trimmed
      end
      private_class_method :normalize
    end
  end
end
