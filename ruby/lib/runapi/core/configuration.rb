# frozen_string_literal: true

module RunApi
  class << self
    attr_accessor :api_key, :base_url

    def configure
      yield self
    end
  end

  self.base_url = Core::Constants::DEFAULT_BASE_URL
end
