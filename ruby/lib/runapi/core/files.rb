# frozen_string_literal: true

require "digest"

module RunApi
  module Core
    class Files
      include RunApi::Core::ResourceHelpers

      ENDPOINT = "/api/v1/files"
      PREPARE_ENDPOINT = "#{ENDPOINT}/prepare"
      CONFIRM_ENDPOINT = "#{ENDPOINT}/confirm"
      PROTOCOL_ENDPOINT = "/v1/files"

      class UploadResponse < RunApi::Core::BaseModel
        required :file_name, String
        required :url, String
        required :size_bytes, Integer
        required :mime_type, String
        required :created_at, String
        required :expires_at, String
      end

      class FileObject < RunApi::Core::BaseModel
        required :id, String
        required :object, String
        required :bytes, Integer
        required :created_at, Integer
        optional :expires_at, Integer
        required :filename, String
        required :purpose, String
      end

      class FileList < RunApi::Core::BaseModel
        required :object, String
        required :data, [FileObject]
        optional :first_id, String
        optional :last_id, String
        required :has_more
      end

      class DeletedFile < RunApi::Core::BaseModel
        required :id, String
        required :object, String
        required :deleted
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

      def create_file(file:, purpose: "user_data", file_name: nil, options: nil)
        path = file_path(file)
        body = MultipartBody.new(
          fields: {purpose:},
          files: {file: MultipartFile.new(path:, filename: file_name || File.basename(path))}
        )
        request(:post, PROTOCOL_ENDPOINT, body:, options:, response_class: FileObject)
      end

      def list(after_id: nil, limit: nil, order: nil, purpose: nil, options: nil)
        query = URI.encode_www_form(compact_params(after: after_id, limit:, order:, purpose:))
        path = query.empty? ? PROTOCOL_ENDPOINT : "#{PROTOCOL_ENDPOINT}?#{query}"
        request(:get, path, options:, response_class: FileList)
      end

      def retrieve(file_id, options: nil)
        request(:get, protocol_file_path(file_id), options:, response_class: FileObject)
      end

      def content(file_id, options: nil)
        @http.request(:get, "#{protocol_file_path(file_id)}/content", options:, raw: true)
      end

      def delete_file(file_id, options: nil)
        request(:delete, protocol_file_path(file_id), options:, response_class: DeletedFile)
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

      def protocol_file_path(file_id)
        raise ArgumentError, "file_id is required" if file_id.to_s.strip.empty?

        "#{PROTOCOL_ENDPOINT}/#{URI.encode_www_form_component(file_id)}"
      end
    end
  end
end
