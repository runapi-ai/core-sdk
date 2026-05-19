# frozen_string_literal: true

module RunApi
  module Core
    module Polling
      ACTIVE_STATUSES = %w[pending processing].freeze

      def self.poll_until_complete(options = PollingOptions.new)
        deadline = Process.clock_gettime(Process::CLOCK_MONOTONIC) + options.max_wait

        loop do
          response = yield
          status = value_for(response, "status").to_s.downcase

          return response if status == "completed"

          if status == "failed"
            message = value_for(response, "error") || "Task failed"
            raise TaskFailedError.new(message, details: details_for(response))
          end

          if Process.clock_gettime(Process::CLOCK_MONOTONIC) >= deadline
            raise TaskTimeoutError, "Task polling timed out after #{options.max_wait}s"
          end

          unless ACTIVE_STATUSES.include?(status)
            raise TaskFailedError.new("Unknown task status: #{status}", details: details_for(response))
          end

          sleep(options.poll_interval)
        end
      end

      def self.value_for(response, key)
        case response
        when Core::BaseModel
          response[key]
        when Hash
          response[key] || response[key.to_sym]
        end
      end
      private_class_method :value_for

      def self.details_for(response)
        response.is_a?(Core::BaseModel) ? response.to_h : response
      end
      private_class_method :details_for
    end
  end
end
