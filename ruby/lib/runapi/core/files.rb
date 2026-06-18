# frozen_string_literal: true

module RunApi
  module Core
    class Files
      include RunApi::Core::ResourceHelpers

      ENDPOINT = "/api/v1/files"

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

        body = if file
          multipart_body(file, file_name:)
        else
          compact_params(source:, file_name:)
        end

        request(:post, ENDPOINT, body:, options:)
      end

      private

      def validate_source!(file:, source:)
        source_count = [file, source].count { |value| !value.nil? }
        return if source_count == 1

        raise ArgumentError, "Exactly one source is required: file or source"
      end

      def multipart_body(file, file_name:)
        path = file_path(file)
        filename = file_name || File.basename(path)
        Core::MultipartBody.new(
          fields: compact_params(file_name: file_name),
          files: {
            file: Core::MultipartFile.new(path:, filename:)
          }
        )
      end

      def file_path(file)
        return file if file.is_a?(String)
        return file.path if file.respond_to?(:path)

        raise ArgumentError, "file must be a file path or respond to :path"
      end
    end
  end
end
