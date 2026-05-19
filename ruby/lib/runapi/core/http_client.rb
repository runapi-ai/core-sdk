# frozen_string_literal: true

module RunApi
  module Core
    class HttpClient
      STALE_CONNECTION_ERRORS = [ Errno::EPIPE, EOFError, IOError, OpenSSL::SSL::SSLError ].freeze

      def initialize(options)
        @options = options
        @pool = ConnectionPool.new(size: 5, timeout: 5) do
          build_connection
        end
      end

      def request(method, path, body: nil, options: nil)
        uri = URI.join(@options.base_url, path)
        req = build_request(method, uri, body, options)
        max_retries = options&.max_retries || @options.max_retries
        retries = 0
        stale_retried = false

        loop do
          response = begin
            @pool.with do |http|
              http.start unless http.started?
              http.request(req)
            end
          rescue *STALE_CONNECTION_ERRORS
            unless stale_retried
              stale_retried = true
              next
            end
            raise NetworkError, "Connection lost"
          rescue ::Net::OpenTimeout, ::Net::ReadTimeout => e
            raise TimeoutError, e.message
          rescue ::SocketError, ::Errno::ECONNREFUSED, ::Errno::ECONNRESET => e
            raise NetworkError, e.message
          end

          return parse_body(response.body) if response.is_a?(Net::HTTPSuccess)

          error = Error.from_response(response, response.body)

          if retryable?(method, response.code.to_i) && retries < max_retries
            retries += 1
            sleep(retry_delay(retries, error))
            stale_retried = false
            next
          end

          raise error
        end
      end

      private

      def build_connection
        uri = URI.parse(@options.base_url)
        http = Net::HTTP.new(uri.host, uri.port)
        http.use_ssl = (uri.scheme == "https")
        http.verify_mode = OpenSSL::SSL::VERIFY_PEER
        http.open_timeout = @options.timeout
        http.read_timeout = @options.timeout
        http
      end

      def build_request(method, uri, body, options)
        klass = Net::HTTP.const_get(method.to_s.capitalize)
        req = klass.new(uri.request_uri)

        req["Authorization"] = "Bearer #{@options.api_key}"
        req["Content-Type"] = "application/json"
        req["Accept"] = "application/json"
        req["User-Agent"] = Constants::SDK_USER_AGENT

        options&.headers&.each { |k, v| req[k.to_s] = v }

        req.body = JSON.generate(body) if body
        req
      end

      def retryable?(method, status)
        Constants::IDEMPOTENT_METHODS.include?(method.to_s.upcase) &&
          Constants::RETRYABLE_STATUS_CODES.include?(status)
      end

      def retry_delay(attempt, error)
        if error.is_a?(RateLimitError) && error.retry_after&.positive?
          return error.retry_after
        end

        base = @options.retry_base_delay * (2**(attempt - 1))
        jitter = rand * base * 0.5
        [ base + jitter, @options.retry_max_delay ].min
      end

      def parse_body(body)
        return nil if body.nil? || body.empty?

        JSON.parse(body)
      rescue JSON::ParserError
        body
      end
    end
  end
end
