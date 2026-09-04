# frozen_string_literal: true

module RunApi
  module Core
    class ResponseHeaders
      include Enumerable

      def initialize(headers = {})
        @headers = {}
        headers&.each { |key, value| @headers[normalize(key)] = value }
      end

      def [](key)
        @headers[normalize(key)]
      end

      def fetch(key, *fallback, &block)
        @headers.fetch(normalize(key), *fallback, &block)
      end

      def key?(key)
        @headers.key?(normalize(key))
      end

      def each(&block)
        @headers.each(&block)
      end

      def empty?
        @headers.empty?
      end

      def to_h
        @headers.dup
      end

      private

      def normalize(key)
        key.to_s.downcase
      end
    end

    class Response < Hash
      attr_reader :response_headers, :status

      def initialize(body:, headers: nil, status: nil)
        super()
        @body = body unless body.is_a?(Hash)
        @response_headers = headers.is_a?(ResponseHeaders) ? headers : ResponseHeaders.new(headers)
        @status = status
        update(body) if body.is_a?(Hash)
      end

      alias_method :headers, :response_headers

      def body
        @body.nil? ? self : @body
      end

      def [](key)
        return @body[key] if @body.respond_to?(:[])

        super
      end

      def dig(*keys)
        return @body.dig(*keys) if @body.respond_to?(:dig)

        super
      end

      def to_h
        return @body.to_h if !@body.nil? && @body.respond_to?(:to_h)

        super
      end

      def ==(other)
        if @body
          @body == (other.is_a?(Response) ? other.body : other)
        else
          super(other.is_a?(Response) ? other.to_h : other)
        end
      end
    end
  end
end
