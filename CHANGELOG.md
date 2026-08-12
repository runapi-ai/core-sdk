# Changelog

## [java/v0.4.1](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.4.1) - 2026-08-12

### Added
- Export the Seedream layer decomposition request contract for model SDK validation.
- Add shared contract constraints for Seedance 2.5 requests.

### Fixed
- Apply the shared Runway aspect_ratio and first_frame_image_url conditional rules in Java request validation.
- Use the Resource error summary while retaining field validation details, Structured Errors, and terminal Task failures.
- Reject enable_safety_checker for Hailuo 02 Pro image-to-video and Wan 2.7 video edit requests.

## [js/v0.3.5](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.5), [ruby/v0.3.5](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.5), [go/v0.2.20](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.20) - 2026-08-12

### Fixed
- Use the Resource error summary while retaining field validation details, Structured Errors, and terminal Task failures.

## [python/v0.5.1](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.5.1) - 2026-08-12

### Added
- Export the Seedream layer decomposition request contract for model SDK validation.
- Add shared contract constraints for Seedance 2.5 requests.

### Fixed
- Use the Resource error summary while retaining field validation details, Structured Errors, and terminal Task failures.


## [python/v0.5.0](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.5.0) - 2026-08-10

### Added
- Add shared contract constraints for Suno music inspiration requests.

### Changed
- Update generated Seedream 5 Lite output quality constraints.

## [java/v0.4.0](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.4.0) - 2026-08-10

### Breaking
- Reject OmniHuman audio-to-video prompts over 300 characters before sending the request.
  Migration: Upgrade the Java package and shorten OmniHuman audio-to-video prompts to 300 characters or fewer.

### Added
- Add shared contract constraints for Suno music inspiration requests.

### Changed
- Update generated Seedream 5 Lite output quality constraints.

## [js/v0.3.4](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.4), [ruby/v0.3.4](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.4) - 2026-08-10

### Changed
- Update generated Seedream 5 Lite output quality constraints.


## [java/v0.3.0](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.3.0) - 2026-08-07

### Added
- Validate the optional multi_shots field for supported WAN 2.6 video requests.
- Preserve repeated multipart form fields used by audio transcription requests.
- Add generated MiniMax H3 input contract metadata.
- Add shared request validation metadata for Qwen 3 image endpoints.
- Add Fish Audio s2.1-pro and MP3 or WAV output constraints to shared contract metadata.

### Changed
- Update generated Grok Imagine Preview resolution and reference image constraints.

### Fixed
- Validate the 10 to 360 second custom duration range and reject controls that the selected vocal mode or model cannot honor.

## [ruby/v0.3.3](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.3) - 2026-08-07

### Added
- Preserve repeated multipart form fields used by audio transcription requests.
- Add Fish Audio s2.1-pro and MP3 or WAV output constraints to shared contract metadata.

### Changed
- Update generated Grok Imagine Preview resolution and reference image constraints.

## [go/v0.2.19](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.19) - 2026-08-07

### Added
- Preserve repeated multipart form fields used by audio transcription requests.
- Add Fish Audio s2.1-pro and MP3 or WAV output constraints to shared contract metadata.

## [python/v0.4.0](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.4.0) - 2026-08-07

### Added
- Preserve repeated multipart form fields used by audio transcription requests.
- Add generated MiniMax H3 input contract metadata.
- Add shared request validation metadata for Qwen 3 image endpoints.
- Add Fish Audio s2.1-pro and MP3 or WAV output constraints to shared contract metadata.

### Changed
- Update generated Grok Imagine Preview resolution and reference image constraints.

## [js/v0.3.3](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.3) - 2026-08-07

### Added
- Add Fish Audio s2.1-pro and MP3 or WAV output constraints to shared contract metadata.

### Changed
- Update generated Grok Imagine Preview resolution and reference image constraints.


## [python/v0.3.6](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.6), [java/v0.2.12](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.12) - 2026-08-06

### Added
- Register the stitching, remastering, and sampling actions in shared contract metadata.

### Fixed
- Validate the optional PixVerse enable_audio field for text-to-video and image-to-video requests.

## [js/v0.3.2](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.2) - 2026-08-06

### Fixed
- Allow token Price Schedules to omit the flat unit price field.
- Validate the optional PixVerse enable_audio field for text-to-video and image-to-video requests.

## [ruby/v0.3.2](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.2), [go/v0.2.18](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.18) - 2026-08-06

### Fixed
- Validate the optional PixVerse enable_audio field for text-to-video and image-to-video requests.


## [python/v0.3.5](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.5), [java/v0.2.11](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.11) - 2026-08-04

### Added
- Register the five PixVerse V6 video actions in shared contract metadata.


## [python/v0.3.4](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.4), [java/v0.2.10](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.10) - 2026-07-31

### Added
- Expose generic cache-write prices separately from TTL-specific cache-write prices.

### Removed
- Remove seedance-v1-lite from shared Seedance contract metadata.
  Migration: Use seedance-v1-pro or another supported Seedance model.

## [js/v0.3.1](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.1), [ruby/v0.3.1](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.1), [go/v0.2.17](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.17) - 2026-07-31

### Added
- Expose generic cache-write prices separately from TTL-specific cache-write prices.


## [python/v0.3.3](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.3), [java/v0.2.9](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.9) - 2026-07-29

### Removed
- Remove seedance-v1-lite from shared Seedance contract metadata.
  Migration: Use seedance-v1-pro or another supported Seedance model.


## [python/v0.3.2](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.2) - 2026-07-28

### Changed
- Describe and validate the documented Gemini Omni, Grok Imagine, and Topaz request fields.

### Fixed
- Carry supported Wan Flash image-to-video duration values in generated contract metadata; request defaults remain API-applied.

## [java/v0.2.8](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.8) - 2026-07-28

### Changed
- Describe and validate the documented Gemini Omni, Grok Imagine, and Topaz request fields.

### Fixed
- Validate required audio and music request fields before sending requests.
- Carry supported Wan Flash image-to-video duration values in generated contract metadata; request defaults remain API-applied.


## [java/v0.2.7](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.7) - 2026-07-28

### Added
- Expose live Price Schedule, Price Quote, and typed Task Billing Facts through every Provider Client.
- Add generated contract metadata required by Kling O1 reference-media validation.
- Expose whether an async create response reused an idempotent task.

### Changed
- Support generated Flux 2 Max request validation metadata used by Flux 2 SDK packages.

## [go/v0.2.16](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.16) - 2026-07-28

### Added
- Add public Pricing resources and persisted task billing facts.
- Expose whether an async create response reused an idempotent task.

## [js/v0.3.0](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.3.0), [ruby/v0.3.0](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.3.0) - 2026-07-28

### Added
- Add the universal Pricing Resource and typed Task Billing Facts to JavaScript and Ruby core SDKs.

## [python/v0.3.1](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.1) - 2026-07-28

### Added
- Add generated contract metadata required by Kling O1 reference-media validation.

### Changed
- Support generated Flux 2 Max request validation metadata used by Flux 2 SDK packages.


## [python/v0.3.0](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.3.0) - 2026-07-24

### Added
- Add shared Files, Account, and Pricing resources plus typed Task Billing Facts to every Python Provider Client.

## [ruby/v0.2.16](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.16) - 2026-07-24

### Added
- Add Client#close to release SDK-owned HTTP connections.

### Fixed
- Allow Ruby applications to keep connection_pool 3.x while retaining compatibility with connection_pool 2.x.


## [python/v0.2.5](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.5), [java/v0.2.6](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.6) - 2026-07-23

### Added
- Add generated Python and Java contract metadata required by Kling 2.6 motion-control validation.


## [java/v0.2.5](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.5) - 2026-07-23

### Added
- Add Kling V3 Omni text-to-video and image-to-video constraints to shared contract metadata.
- Add generated validation metadata for seven additional Producer FUZZ music generation versions.
- Add generated contract metadata required by the Kling video continuation resource.

### Fixed
- Restore the generated method boundary required for the Java core contract metadata to compile.
- Keep generated Java contract metadata aligned with the current aggregate API contract.
- Restore valid generated method partitioning after concurrent catalog merges.

## [js/v0.2.15](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.15), [ruby/v0.2.15](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.15) - 2026-07-23

### Added
- Add Kling V3 Omni text-to-video and image-to-video constraints to shared contract metadata.
- Add generated contract metadata required by the Kling video continuation resource.

## [python/v0.2.4](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.4) - 2026-07-23

### Added
- Add Kling V3 Omni text-to-video and image-to-video constraints to shared contract metadata.
- Add generated validation metadata for seven additional Producer FUZZ music generation versions.
- Add generated contract metadata required by the Kling video continuation resource.


## [python/v0.2.3](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.3) - 2026-07-22

### Added
- Add Kling 2.6 text-to-video and image-to-video constraints to shared contract metadata.
- Add generated validation metadata for Midjourney first-video extension requests.
- Add generated validation metadata for Flux text-to-image and remix-image requests.
- Publish Veo 3.1 Lite model and input constraints in aggregate contract metadata.
- Add shared request validation metadata for Qwen Image generation, remix, and edit endpoints.

## [java/v0.2.4](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.4) - 2026-07-22

### Added
- Add Kling 2.6 text-to-video and image-to-video constraints to shared contract metadata.
- Add generated validation metadata for Midjourney first-video extension requests.
- Add generated validation metadata for Flux text-to-image and remix-image requests.
- Publish Veo 3.1 Lite model and input constraints in aggregate contract metadata.
- Add shared request validation metadata for Qwen Image generation, remix, and edit endpoints.

### Changed
- Maintenance release with no public API changes; refresh generated Java contract source partitioning.

## [go/v0.2.15](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.15) - 2026-07-22

### Fixed
- Apply generated numeric conditional rules consistently in Go request validation.


## [java/v0.2.3](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.3) - 2026-07-21

### Added
- Add the optional Fish Audio references field to shared Java contract metadata.
- Add generated validation metadata for lyrics generation and lyric blending requests.

### Changed
- Publish Seedance 1.5 Pro and V1 Pro Fast seed constraints in aggregate contract metadata.

## [python/v0.2.2](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.2) - 2026-07-21

### Added
- Add generated validation metadata for lyrics generation and lyric blending requests.


## [js/v0.2.14](https://github.com/runapi-ai/core-sdk/releases/tag/js%2Fv0.2.14), [ruby/v0.2.14](https://github.com/runapi-ai/core-sdk/releases/tag/ruby%2Fv0.2.14), [go/v0.2.14](https://github.com/runapi-ai/core-sdk/releases/tag/go%2Fv0.2.14) - 2026-07-20

### Changed
- Validate array types and generated minimum and maximum item counts before sending requests.

## [python/v0.2.1](https://github.com/runapi-ai/core-sdk/releases/tag/python%2Fv0.2.1), [java/v0.2.2](https://github.com/runapi-ai/core-sdk/releases/tag/java%2Fv0.2.2) - 2026-07-20

### Added
- Publish shared Python and Java SDK contract metadata for the Producer text-to-music request schema.

### Changed
- Validate array types and generated minimum and maximum item counts before sending requests.


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
