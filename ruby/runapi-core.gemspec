# frozen_string_literal: true

Dir.chdir(__dir__) do
  require_relative "lib/runapi/core/version"

  Gem::Specification.new do |spec|
    spec.name = "runapi-core"
    spec.version = RunApi::Core::VERSION
    spec.metadata["runapi_slug"] = "core"
    spec.authors = ["RunAPI"]
    spec.email = ["contact@runapi.ai"]

    spec.summary = "RunAPI Core Ruby SDK"
    spec.description = "The RunAPI Core Ruby SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model gems. Install `runapi-core` only when you are building SDK infrastructure or shared Ruby tooling; application code should normally install a concrete model gem such as `runapi-suno`."
    spec.homepage = "https://runapi.ai/models"
    spec.license = "Apache-2.0"
    spec.required_ruby_version = ">= 3.1.0"
    spec.metadata["homepage_uri"] = "https://runapi.ai/models"
    spec.metadata["documentation_uri"] = "https://github.com/runapi-ai/core-sdk/blob/main/ruby/README.md"
    spec.metadata["source_code_uri"] = "https://github.com/runapi-ai/core-sdk"
    spec.metadata["bug_tracker_uri"] = "https://github.com/runapi-ai/core-sdk/issues"
    spec.metadata["changelog_uri"] = "https://github.com/runapi-ai/core-sdk/blob/main/CHANGELOG.md"


    spec.files = Dir.glob("lib/**/*") + %w[LICENSE README.md]
    spec.extra_rdoc_files = ["README.md"]
        spec.require_paths = ["lib"]

    spec.add_dependency "connection_pool", "~> 2.4"
  end
end
