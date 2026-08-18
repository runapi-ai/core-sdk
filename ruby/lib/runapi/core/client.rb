# frozen_string_literal: true

module RunApi
  module Core
    # Base class for every RunAPI client. Resolves the API key, builds the shared
    # HTTP client, and exposes the Universal Resources (Files, Uploads, account, pricing) that
    # are available on any client regardless of which model gem was required.
    #
    # Provider clients inherit from this and build their model resources from the
    # protected +http+ reader.
    class Client
      # @return [Files] Persistent File lifecycle and temporary URL upload operations.
      attr_reader :files
      # @return [Account] Account info and balance operations.
      attr_reader :account
      # @return [Pricing] Live Price Schedule lookup and Price Quote operations.
      attr_reader :pricing
      # @return [Uploads] Multipart Upload lifecycle operations.
      attr_reader :uploads

      def initialize(api_key: nil, **options)
        @api_key = Core::Auth.resolve_api_key(api_key)
        client_options = Core::ClientOptions.new(api_key: @api_key, **options)
        @owns_http_client = client_options.http_client.nil?
        @http = client_options.http_client || Core::HttpClient.new(client_options)
        @files = Files.new(@http)
        @account = Account.new(@http)
        @pricing = Pricing.new(@http)
        @uploads = Uploads.new(@http)
      end

      # Closes the SDK-created HTTP client. Injected clients remain caller-owned.
      def close
        @http.close if @owns_http_client
      end

      protected

      attr_reader :http
    end
  end
end
