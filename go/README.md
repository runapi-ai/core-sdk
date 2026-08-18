# RunAPI Core Go SDK

The RunAPI Core Go SDK provides shared authentication, HTTP, retry, error, Files, Uploads, and polling primitives for RunAPI model Go modules. Install `github.com/runapi-ai/core-sdk/go` only when you are building SDK infrastructure or shared Go tooling; application code should normally install a concrete model module such as `github.com/runapi-ai/suno-sdk/go`.

## Install

```bash
go get github.com/runapi-ai/core-sdk/go@latest
```

## Notes

Use the core module for client options, common error types, request helpers, and task polling behavior shared across Go Provider Client modules. Public SDK docs live at https://runapi.ai/docs/resources/sdks and the model catalog lives at https://runapi.ai/models.

## Request identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

Task-creation calls also accept an optional opaque `Idempotency-Key` up to 512 characters. Generate one value per logical task and reuse it only with identical input after an unknown result. Reusing the value with different input returns `409 Conflict`; do not derive it from `X-Client-Request-Id`.

```go
task, err := client.TextToMusic.Create(
    context.Background(),
    suno.TextToMusicParams{Prompt: "A chill lo-fi beat"},
    option.WithHeader("X-Client-Request-Id", "order-123"),
    option.WithHeader("Idempotency-Key", "opaque-logical-task-123"),
)
```

Public API responses expose `X-RunAPI-Task-Id` when a RunAPI task exists. High-level Go Provider Client resource methods return parsed response bodies; use a custom transport or direct HTTP request when your integration needs raw response headers.

## Temporary File Upload

```go
client, _ := nanobanana.NewClient(option.WithAPIKey("sk-your-api-key"))

upload, _ := client.Files.Create(context.Background(), files.CreateParams{
    Source: files.Source{Type: "url", URL: "https://cdn.runapi.ai/public/samples/image.jpg"},
})
fmt.Println(upload.URL)
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## Persistent Files And Multipart Uploads

The existing `Files.Create` method above keeps its temporary URL behavior. Use `CreateFile` for a persistent File object and `Uploads` when sending one or more Parts:

```go
file, _ := client.Files.CreateFile(context.Background(), files.ProtocolCreateParams{
    File: "./knowledge.pdf",
})
content, _ := client.Files.Content(context.Background(), file.ID)

upload, _ := client.Uploads.Create(context.Background(), uploads.CreateParams{
    Bytes: 1048576, Filename: "archive.bin", MIMEType: "application/octet-stream",
})
part, _ := client.Uploads.AddPart(context.Background(), upload.ID, uploads.AddPartParams{
    File: "./archive.part-01",
})
completed, _ := client.Uploads.Complete(context.Background(), upload.ID, []string{part.ID})
```

Use `Files.List`, `Retrieve`, and `DeleteFile` for the remaining File lifecycle. See https://runapi.ai/docs/resources/files for limits and REST examples.

## License

Licensed under the Apache License, Version 2.0.
