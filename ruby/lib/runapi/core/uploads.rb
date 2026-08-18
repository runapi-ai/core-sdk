# frozen_string_literal: true

module RunApi
  module Core
    class Uploads
      include RunApi::Core::ResourceHelpers

      ENDPOINT = "/v1/uploads"

      class UploadObject < RunApi::Core::BaseModel
        required :id, String
        required :object, String
        required :bytes, Integer
        required :created_at, Integer
        required :filename, String
        required :purpose, String
        required :status, String
        required :expires_at, Integer
        optional :file, -> { Files::FileObject }
      end

      class UploadPart < RunApi::Core::BaseModel
        required :id, String
        required :object, String
        required :created_at, Integer
        required :upload_id, String
      end

      RESPONSE_CLASS = UploadObject

      def initialize(http)
        @http = http
      end

      def create(bytes:, filename:, mime_type:, purpose: "user_data", options: nil)
        request(:post, ENDPOINT, body: {bytes:, filename:, mime_type:, purpose:}, options:)
      end

      def add_part(upload_id, data:, file_name: nil, options: nil)
        path = file_path(data)
        body = MultipartBody.new(
          files: {data: MultipartFile.new(path:, filename: file_name || File.basename(path))}
        )
        request(:post, "#{upload_path(upload_id)}/parts", body:, options:, response_class: UploadPart)
      end

      def complete(upload_id, part_ids:, options: nil)
        request(:post, "#{upload_path(upload_id)}/complete", body: {part_ids:}, options:)
      end

      def cancel(upload_id, options: nil)
        request(:post, "#{upload_path(upload_id)}/cancel", body: {}, options:)
      end

      private

      def file_path(file)
        return file if file.is_a?(String)
        return file.path if file.respond_to?(:path)

        raise ArgumentError, "data must be a file path or respond to :path"
      end

      def upload_path(upload_id)
        raise ArgumentError, "upload_id is required" if upload_id.to_s.strip.empty?

        "#{ENDPOINT}/#{URI.encode_www_form_component(upload_id)}"
      end
    end
  end
end
