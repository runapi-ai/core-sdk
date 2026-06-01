# frozen_string_literal: true

require "time"

module RunApi
  module Core
    # Base error class for all RunAPI SDK errors.
    # Includes HTTP status, request ID, and response details.
    class Error < StandardError
      # @return [Integer, nil] HTTP status code if available.
      attr_reader :status
      # @return [String, nil] Request ID from response headers.
      attr_reader :request_id
      # @return [Hash, String, nil] Parsed response body or error details.
      attr_reader :details

      def initialize(message = nil, status: nil, request_id: nil, details: nil)
        super(message)
        @status = status
        @request_id = request_id
        @details = details
      end

      def to_h
        {
          error: self.class.name,
          message: message,
          status: status,
          request_id: request_id,
          details: details
        }.compact
      end

      STATUS_MAP = {
        400 => "ValidationError",
        401 => "AuthenticationError",
        402 => "InsufficientCreditsError",
        404 => "NotFoundError",
        409 => "ConflictError",
        422 => "ValidationError",
        429 => "RateLimitError",
        500 => "ServerError",
        501 => "ServerError",
        502 => "ServerError",
        503 => "ServiceUnavailableError",
        504 => "ServerError",
        505 => "ServerError"
      }.freeze

      DEFAULT_MESSAGES = {
        400 => "Bad request",
        401 => "Unauthorized",
        402 => "Insufficient credits",
        404 => "Not found",
        408 => "Request timeout",
        409 => "Conflict",
        413 => "Payload too large",
        415 => "Unsupported media type",
        422 => "Validation failed",
        429 => "Too many requests",
        503 => "Service unavailable"
      }.freeze

      class << self
        # Constructs appropriate error class from HTTP response.
        # Maps status codes to specific error types and extracts error messages.
        #
        # @param response [Net::HTTPResponse] HTTP response object
        # @param body [String, nil] Response body as string
        # @return [Error] Specific error instance based on status code
        def from_response(response, body = nil)
          status = response.code.to_i
          request_id = response["x-request-id"]

          parsed_body = parse_body(body)
          message = extract_message(parsed_body) ||
            DEFAULT_MESSAGES[status] ||
            "Request failed"

          retry_after = parse_retry_after(response["retry-after"])

          error_class_name = STATUS_MAP[status]
          error_class = if error_class_name
            Core.const_get(error_class_name)
          else
            Error
          end

          kwargs = {
            status: status,
            request_id: request_id,
            details: parsed_body
          }
          kwargs[:retry_after] = retry_after if error_class == RateLimitError

          error_class.new(message, **kwargs)
        end

        private

        def parse_body(body)
          return nil if body.to_s.empty?
          return extract_html_error(body) if body.match?(/<!doctype|<html/i)

          JSON.parse(body)
        rescue JSON::ParserError
          body
        end

        def extract_html_error(html)
          title = html[%r{<title>(.*?)</title>}mi, 1]
          h1 = html[%r{<h1>(.*?)</h1>}mi, 1]

          error_text = title || h1 || "HTML Error Page"

          error_text = error_text.gsub(/&[a-z]+;/i, " ")
            .gsub(/<[^>]+>/, "")
            .strip

          {
            "error" => error_text,
            "is_html_error" => true,
            "message" => "Server returned HTML error page: #{error_text}"
          }
        end

        def extract_message(body)
          return nil unless body.is_a?(Hash)

          (body["error"].is_a?(Hash) ? body.dig("error", "message") : body["error"]) ||
            body.dig("errors", 0) ||
            body["message"] ||
            body["detail"] ||
            body["errorMessage"] ||
            body["msg"]
        end

        def parse_retry_after(value)
          return nil if value.nil?

          numeric = Float(value, exception: false)
          return numeric if numeric

          begin
            Time.httpdate(value) - Time.now.utc
          rescue ArgumentError
            nil
          end
        end
      end
    end

    # Raised when API key is missing or invalid (HTTP 401).
    class AuthenticationError < Error
      def initialize(message = "Unauthorized", **kwargs)
        super(message, status: 401, **kwargs)
      end
    end

    # Raised when rate limit is exceeded (HTTP 429). Includes retry-after delay.
    class RateLimitError < Error
      # @return [Numeric, nil] Suggested retry delay in seconds from Retry-After header.
      attr_reader :retry_after

      def initialize(message = "Too many requests", retry_after: nil, **kwargs)
        super(message, status: 429, **kwargs)
        @retry_after = retry_after
      end
    end

    # Raised when account has insufficient credits (HTTP 402).
    class InsufficientCreditsError < Error
      def initialize(message = "Insufficient credits", **kwargs)
        super(message, status: 402, **kwargs)
      end
    end

    # Raised when requested resource does not exist (HTTP 404).
    class NotFoundError < Error
      def initialize(message = "Not found", **kwargs)
        super(message, status: 404, **kwargs)
      end
    end

    # Raised when request validation fails (HTTP 400, 422).
    class ValidationError < Error
      def initialize(message = "Validation failed", **kwargs)
        super
      end
    end

    # Raised when service is temporarily unavailable (HTTP 503).
    class ServiceUnavailableError < Error
      def initialize(message = "Service unavailable", **kwargs)
        super(message, status: kwargs.delete(:status) || 503, **kwargs)
      end
    end

    # Raised when network connection fails or request cannot be sent.
    class NetworkError < Error
      def initialize(message = "Network error", **kwargs)
        super
      end
    end

    # Raised when HTTP request exceeds configured timeout.
    class TimeoutError < Error
      def initialize(message = "Request timed out", **kwargs)
        super
      end
    end

    # Raised when polling for task completion exceeds maximum wait time.
    class TaskTimeoutError < Error
      def initialize(message = "Task polling timed out", **kwargs)
        super
      end
    end

    # Raised when async task fails during processing.
    class TaskFailedError < Error
      def initialize(message = "Task failed", **kwargs)
        super
      end
    end

    # Raised when request conflicts with current resource state (HTTP 409).
    class ConflictError < Error
      def initialize(message = "Conflict", **kwargs)
        super(message, status: 409, **kwargs)
      end
    end

    # Raised when server encounters an internal error (HTTP 5xx).
    class ServerError < Error
      def initialize(message = "Server error", **kwargs)
        super(message, status: kwargs.delete(:status) || 500, **kwargs)
      end
    end
  end
end
