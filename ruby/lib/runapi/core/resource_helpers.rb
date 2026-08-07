# frozen_string_literal: true

module RunApi
  module Core
    module ResourceHelpers
      private

      # Performs an HTTP request and coerces JSON responses into typed model objects.
      # Keeps existing request signatures so current stubs and custom transports keep working.
      def request(method, path, body: :__runapi_no_body__, options: nil, response_class: default_response_class)
        response = if body == :__runapi_no_body__
          if options
            @http.request(method, path, options: options)
          else
            @http.request(method, path)
          end
        else
          kwargs = {body: body}
          kwargs[:options] = options if options
          @http.request(method, path, **kwargs)
        end

        payload = response.is_a?(Core::Response) ? response.body : response
        result = Core::BaseModel.coerce(payload, as: response_class)
        attach_response_headers(result, response.response_headers) if response.is_a?(Core::Response)
        result
      end

      def compact_params(params)
        params.reject { |_, v| v.nil? || (v.is_a?(String) && v.strip.empty?) }
      end

      def param(params, key)
        return params[key] if params.key?(key)
        params[key.to_s] if params.key?(key.to_s)
      end

      def validate_optional!(params, key, allowed)
        value = param(params, key)
        return unless value

        unless allowed.include?(value)
          raise Core::ValidationError, "Invalid #{key}: #{value}. Must be one of: #{allowed.join(", ")}"
        end
      end

      # ---- Contract validation ------------------------------------------
      # Validates request params against the generated contract: model
      # membership, then declared cross-field rules, then per-field
      # required/enum/integer/min/max/length. `schema` is one action entry from the generated
      # per-package CONTRACT (CONTRACT["<action>"]).

      def validate_contract!(schema, params)
        model = param_value(params, "model")
        models = schema["models"] || []
        if models.empty?
          fields = schema.dig("fields_by_model", "_") || {}
        else
          unless models.include?(model)
            raise Core::ValidationError, "model must be one of: #{models.sort.join(", ")}"
          end

          fields = schema.dig("fields_by_model", model) || {}
        end

        Array(schema["rules"]).each { |rule| enforce_contract_rule!(params, rule) }
        fields.each do |field, rules|
          validate_schema_field!(params, field, rules)
        end
      end

      def validate_schema_field!(params, field, rules)
        value = param_value(params, field)
        if !value.nil? && (rules.key?("min_items") || rules.key?("max_items"))
          validate_schema_item_count!(field, value, rules)
        end

        present = field_present?(params, field)
        raise Core::ValidationError, "#{field} is required" if rules["required"] && !present
        return unless present

        if (enum = rules["enum"]) && !enum_value_allowed?(enum, value)
          raise Core::ValidationError, "#{field} must be one of: #{enum.join(", ")}"
        end

        validate_schema_integer!(field, value, rules) if rules["type"] == "integer"
        validate_schema_range!(field, value, rules) if rules.key?("min") || rules.key?("max")
      end

      def validate_schema_item_count!(field, value, rules)
        raise Core::ValidationError, "#{field} must be an array" unless value.is_a?(Array)

        min = rules["min_items"]
        max = rules["max_items"]
        return if (min.nil? || value.size >= min) && (max.nil? || value.size <= max)

        raise Core::ValidationError, item_count_message(field, min, max)
      end

      def item_count_message(field, min, max)
        if min && max
          "#{field} must contain between #{min} and #{max} items"
        elsif min
          "#{field} must contain at least #{min} items"
        else
          "#{field} must contain at most #{max} items"
        end
      end

      # Mirrors GatewayEntry#validate_schema_integer!: a type: integer field
      # rejects non-integer numbers (e.g. 11.5), which min/max alone admit.
      def validate_schema_integer!(field, value, rules)
        return if value.is_a?(Integer)

        min = rules["min"]
        max = rules["max"]
        detail = (min && max) ? " between #{min} and #{max}" : ""
        raise Core::ValidationError, "#{field} must be an integer#{detail}"
      end

      def validate_schema_range!(field, value, rules)
        if rules["length"]
          measured = value.to_s.length
          unit = "characters"
        else
          raise Core::ValidationError, "#{field} must be a number" unless value.is_a?(Numeric)

          measured = value
          unit = nil
        end

        min = rules["min"]
        max = rules["max"]
        return if (min.nil? || measured >= min) && (max.nil? || measured <= max)

        raise Core::ValidationError, schema_range_message(field, min, max, unit)
      end

      def schema_range_message(field, min, max, unit)
        suffix = unit ? " #{unit}" : ""
        if min && max
          "#{field} must be between #{min} and #{max}#{suffix}"
        elsif min
          "#{field} must be at least #{min}#{suffix}"
        else
          "#{field} must be at most #{max}#{suffix}"
        end
      end

      def enum_value_allowed?(enum, value)
        enum.any? do |allowed|
          if allowed == true || allowed == false
            value == allowed
          elsif allowed.is_a?(Numeric)
            value.is_a?(Numeric) && value == allowed
          elsif value.is_a?(Numeric)
            allowed == value
          else
            allowed.to_s == value.to_s
          end
        end
      end

      def enforce_contract_rule!(params, rule)
        conditions = rule["when"] || {}
        return unless conditions.all? { |field, condition| rule_condition_met?(params, field, condition) }

        context = conditions.map { |field, condition| rule_condition_label(field, condition) }.join(" and ")
        qualifier = context.empty? ? "" : " when #{context}"

        Array(rule["required"]).each do |field|
          next if field_present?(params, field)

          raise Core::ValidationError, "#{field} is required#{qualifier}"
        end

        required_any = Array(rule["required_any"])
        if required_any.any? && required_any.none? { |field| field_present?(params, field) }
          raise Core::ValidationError, "one of #{required_any.join(", ")} is required#{qualifier}"
        end

        Array(rule["forbidden"]).each do |field|
          next unless field_present?(params, field)

          raise Core::ValidationError, "#{field} is not allowed#{qualifier}"
        end

        (rule["enum"] || {}).each do |field, allowed|
          next unless field_present?(params, field)

          value = param_value(params, field)
          next if Array(allowed).any? { |candidate| candidate.to_s == value.to_s }

          raise Core::ValidationError, "#{field} must be one of: #{Array(allowed).join(", ")}#{qualifier}"
        end
      end

      # A `when` entry is either `{present: true|false}` or a scalar the
      # supplied value must equal. Rules never resolve declared defaults.
      def rule_condition_met?(params, field, condition)
        if condition.is_a?(Hash) && (condition.key?("present") || condition.key?(:present))
          expected = condition["present"].nil? ? condition[:present] : condition["present"]
          return field_present?(params, field) == (expected == true)
        end
        return false unless param_key?(params, field)

        param_value(params, field).to_s == condition.to_s
      end

      def rule_condition_label(field, condition)
        if condition.is_a?(Hash) && (condition.key?("present") || condition.key?(:present))
          expected = condition["present"].nil? ? condition[:present] : condition["present"]
          return (expected == true) ? "#{field} is present" : "#{field} is absent"
        end

        "#{field} is #{condition}"
      end

      def field_present?(params, field)
        return false unless param_key?(params, field)

        value = param_value(params, field)
        case value
        when false then true
        when Array then value.any? { |item| present_value?(item) }
        else present_value?(value)
        end
      end

      def param_key?(params, field)
        params.key?(field.to_sym) || params.key?(field.to_s)
      end

      # Indifferent value lookup for a string-or-symbol field across params that
      # may be keyed either way.
      def param_value(params, field)
        if params.key?(field.to_sym)
          params[field.to_sym]
        elsif params.key?(field.to_s)
          params[field.to_s]
        end
      end

      def present_value?(value)
        case value
        when nil, false then false
        when true then true
        when String then !value.strip.empty?
        when Array, Hash then !value.empty?
        else true
        end
      end

      def default_response_class
        if self.class.const_defined?(:RESPONSE_CLASS, false)
          self.class::RESPONSE_CLASS
        else
          Core::TaskResponse
        end
      end

      # Run polling and, once the task reports `completed`, re-coerce the payload
      # into the resource's narrowed response class (when defined). This lets
      # `run()` callers rely on result fields being present without a nil check.
      def poll_until_complete(polling_opts = Core::PollingOptions.new, &block)
        response = Core::Polling.poll_until_complete(polling_opts, &block)
        return response unless self.class.const_defined?(:COMPLETED_RESPONSE_CLASS, false)

        completed_class = self.class::COMPLETED_RESPONSE_CLASS
        return response if response.is_a?(completed_class)

        payload = response.is_a?(Core::BaseModel) ? response.to_h : response
        completed = completed_class.from_hash(payload)
        completed.with_response_headers(response.response_headers) if response.is_a?(Core::BaseModel)
        completed
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
