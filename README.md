<p align="center">
  <a href="https://runapi.ai"><img src="https://runapi.ai/icon.svg" height="56" alt="RunAPI"></a>
</p>

<h3 align="center">
  <a href="https://github.com/runapi-ai/core-sdk">RunAPI Core SDK</a>
</h3>

<p align="center">
  Shared SDK primitives for RunAPI JavaScript, Python, Ruby, Go, and Java SDKs.
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

RunAPI Core SDK contains the shared authentication, HTTP, retry, error, file upload, account, and polling primitives used by RunAPI model SDKs. Application code should usually install a concrete model package such as `@runapi.ai/wan`, `runapi-wan`, `github.com/runapi-ai/wan-sdk/go`, or `ai.runapi:runapi-wan`; install core packages directly only when building shared SDK infrastructure.

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
  implementation("ai.runapi:runapi-core:0.1.0")
}
```

Maven:

```xml
<dependency>
  <groupId>ai.runapi</groupId>
  <artifactId>runapi-core</artifactId>
  <version>0.1.0</version>
</dependency>
```

## Use Core Directly

Core is normally transitive from a model SDK. Install it directly when you need shared Java exceptions, `RequestOptions`, files, account, or transport primitives in reusable tooling.

```java
import ai.runapi.core.RequestOptions;
import ai.runapi.core.files.FileCreateParams;
import java.time.Duration;

RequestOptions options = RequestOptions.builder()
    .timeout(Duration.ofMinutes(15))
    .maxRetries(2)
    .build();

FileCreateParams upload = FileCreateParams.fromUrl("https://example.com/input.png")
    .fileName("input.png")
    .build();
```

## Repository Layout

- `js/` publishes `@runapi.ai/core`.
- `python/` publishes `runapi-core`.
- `ruby/` publishes `runapi-core`.
- `go/` publishes `github.com/runapi-ai/core-sdk/go`.
- `java/` publishes `ai.runapi:runapi-core` and `ai.runapi:runapi-bom`.

## Public Links

- SDK docs: https://runapi.ai/docs#runapi-sdks
- Model catalog: https://runapi.ai/models
- Repository: https://github.com/runapi-ai/core-sdk

## License

Licensed under the Apache License, Version 2.0.
