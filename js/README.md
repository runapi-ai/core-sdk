# RunAPI Core JavaScript SDK

The RunAPI Core JavaScript SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI JavaScript Provider Client packages. Install `@runapi.ai/core` only when you are building SDK infrastructure or shared tooling; application code should normally install a concrete package such as `@runapi.ai/suno`.

## Install

```bash
npm install @runapi.ai/core
```

## Notes

Use the core package for `ClientOptions`, common error classes, request helpers, and task polling behavior shared across JavaScript Provider Client packages. Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## Request identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

Task-creation calls also accept an optional opaque `Idempotency-Key` up to 512 characters. Generate one value per logical task and reuse it only with identical input after an unknown result. Reusing the value with different input returns `409 Conflict`; do not derive it from `X-Client-Request-Id`.

```typescript
await client.textToImage.create(
  { prompt: 'A sunset over the ocean' },
  { headers: {
    'X-Client-Request-Id': 'order-123',
    'Idempotency-Key': 'opaque-logical-task-123'
  } }
);
```

Public API responses expose `X-RunAPI-Task-Id` when a RunAPI task exists. High-level JavaScript Provider Client resource methods return parsed response bodies; use a custom transport or direct HTTP request when your integration needs raw response headers.

## File Upload

```typescript
import { NanoBananaClient } from '@runapi.ai/nano-banana';

const client = new NanoBananaClient({ apiKey: process.env.RUNAPI_API_KEY });

const upload = await client.files.create({ source: { type: 'url', url: 'https://cdn.runapi.ai/public/samples/image.jpg' } });
console.log(upload.url);
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## License

Licensed under the Apache License, Version 2.0.
