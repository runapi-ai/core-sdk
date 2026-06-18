# RunAPI Core JavaScript SDK

The RunAPI Core JavaScript SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model SDK packages. Install `@runapi.ai/core` only when you are building SDK infrastructure or shared tooling; application code should normally install a concrete model package such as `@runapi.ai/suno`.

## Install

```bash
npm install @runapi.ai/core
```

## Notes

Use the core package for `ClientOptions`, common error classes, request helpers, and task polling behavior that model SDKs share. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## File Upload

```typescript
import { NanoBananaClient } from '@runapi.ai/nano-banana';

const client = new NanoBananaClient({ apiKey: process.env.RUNAPI_API_KEY });

const upload = await client.files.create({ source: { type: 'url', url: 'https://example.com/photo.jpg' } });
console.log(upload.url);
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## License

Licensed under the Apache License, Version 2.0.
