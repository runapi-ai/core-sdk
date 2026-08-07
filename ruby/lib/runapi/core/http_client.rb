# frozen_string_literal: true

module RunApi
  module Core
    class HttpClient
      STALE_CONNECTION_ERRORS = [Errno::EPIPE, EOFError, IOError, OpenSSL::SSL::SSLError].freeze

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

          if response.is_a?(Net::HTTPNotModified) && options&.allow_not_modified
            return Response.new(body: {"not_modified" => true}, headers: response_headers(response))
          end

          if response.is_a?(Net::HTTPSuccess)
            body = parse_body(response.body)
            return nil if body.nil?
            return body unless body.is_a?(Hash) || body.is_a?(Array)

            return Response.new(body:, headers: response_headers(response))
          end

          error = Error.from_response(response, response.body)

          if retryable?(method, response.code.to_i) && retries < max_retries
            retries += 1
            sleep(retry_delay(retries, error))
            stale_retried = false
            next
          end

          raise error
        end
      ensure
        close_multipart_files(req)
      end

      def close
        @pool.shutdown do |http|
          http.finish if http.started?
        end
      end

      # PUT bytes straight to a pre-authorized upload URL with the exact headers
      # issued for it. Skips the base URL, auth, and retries: the URL is single-use
      # and the body is not safe to replay.
      def upload(url, headers:, body:)
        uri = URI.parse(url)
        http = Net::HTTP.new(uri.host, uri.port)
        http.use_ssl = (uri.scheme == "https")
        http.open_timeout = @options.timeout
        http.read_timeout = @options.timeout

        req = Net::HTTP::Put.new(uri.request_uri)
        headers.each { |key, value| req[key.to_s] = value }
        req.body = body

        response = http.start { |connection| connection.request(req) }
        return if response.is_a?(Net::HTTPSuccess)

        raise Error.from_response(response, response.body)
      rescue ::Net::OpenTimeout, ::Net::ReadTimeout => e
        raise TimeoutError, e.message
      rescue ::SocketError, ::Errno::ECONNREFUSED, ::Errno::ECONNRESET => e
        raise NetworkError, e.message
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

        req["Authorization"] = "Bearer #{@options.api_key}" if @options.api_key
        req["Accept"] = "application/json"
        req["User-Agent"] = Constants::SDK_USER_AGENT

        options&.headers&.each { |k, v| req[k.to_s] = v }

        if body.is_a?(MultipartBody)
          req.set_form(multipart_parts(body), "multipart/form-data")
        elsif body
          req["Content-Type"] = "application/json"
          req.body = JSON.generate(body)
        end
        req
      end

      def multipart_parts(body)
        opened_files = []
        field_parts = body.fields.flat_map do |key, value|
          Array(value).map { |item| [key, item.to_s] }
        end
        file_parts = body.files.map do |key, file|
          options = {filename: file.filename}
          options[:content_type] = file.content_type if file.content_type
          opened_files << File.open(file.path, "rb")
          [key, opened_files.last, options]
        end
        field_parts + file_parts
      rescue
        opened_files.each { |file| file.close unless file.closed? }
        raise
      end

      def close_multipart_files(request)
        body_data = request&.instance_variable_get(:@body_data)
        return unless body_data

        body_data.each do |part|
          file = part[1]
          file.close if file.is_a?(File) && !file.closed?
        end
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
        [base + jitter, @options.retry_max_delay].min
      end

      def parse_body(body)
        return nil if body.nil? || body.empty?

        JSON.parse(body)
      rescue JSON::ParserError
        body
      end

      def response_headers(response)
        headers = {}
        response.each_header { |key, value| headers[key] = value }
        headers
      end
    end
  end
end
