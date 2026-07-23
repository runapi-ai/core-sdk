# RunAPI Core Java SDK

[![Maven Central](https://img.shields.io/maven-central/v/ai.runapi/runapi-core)](https://central.sonatype.com/artifact/ai.runapi/runapi-core)

The RunAPI Core Java SDK provides shared authentication, HTTP, retry, error, polling, file upload, account, request option, and transport primitives for RunAPI Java modules. Application code should normally install a concrete model module such as `ai.runapi:runapi-wan`; install `ai.runapi:runapi-core` directly only when building shared Java SDK tooling.

## Requirements

The Java SDK targets Java 8 bytecode and is tested on Java 8, 11, 17, and 21.

## Install

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

Use the BOM when multiple RunAPI Java modules are installed:

```kotlin
dependencies {
  implementation(platform("ai.runapi:runapi-bom:0.2.6"))
  implementation("ai.runapi:runapi-core")
}
```

## What Core Provides

- Client configuration and API key resolution through builders and environment variables.
- Shared `RequestOptions` for timeouts, retries, headers, and polling behavior.
- Files and account clients used by all model clients.
- Strict contract validation helpers used by model packages.
- Common error types such as `RunApiException`, `ValidationException`, and `RateLimitException`.

## Request Identifiers And Safe Task Creation

Task-creation calls accept an optional opaque `Idempotency-Key` up to 512 characters. Generate one value per logical task and reuse it only with identical input after an unknown result. Reusing the value with different input returns `409 Conflict`; do not derive it from `X-Client-Request-Id`.

```java
import ai.runapi.core.RequestOptions;

RequestOptions options = RequestOptions.builder()
    .header("X-Client-Request-Id", "order-123")
    .header("Idempotency-Key", "opaque-logical-task-123")
    .build();
```

## File Upload

```java
import ai.runapi.core.files.FileCreateParams;
import ai.runapi.core.files.FileUploadResponse;
import ai.runapi.wan.WanClient;
import java.nio.file.Paths;

WanClient client = WanClient.builder()
    .apiKey(System.getenv("RUNAPI_API_KEY"))
    .build();

FileUploadResponse uploaded = client.files().create(
    FileCreateParams.fromPath(Paths.get("input.png"))
        .fileName("input.png")
        .build()
);
```

Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
