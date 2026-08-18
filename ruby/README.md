# RunAPI Core Ruby SDK

The RunAPI Core Ruby SDK provides shared authentication, HTTP, retry, error, Files, Uploads, and polling primitives for RunAPI model gems. Install `runapi-core` only when you are building SDK infrastructure or shared Ruby tooling; application code should normally install a concrete model gem such as `runapi-suno`.

## Install

```bash
gem install runapi-core
```

## Notes

Use the core gem for common client options, error classes, request helpers, and task polling behavior that Provider Clients share. Public SDK docs live at https://runapi.ai/docs/resources/sdks and the model catalog lives at https://runapi.ai/models.

## Live Pricing

Every Provider Client exposes `pricing`. Schedule lookup and quotes use the live API response and do not retain a local price cache.

```ruby
schedules = client.pricing.list(service: "suno")
quote = client.pricing.quote(
  service: "suno",
  action: "convert_audio",
  params: {}
)
```

Public schedule lookup and quotes that use only public parameters work without an API key. Pass a standard API key when a quote references an account-owned source Task.

Use `PricingClient` when pricing is the only capability needed:

```ruby
require "runapi/core"

pricing = RunApi::Core::PricingClient.new
schedules = pricing.list(service: "suno")
```

## Request Identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

Task-creation calls also accept an optional opaque `Idempotency-Key` up to 512 characters. Generate one value per logical task and reuse it only with identical input after an unknown result. Reusing the value with different input returns `409 Conflict`; do not derive it from `X-Client-Request-Id`.

High-level Ruby Provider Client resource methods accept per-request options and keep response headers on the returned model object. This example uses the Suno Provider Client; install `runapi-suno` to run it.

```ruby
require "runapi/suno"

client = RunApi::Suno::Client.new(api_key: ENV.fetch("RUNAPI_API_KEY"))
options = RunApi::Core::RequestOptions.new(
  headers: {
    "X-Client-Request-Id" => "order-123",
    "Idempotency-Key" => "opaque-logical-task-123"
  }
)

response = client.text_to_music.create(
  prompt: "A chill lo-fi beat",
  model: "suno-v4.5-plus",
  vocal_mode: "instrumental",
  options: options
)

runapi_task_id = response.runapi_task_id
# Equivalent case-insensitive lookup:
runapi_task_id = response.response_headers["X-RunAPI-Task-Id"]
```

## Temporary File Upload

```ruby
client = RunApi::NanoBanana::Client.new(api_key: ENV["RUNAPI_API_KEY"])

upload = client.files.create(source: {type: "url", url: "https://cdn.runapi.ai/public/samples/image.jpg"})
puts upload.url
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## Persistent Files And Multipart Uploads

The existing `files.create` method above keeps its temporary URL behavior. Use `create_file` for a persistent File object and `uploads` when sending one or more Parts:

```ruby
file = client.files.create_file(file: "./knowledge.pdf")
content = client.files.content(file.id)

upload = client.uploads.create(
  bytes: 1_048_576,
  filename: "archive.bin",
  mime_type: "application/octet-stream"
)
part = client.uploads.add_part(upload.id, data: "./archive.part-01")
completed = client.uploads.complete(upload.id, part_ids: [part.id])
```

Use `files.list`, `retrieve`, and `delete_file` for the remaining File lifecycle. See https://runapi.ai/docs/resources/files for limits and REST examples.

## License

Licensed under the Apache License, Version 2.0.
