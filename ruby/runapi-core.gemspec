# frozen_string_literal: true

Dir.chdir(__dir__) do
  require_relative "lib/runapi/core/version"

  Gem::Specification.new do |spec|
    spec.name = "runapi-core"
    spec.version = RunApi::Core::VERSION
    spec.authors = [ "RunAPI" ]
    spec.email = [ "contact@runapi.ai" ]

    spec.summary = "Shared SDK primitives for RunAPI JavaScript, Ruby, and Go SDKs."
    spec.description = "RunAPI core SDK for JavaScript, Ruby, and Go"
    spec.homepage = "https://runapi.ai/docs#runapi-sdks"
    spec.license = "Apache-2.0"
    spec.required_ruby_version = ">= 3.1.0"

    spec.metadata["homepage_uri"] = "https://runapi.ai/docs#runapi-sdks"
    spec.metadata["documentation_uri"] = "https://runapi.ai/docs#runapi-sdks"
    spec.metadata["source_code_uri"] = "https://github.com/runapi-ai/core-sdk"
    spec.metadata["changelog_uri"] = "https://github.com/runapi-ai/core-sdk/blob/main/CHANGELOG.md"

    spec.files = Dir.glob("lib/**/*") + %w[LICENSE]
    spec.require_paths = [ "lib" ]

    spec.add_dependency "connection_pool", "~> 2.4"
  end
end
