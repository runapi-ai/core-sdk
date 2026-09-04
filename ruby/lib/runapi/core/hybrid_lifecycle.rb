# frozen_string_literal: true

module RunApi
  module Core
    module HybridLifecycle
      StoredHttpResponse = Struct.new(:status, :headers) do
        def code = status.to_s
        def [](name) = headers[name]
        def each_header(&block) = headers.each(&block)
      end

      private

      def run_hybrid(path, body:, options:, response_class: default_response_class)
        terminal = nil
        subscribe_hybrid(path, body:, options:, response_class:).each { |result| terminal = result }
        terminal
      end

      def subscribe_hybrid(path, body:, options:, response_class: default_response_class)
        options = hybrid_request_options(options)
        Enumerator.new do |subscriber|
          response = raw_request(:post, path, body:, options:)
          unless response.status == 202
            terminal = decode_hybrid_response(response, response_class)
            subscriber << terminal
            next terminal
          end

          location = response.response_headers["Location"]
          raise Core::TaskFailedError, "Accepted task response is missing Location" if location.to_s.empty?

          poll_hybrid_task(location, options:, response_class:, subscriber:)
        end
      end

      def raw_request(method, path, body: :__runapi_no_body__, options: nil)
        response = if body == :__runapi_no_body__
          options ? @http.request(method, path, options:) : @http.request(method, path)
        else
          kwargs = {body: body}
          kwargs[:options] = options if options
          @http.request(method, path, **kwargs)
        end

        return response if response.is_a?(Core::Response)

        Core::Response.new(body: response, status: 200)
      end

      def hybrid_request_options(options)
        headers = options&.headers&.dup || {}
        return options if headers.keys.any? { |key| key.to_s.casecmp?("Idempotency-Key") }

        headers["Idempotency-Key"] = SecureRandom.uuid
        Core::RequestOptions.new(
          headers:,
          timeout: options&.timeout,
          max_retries: options&.max_retries,
          allow_not_modified: options&.allow_not_modified
        )
      end

      def poll_hybrid_task(location, options:, response_class:, subscriber:)
        loop do
          response = raw_request(:get, location, options:)
          payload = response.body
          status = hybrid_task_status(payload)

          if status == "completed"
            terminal = decode_hybrid_response(stored_hybrid_response(payload, response), response_class)
            subscriber << terminal
            break terminal
          end
          raise stored_hybrid_error(payload, response) if status == "failed"

          unless Core::Polling::ACTIVE_STATUSES.include?(status)
            raise_task_failed(payload, response, "Unknown task status: #{status}")
          end

          subscriber << decode_processing_response(response)
          sleep retry_after(response)
        end
      end

      def hybrid_task_status(payload)
        case payload
        when Core::BaseModel
          payload.status.to_s.downcase
        when Hash
          (payload["status"] || payload[:status]).to_s.downcase
        else
          ""
        end
      end

      def decode_processing_response(response)
        result = Core::BaseModel.coerce(response.body, as: Core::TaskResponse)
        attach_response_headers(result, response.response_headers)
        result
      end

      def decode_hybrid_response(response, response_class)
        return response.body unless json_response?(response)

        result = Core::BaseModel.coerce(response.body, as: response_class)
        attach_response_headers(result, response.response_headers)
        result
      end

      def stored_hybrid_response(payload, polling_response)
        envelope = payload.is_a?(Core::BaseModel) ? payload.to_h : payload
        stored = envelope.is_a?(Hash) ? (envelope["response"] || envelope[:response]) : nil
        unless stored.is_a?(Hash)
          raise_task_failed(payload, polling_response, "Terminal Task Result is missing response")
        end

        status = stored["status"] || stored[:status]
        content_type = stored["content_type"] || stored[:content_type]
        unless status.is_a?(Integer) && content_type.is_a?(String) && !content_type.empty?
          raise_task_failed(payload, polling_response, "Terminal Task Result response is invalid")
        end

        headers = (stored["headers"] || stored[:headers] || {}).to_h
        headers = headers.merge("Content-Type" => content_type)
        Core::Response.new(body: stored.key?("body") ? stored["body"] : stored[:body], headers:, status:)
      end

      def stored_hybrid_error(payload, polling_response)
        response = stored_hybrid_response(payload, polling_response)
        serialized_body = response.body.is_a?(String) ? response.body : JSON.generate(response.body)
        Core::Error.from_response(StoredHttpResponse.new(response.status, response.response_headers), serialized_body)
      end

      def json_response?(response)
        response.response_headers["Content-Type"].to_s.downcase.include?("json") || response.body.is_a?(Hash) || response.body.is_a?(Array)
      end

      def retry_after(response)
        value = Float(response.response_headers["Retry-After"], exception: false)
        value&.positive? ? value : 0
      end

      def raise_task_failed(payload, response, message = nil)
        raise Core::TaskFailedError.new(
          message || hybrid_task_error(payload) || "Task failed",
          details: payload,
          response_headers: response.response_headers
        )
      end

      def hybrid_task_error(payload)
        case payload
        when Core::BaseModel
          payload.error
        when Hash
          payload["error"] || payload[:error]
        end
      end

      def attach_response_headers(result, headers)
        case result
        when Core::BaseModel
          result.with_response_headers(headers)
        when Array
          result.each { |item| attach_response_headers(item, headers) }
        end
      end
    end
  end
end
