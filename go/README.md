# RunAPI Core Go SDK

The RunAPI Core Go SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model Go modules. Install `github.com/runapi-ai/core-sdk/go` only when you are building SDK infrastructure or shared Go tooling; application code should normally install a concrete model module such as `github.com/runapi-ai/suno-sdk/go`.

## Install

```bash
go get github.com/runapi-ai/core-sdk/go@latest
```

## Notes

Use the core module for client options, common error types, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## Request identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

```go
task, err := client.TextToMusic.Create(
    context.Background(),
    suno.TextToMusicParams{Prompt: "A chill lo-fi beat"},
    option.WithHeader("X-Client-Request-Id", "order-123"),
)
```

Public API responses expose `X-RunAPI-Task-Id` when a RunAPI task exists. High-level model SDK methods return parsed response bodies; use a custom transport or direct HTTP request when your integration needs response headers.

## File Upload

```go
client, _ := nanobanana.NewClient(option.WithAPIKey("sk-your-api-key"))

upload, _ := client.Files.Create(context.Background(), files.CreateParams{
    Source: files.Source{Type: "url", URL: "https://cdn.runapi.ai/public/samples/image.jpg"},
})
fmt.Println(upload.URL)
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## License

Licensed under the Apache License, Version 2.0.
