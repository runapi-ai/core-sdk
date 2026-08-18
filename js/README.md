# RunAPI Core JavaScript SDK

The RunAPI Core JavaScript SDK provides shared authentication, HTTP, retry, error, Files, Uploads, and polling primitives for RunAPI JavaScript Provider Client packages. Install `@runapi.ai/core` only when you are building SDK infrastructure or shared tooling; application code should normally install a concrete package such as `@runapi.ai/suno`.

## Install

```bash
npm install @runapi.ai/core
```

## Notes

Use the core package for `ClientOptions`, common error classes, request helpers, and task polling behavior shared across JavaScript Provider Client packages. Public SDK docs live at https://runapi.ai/docs/resources/sdks and the model catalog lives at https://runapi.ai/models.

## Live Pricing

Every Provider Client exposes `pricing`. Schedule lookup and quotes use the live API response and do not retain a local price cache.

```typescript
const schedules = await client.pricing.list({ service: 'suno' });
const quote = await client.pricing.quote({
  service: 'suno',
  action: 'convert_audio',
  params: {},
});
```

Public schedule lookup and quotes that use only public parameters work without an API key. Pass a standard API key when a quote references an account-owned source Task.

Use `PricingClient` when pricing is the only capability needed:

```typescript
import { PricingClient } from '@runapi.ai/core';

const pricing = new PricingClient();
const schedules = await pricing.list({ service: 'suno' });
```

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

## Temporary File Upload

```typescript
import { NanoBananaClient } from '@runapi.ai/nano-banana';

const client = new NanoBananaClient({ apiKey: process.env.RUNAPI_API_KEY });

const upload = await client.files.create({ source: { type: 'url', url: 'https://cdn.runapi.ai/public/samples/image.jpg' } });
console.log(upload.url);
```

> [!IMPORTANT]
> Uploaded file URLs expire 1 hour after creation. Pass them to a model promptly rather than storing them for later use.

## Persistent Files And Multipart Uploads

The existing `files.create()` method above keeps its temporary URL behavior. Use `createFile()` for a persistent File object and `uploads` when sending one or more Parts:

```typescript
const file = await client.files.createFile({
  file: new Blob([fileBytes], { type: 'application/pdf' }),
  filename: 'knowledge.pdf',
});
const content = await client.files.content(file.id);

const upload = await client.uploads.create({
  bytes: 1048576,
  filename: 'archive.bin',
  mime_type: 'application/octet-stream',
});
const part = await client.uploads.addPart(upload.id, new Blob([partBytes]));
const completed = await client.uploads.complete(upload.id, [part.id]);
```

Use `files.list()`, `retrieve()`, and `deleteFile()` for the remaining File lifecycle. See https://runapi.ai/docs/resources/files for limits and REST examples.

## License

Licensed under the Apache License, Version 2.0.
