<p align="center">
  <a href="https://runapi.ai"><img src="https://runapi.ai/icon.svg" height="56" alt="RunAPI"></a>
</p>

<h3 align="center">
  <a href="https://github.com/runapi-ai/core-sdk">RunAPI Core SDK</a>
</h3>

<p align="center">
  Shared SDK primitives for RunAPI JavaScript, Python, Ruby, Go, Java, and PHP SDKs.
</p>

<div align="center">

[![npm](https://img.shields.io/npm/v/@runapi.ai/core)](https://www.npmjs.com/package/@runapi.ai/core)
[![PyPI](https://img.shields.io/pypi/v/runapi-core)](https://pypi.org/project/runapi-core/)
[![RubyGems](https://img.shields.io/gem/v/runapi-core)](https://rubygems.org/gems/runapi-core)
[![Go Reference](https://pkg.go.dev/badge/github.com/runapi-ai/core-sdk/go.svg)](https://pkg.go.dev/github.com/runapi-ai/core-sdk/go)
[![Maven Central](https://img.shields.io/maven-central/v/ai.runapi/runapi-core)](https://central.sonatype.com/artifact/ai.runapi/runapi-core)
[![License](https://img.shields.io/github/license/runapi-ai/core-sdk)](https://github.com/runapi-ai/core-sdk/blob/main/LICENSE)

</div>
<br/>

RunAPI Core SDK contains the shared authentication, HTTP, retry, error, file upload, account, and polling primitives used by RunAPI Provider Client packages. Application code should usually install a concrete Provider Client package such as `@runapi.ai/wan`, `runapi-wan`, `runapi-ai/wan`, `github.com/runapi-ai/wan-sdk/go`, or `ai.runapi:runapi-wan`; install core packages directly only when building shared SDK infrastructure.

## Install

```bash
npm install @runapi.ai/core
pip install runapi-core
gem install runapi-core
go get github.com/runapi-ai/core-sdk/go@latest
```

Gradle:

```kotlin
dependencies {
  implementation("ai.runapi:runapi-core:0.2.6")
}
```

Maven:

```xml
<dependency>
  <groupId>ai.runapi</groupId>
  <artifactId>runapi-core</artifactId>
  <version>0.2.6</version>
</dependency>
```

The PHP core package is published from the split Composer repository as `runapi-ai/core`; see https://github.com/runapi-ai/core-php for PHP install and examples.

## Use Core Directly

Core is normally transitive from a Provider Client package. Install it directly when you need shared Java exceptions, `RequestOptions`, files, account, or transport primitives in reusable tooling.

```java
import ai.runapi.core.RequestOptions;
import ai.runapi.core.files.FileCreateParams;
import java.time.Duration;

RequestOptions options = RequestOptions.builder()
    .timeout(Duration.ofMinutes(15))
    .maxRetries(2)
    .build();

FileCreateParams upload = FileCreateParams.fromUrl("https://cdn.runapi.ai/public/samples/input.png")
    .fileName("input.png")
    .build();
```

## Repository Layout

- `js/` publishes `@runapi.ai/core`.
- `python/` publishes `runapi-core`.
- `ruby/` publishes `runapi-core`.
- `go/` publishes `github.com/runapi-ai/core-sdk/go`.
- `java/` publishes `ai.runapi:runapi-core` and `ai.runapi:runapi-bom`.
- PHP publishes `runapi-ai/core` from https://github.com/runapi-ai/core-php.

## Public Links

- SDK docs: https://runapi.ai/docs#runapi-sdks
- Model catalog: https://runapi.ai/models
- Repository: https://github.com/runapi-ai/core-sdk

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

Public API responses expose `X-RunAPI-Task-Id` when a RunAPI task exists. Ruby and Python Provider Client resource methods keep response headers on returned model objects via `response_headers` and `runapi_task_id`. Other high-level SDK resource methods expose parsed response bodies; use a custom transport or direct HTTP request when those integrations need raw response headers.

## License

Licensed under the Apache License, Version 2.0.
