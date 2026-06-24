# RunAPI Core Python SDK

The RunAPI Core Python SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model packages. Install `runapi-core` only when you are building SDK infrastructure or shared Python tooling; application code should normally install a concrete model package such as `runapi-flux-2`.

## Install

```bash
pip install runapi-core
```

## Notes

Use the core package for common client options, error classes, request helpers, file uploads, and task polling behavior that model SDKs share. Configure it globally or per client:

```python
import runapi.core as runapi

runapi.configure(api_key="sk-...")  # or set RUNAPI_API_KEY in the environment
```

```python
from runapi.core import FilesClient

files = FilesClient()  # reads RUNAPI_API_KEY, or pass api_key="sk-..."
uploaded = files.create(file="./input.png")
remote = files.create(source="https://example.com/input.png")
inline = files.create(source="iVBORw0KGgo...")
print(uploaded.url)
```

Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
