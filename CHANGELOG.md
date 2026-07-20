# Changelog

## [java/v0.2.1](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.1) - 2026-07-20

### Fixed
- Publish model-specific contract rules that reject `seed` for Wan 2.6 video requests.


## [python/v0.2.0](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.0) - 2026-07-20

### Added
- Add shared contract metadata for OpenAI TTS and Fish Audio clients.
- Add model-specific contract validation metadata for Gemini Omni Flash Preview text-to-video requests.
- Publish Gemini TTS model and input contract metadata for Provider Clients.
- Publish Seedream 5 Pro model and input contract metadata.

### Changed
- Publish shared Python and Java contract metadata for the Midjourney prompt shortening request schema.
- Publish Seedream 5-Lite output format contract metadata.
- Publish advanced stem separation mode, stem values, and conditional validation metadata.

### Fixed
- Preserve API-provided error codes, leave missing codes unset, and use SDK exception types for local failures.
- Recognize continuation request failures across HTTP 400, 409, 422, 429, and 503 responses.

## [java/v0.2.0](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.0) - 2026-07-20

### Breaking
- Replace Grok Imagine image-to-video `source_image_urls` contract metadata with scalar `source_image_url`.
  Migration: Validate and send the source image through `source_image_url`.

### Added
- Add shared contract metadata for OpenAI TTS and Fish Audio clients.
- Add OpenAI TTS and Fish Audio modules to the RunAPI BOM.
- Add model-specific contract validation metadata for Gemini Omni Flash Preview text-to-video requests.
- Publish Gemini TTS model and input contract metadata for Provider Clients.
- Publish Seedream 5 Pro model and input contract metadata.

### Changed
- Publish shared Python and Java contract metadata for the Midjourney prompt shortening request schema.
- Publish Seedream 5-Lite output format contract metadata.
- Publish advanced stem separation mode, stem values, and conditional validation metadata.

### Fixed
- Preserve API-provided error codes, leave missing codes unset, and use SDK exception types for local failures.
- Recognize continuation request failures across HTTP 400, 409, 422, 429, and 503 responses.

## [go/v0.2.13](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.13) - 2026-07-20

### Fixed
- Classify HTTP 413 responses as validation errors with a stable default message.
- Preserve API-provided error codes, leave missing codes unset, and use SDK exception types for local failures.
- Recognize continuation request failures across HTTP 400, 409, 422, 429, and 503 responses.

## [js/v0.2.13](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.13), [ruby/v0.2.13](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.13) - 2026-07-20

### Fixed
- Preserve API-provided error codes, leave missing codes unset, and use SDK exception types for local failures.
- Recognize continuation request failures across HTTP 400, 409, 422, 429, and 503 responses.


## [python/v0.1.6](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.6), [java/v0.1.7](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.7) - 2026-07-17

### Changed
- Publish shared Python and Java SDK contract metadata for Grok Imagine Video 1.5 Fast.

## [js/v0.2.12](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.12), [ruby/v0.2.12](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.12), [go/v0.2.12](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.12), [python/v0.1.5](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.5), [java/v0.1.6](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.6) - 2026-07-17

### Changed
- Add Midjourney request contract metadata across the JavaScript, Ruby, Go, Python, and Java SDKs.

## [js/v0.2.11](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.11), [ruby/v0.2.11](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.11), [go/v0.2.11](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.11), [python/v0.1.4](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.4), [java/v0.1.5](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.5) - 2026-07-16

### Changed
- Add Kling V3 Turbo text-to-video and image-to-video contract metadata to the Python and Java core SDKs.
- Include generated validation rules for the new Kling V3 Turbo variants.
- Publish shared SDK contract validation updates for rule ordering, functional action fallbacks, and stricter integer and length constraints.

## [js/v0.2.10](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.10), [ruby/v0.2.10](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.10), [go/v0.2.10](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.10), [python/v0.1.3](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.3), [java/v0.1.4](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.4) - 2026-07-08

### Changed
- Refresh shared SDK contract validation for updated model constraints.

## [js/v0.2.9](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.9), [ruby/v0.2.9](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.9), [go/v0.2.9](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.9), [python/v0.1.2](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.2), [java/v0.1.3](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.3) - 2026-07-07

### Changed
- Refresh RunAPI contract metadata for Nano Banana 2 Lite.
- Publish js/v0.2.9, ruby/v0.2.9, go/v0.2.9, python/v0.1.2, and java/v0.1.3.

## [js/v0.2.7](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.7), [js/v0.2.8](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.8), [ruby/v0.2.7](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.7), [ruby/v0.2.8](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.8), [go/v0.2.7](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.7), [go/v0.2.8](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.8), [python/v0.1.1](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.1), [java/v0.1.2](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.2) - 2026-07-02

### Changed
- Request validation is now generated from the RunAPI request contract, keeping client-side checks in sync with the API surface.

## [java/v0.1.1](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.1) - 2026-06-25

### Fixed
- Fixed Java retry handling for Retry-After response headers.
- Fixed Java contract validation for action-level conditional rules.
- Refreshed Java SDK metadata for v0.1.1.

## [java/v0.1.0](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.1.0) - 2026-06-24

### Added
- Publish `ai.runapi:runapi-core` and `ai.runapi:runapi-bom` for Java SDK consumers.
- Include Java 8-compatible bytecode, sources, and Javadocs.

## [js/v0.2.6](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.6), [ruby/v0.2.6](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.6), [go/v0.2.6](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.6), [python/v0.1.0](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.1.0) - 2026-06-18

### Highlights
- Per-method documentation across all resources (godoc, JSDoc, YARD)
- File upload and account available as universal client resources

## [js/v0.2.5](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.5), [ruby/v0.2.5](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.5), [go/v0.2.5](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.5) - 2026-06-01

### Changed
- Align SDK with upstream Input Contract and public API vocabulary changes
- Update endpoint definitions and field constraints

## [js/v0.2.4](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.4), [ruby/v0.2.4](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.4), [go/v0.2.4](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.4) - 2026-05-22

### Changed
- Publish JavaScript, Ruby, and Go core SDK artifacts with per-language GitHub release tags.
- Refresh public README metadata and package metadata.

## [v0.2.3](https://github.com/runapi-ai/core-sdk/releases/tag/v0.2.3) - 2026-05-22

### Changed
- Publish core-sdk v0.2.3 with refreshed README header, package metadata, and current SDK source.

## [v0.2.2](https://github.com/runapi-ai/core-sdk/releases/tag/v0.2.2) - 2026-05-22

### Changed
- Publish core-sdk v0.2.2 with refreshed README header, package metadata, and current SDK source.

## [v0.2.1](https://github.com/runapi-ai/core-sdk/releases/tag/v0.2.1) - 2026-05-19

Initial release.
