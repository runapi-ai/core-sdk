<p align="center">
  <a href="https://runapi.ai"><img src="https://runapi.ai/icon.svg" height="56" alt="RunAPI"></a>
</p>

<h3 align="center">
  <a href="https://github.com/runapi-ai/core-sdk">RunAPI Core SDK</a>
</h3>

<p align="center">
  Shared SDK primitives for RunAPI JavaScript, Ruby, and Go SDKs.
</p>

<div align="center">

[![npm](https://img.shields.io/npm/v/@runapi.ai/core)](https://www.npmjs.com/package/@runapi.ai/core)
[![RubyGems](https://img.shields.io/gem/v/runapi-core)](https://rubygems.org/gems/runapi-core)
[![Go Reference](https://pkg.go.dev/badge/github.com/runapi-ai/core-sdk/go.svg)](https://pkg.go.dev/github.com/runapi-ai/core-sdk/go)
[![License](https://img.shields.io/github/license/runapi-ai/core-sdk)](https://github.com/runapi-ai/core-sdk/blob/main/LICENSE)

</div>
<br/>

RunAPI Core SDK contains the shared authentication, HTTP, retry, error, and polling primitives used by RunAPI JavaScript, Ruby, and Go model SDKs. Application code should usually install a model package such as `@runapi.ai/suno`; install core packages only when you are building shared SDK infrastructure.

## Install

```bash
npm install @runapi.ai/core
gem install runapi-core
go get github.com/runapi-ai/core-sdk/go@latest
```

## Public links

- SDK docs: https://runapi.ai/docs#runapi-sdks
- Model catalog: https://runapi.ai/models
- Repository: https://github.com/runapi-ai/core-sdk

## License

Licensed under the Apache License, Version 2.0.
