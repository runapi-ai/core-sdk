# frozen_string_literal: true

module RunApi
  module Core
    # Lightweight response model with typed field declarations and recursive coercion.
    class BaseModel
      Field = Struct.new(:name, :required, :type, :item_type, :enum, keyword_init: true)

      class << self
        def fields
          @fields ||= begin
            parent_fields = superclass.respond_to?(:fields) ? superclass.fields : {}
            parent_fields.transform_values(&:dup)
          end
        end

        def required(name, type = nil, enum: nil)
          define_field(name, type, required: true, enum: enum)
        end

        def optional(name, type = nil, enum: nil)
          define_field(name, type, required: false, enum: enum)
        end

        def from_hash(payload)
          return payload if payload.is_a?(self)

          unless payload.is_a?(Hash)
            raise TypeError, "Expected Hash for #{name}, got #{payload.class}"
          end

          new(payload)
        end

        def coerce(value, as: DynamicModel)
          target_model = resolve_type(as)

          case value
          when nil
            nil
          when BaseModel
            if target_model && target_model <= BaseModel && !value.is_a?(target_model)
              target_model.from_hash(value.to_h).with_response_headers(value.response_headers)
            else
              value
            end
          when Hash
            model = (target_model && target_model <= BaseModel) ? target_model : DynamicModel
            model.from_hash(value)
          when Array
            value.map { |item| coerce(item, as: target_model || DynamicModel) }
          else
            value
          end
        end

        private

        def define_field(name, type, required:, enum:)
          key = name.to_s

          field_type = type
          item_type = nil
          if type.is_a?(Array)
            raise ArgumentError, "Array field type must contain exactly one item type" unless type.size == 1

            field_type = Array
            item_type = type.first
          end

          fields[key] = Field.new(
            name: key,
            required: required,
            type: field_type,
            item_type: item_type,
            enum: enum
          )

          define_method(name) { @attributes[key] } unless method_defined?(name)
        end

        def resolve_type(type)
          type.respond_to?(:call) ? type.call : type
        end
      end

      def initialize(attributes = {})
        source = normalize_input(attributes)
        @attributes = {}
        @response_headers = ResponseHeaders.new

        assign_declared_fields!(source)
        assign_extra_fields!(source)
      end

      attr_reader :response_headers

      def response_header(name)
        response_headers[name]
      end

      def runapi_task_id
        response_header("X-RunAPI-Task-Id")
      end

      def with_response_headers(headers)
        @response_headers = headers.is_a?(ResponseHeaders) ? headers : ResponseHeaders.new(headers)
        self
      end

      def [](key)
        @attributes[key.to_s]
      end

      def dig(*keys)
        current = self
        keys.each do |key|
          current = case current
          when BaseModel
            current[key]
          when Hash
            current[key] || current[key.to_s] || current[key.to_sym]
          when Array
            key.is_a?(Integer) ? current[key] : nil
          end
          return nil if current.nil?
        end
        current
      end

      def to_h
        @attributes.each_with_object({}) do |(key, value), out|
          out[key] = serialize(value)
        end
      end
      alias_method :to_hash, :to_h

      def ==(other)
        case other
        when BaseModel
          to_h == other.to_h
        when Hash
          to_h == stringify_keys(other)
        else
          super
        end
      end

      private

      def assign_declared_fields!(source)
        self.class.fields.each_value do |field|
          if source.key?(field.name)
            assign_attribute(field.name, coerce_declared_value(source.delete(field.name), field))
            next
          end

          raise ValidationError, "#{field.name} is required" if field.required
        end
      end

      def assign_extra_fields!(source)
        source.each do |key, value|
          assign_attribute(key, coerce_dynamic_value(value))
          define_dynamic_reader!(key)
        end
      end

      def assign_attribute(key, value)
        @attributes[key.to_s] = value
      end

      def coerce_declared_value(value, field)
        coerced =
          if field.type == Array && value.is_a?(Array)
            value.map { |item| coerce_with_type(item, field.item_type) }
          else
            coerce_with_type(value, field.type)
          end

        validate_enum!(field, coerced)
        coerced
      end

      def coerce_with_type(value, type)
        return coerce_dynamic_value(value) if type.nil?

        resolved_type = self.class.send(:resolve_type, type)

        if resolved_type && resolved_type <= BaseModel && value.is_a?(Hash)
          return resolved_type.from_hash(value)
        end

        return coerce_dynamic_value(value) if resolved_type.nil?

        value
      end

      def validate_enum!(field, value)
        return if value.nil? || field.enum.nil?

        allowed = field.enum.respond_to?(:call) ? field.enum.call : field.enum
        return unless allowed

        invalid_value = Array(value).find do |item|
          allowed.none? { |candidate| candidate == item || candidate.to_s == item.to_s }
        end
        return unless invalid_value

        raise ValidationError, "Invalid #{field.name}: #{invalid_value}. Must be one of: #{allowed.join(", ")}"
      end

      def coerce_dynamic_value(value)
        case value
        when Hash
          DynamicModel.from_hash(value)
        when Array
          value.map { |item| coerce_dynamic_value(item) }
        else
          value
        end
      end

      def serialize(value)
        case value
        when BaseModel
          value.to_h
        when Array
          value.map { |item| serialize(item) }
        else
          value
        end
      end

      def normalize_input(attributes)
        return {} if attributes.nil?

        unless attributes.is_a?(Hash)
          raise TypeError, "Expected Hash, got #{attributes.class}"
        end

        attributes.each_with_object({}) do |(key, value), out|
          out[key.to_s] = value
        end
      end

      def stringify_keys(value)
        case value
        when Hash
          value.each_with_object({}) do |(k, v), out|
            out[k.to_s] = stringify_keys(v)
          end
        when Array
          value.map { |item| stringify_keys(item) }
        else
          value
        end
      end

      def define_dynamic_reader!(key)
        name = key.to_s
        return unless /\A[a-z_][a-zA-Z0-9_]*\z/.match?(name)
        return if respond_to?(name)

        define_singleton_method(name) { @attributes[name] }
      end
    end

    # Generic response model used when no API-specific typed model is provided.
    class DynamicModel < BaseModel
    end
  end
end
