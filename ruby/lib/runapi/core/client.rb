# frozen_string_literal: true

module RunApi
  module Core
    # Base class for every RunAPI client. Resolves the API key, builds the shared
    # HTTP client, and exposes the Universal Resources (file upload, account) that
    # are available on any client regardless of which model gem was required.
    #
    # Provider clients inherit from this and build their model resources from the
    # protected +http+ reader.
    class Client
      # @return [Files] Temporary file upload operations.
      attr_reader :files
      # @return [Account] Account info and balance operations.
      attr_reader :account

      def initialize(api_key: nil, **options)
        @api_key = Core::Auth.resolve_api_key(api_key)
        client_options = Core::ClientOptions.new(api_key: @api_key, **options)
        @owns_http_client = client_options.http_client.nil?
        @http = client_options.http_client || Core::HttpClient.new(client_options)
        @files = Files.new(@http)
        @account = Account.new(@http)
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
