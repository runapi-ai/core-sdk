# RunAPI Core Ruby SDK

The RunAPI Core Ruby SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model gems. Install `runapi-core` only when you are building SDK infrastructure or shared Ruby tooling; application code should normally install a concrete model gem such as `runapi-suno`.

## Install

```bash
gem install runapi-core
```

## Notes

Use the core gem for common client options, error classes, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
