# RunAPI Core Go SDK

The RunAPI Core Go SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model Go modules. Install `github.com/runapi-ai/core-sdk/go` only when you are building SDK infrastructure or shared Go tooling; application code should normally install a concrete model module such as `github.com/runapi-ai/suno-sdk/go`.

## Install

```bash
go get github.com/runapi-ai/core-sdk/go@latest
```

## Notes

Use the core module for client options, common error types, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
