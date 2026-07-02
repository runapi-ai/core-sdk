# frozen_string_literal: true

require "digest"

module RunApi
  module Core
    class Files
      include RunApi::Core::ResourceHelpers

      ENDPOINT = "/api/v1/files"
      PREPARE_ENDPOINT = "#{ENDPOINT}/prepare"
      CONFIRM_ENDPOINT = "#{ENDPOINT}/confirm"

      class UploadResponse < RunApi::Core::BaseModel
        required :file_name, String
        required :url, String
        required :size_bytes, Integer
        required :mime_type, String
        required :created_at, String
        required :expires_at, String
      end

      RESPONSE_CLASS = UploadResponse

      def initialize(http)
        @http = http
      end

      def create(file: nil, source: nil, file_name: nil, options: nil)
        validate_source!(file:, source:)

        return upload_direct(file, file_name:, options:) if file

        request(:post, ENDPOINT, body: compact_params(source:, file_name:), options:)
      end

      private

      def validate_source!(file:, source:)
        source_count = [file, source].count { |value| !value.nil? }
        return if source_count == 1

        raise ArgumentError, "Exactly one source is required: file or source"
      end

      # Local files upload straight to storage: ask for a pre-authorized target,
      # PUT the bytes there (never through the API), then confirm. The caller still
      # makes a single create call.
      def upload_direct(file, file_name:, options:)
        path = file_path(file)
        bytes = File.binread(path)
        prepared = @http.request(
          :post,
          PREPARE_ENDPOINT,
          body: compact_params(
            filename: file_name || File.basename(path),
            byte_size: bytes.bytesize,
            checksum: Digest::MD5.base64digest(bytes)
          ),
          options:
        )

        @http.upload(prepared["upload_url"], headers: prepared["headers"], body: bytes)

        request(:post, CONFIRM_ENDPOINT, body: {signed_id: prepared["signed_id"]}, options:)
      end

      def file_path(file)
        return file if file.is_a?(String)
        return file.path if file.respond_to?(:path)

        raise ArgumentError, "file must be a file path or respond to :path"
      end
    end
  end
end
