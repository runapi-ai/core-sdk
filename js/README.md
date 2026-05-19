# RunAPI Core JavaScript SDK

The RunAPI Core JavaScript SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model SDK packages. Install `@runapi.ai/core` only when you are building SDK infrastructure or shared tooling; application code should normally install a concrete model package such as `@runapi.ai/suno`.

## Install

```bash
npm install @runapi.ai/core
```

## Notes

Use the core package for `ClientOptions`, common error classes, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
