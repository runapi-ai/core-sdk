# frozen_string_literal: true

module RunApi
  module Core
    MultipartFile = Struct.new(:path, :filename, :content_type, keyword_init: true)

    class MultipartBody
      attr_reader :fields, :files

      def initialize(fields: {}, files: {})
        @fields = stringify_keys(fields)
        @files = stringify_keys(files)
      end

      private

      def stringify_keys(hash)
        hash.each_with_object({}) do |(key, value), result|
          result[key.to_s] = value
        end
      end
    end
  end
end
