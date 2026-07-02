# RunAPI Core Ruby SDK

The RunAPI Core Ruby SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model gems. Install `runapi-core` only when you are building SDK infrastructure or shared Ruby tooling; application code should normally install a concrete model gem such as `runapi-suno`.

## Install

```bash
gem install runapi-core
```

## Notes

Use the core gem for common client options, error classes, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## Request Identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

High-level Ruby model SDK methods currently return parsed response bodies. When an integration needs to send a client request id or read `X-RunAPI-Task-Id`, make the call through direct HTTP or a custom transport so response headers stay available.

```ruby
require "json"
require "net/http"
require "uri"

uri = URI("https://runapi.ai/api/v1/suno/text_to_music")
request = Net::HTTP::Post.new(uri)
request["Authorization"] = "Bearer #{ENV.fetch("RUNAPI_API_KEY")}"
request["Content-Type"] = "application/json"
request["X-Client-Request-Id"] = "order-123"
request.body = JSON.generate({
  prompt: "A chill lo-fi beat",
  model: "suno-v4.5-plus",
  vocal_mode: "instrumental"
})

response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: true) { |http| http.request(request) }
runapi_task_id = response["X-RunAPI-Task-Id"]
body = JSON.parse(response.body)
```

## File Upload

```ruby
client = RunApi::NanoBanana::Client.new(api_key: ENV["RUNAPI_API_KEY"])

upload = client.files.create(source: {type: "url", url: "https://cdn.runapi.ai/public/samples/image.jpg"})
puts upload.url
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## License

Licensed under the Apache License, Version 2.0.
