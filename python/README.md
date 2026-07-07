# RunAPI Core Python SDK

The RunAPI Core Python SDK provides shared authentication, HTTP, retry, error, and polling primitives for RunAPI model packages. Install `runapi-core` only when you are building SDK infrastructure or shared Python tooling; application code should normally install a concrete model package such as `runapi-flux-2`.

## Install

```bash
pip install runapi-core
```

## Notes

Use the core package for common client options, error classes, request helpers, file uploads, and task polling behavior that Provider Clients share. Configure it globally or per client:

```python
import runapi.core as runapi

runapi.configure(api_key="sk-...")  # or set RUNAPI_API_KEY in the environment
```

## Request identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

High-level Python Provider Client resource methods accept per-request options and keep response headers on the returned model object. This example uses the Suno Provider Client; install `runapi-suno` to run it.

```python
import os

from runapi.core import RequestOptions
from runapi.suno import SunoClient

client = SunoClient(api_key=os.environ["RUNAPI_API_KEY"])
options = RequestOptions(
    headers={"X-Client-Request-Id": "order-123"},
)

response = client.text_to_music.create(
    prompt="A chill lo-fi beat",
    model="suno-v4.5-plus",
    vocal_mode="instrumental",
    options=options,
)

runapi_task_id = response.runapi_task_id
# Equivalent case-insensitive lookup:
runapi_task_id = response.response_headers["X-RunAPI-Task-Id"]
```

```python
from runapi.core import FilesClient

files = FilesClient()  # reads RUNAPI_API_KEY, or pass api_key="sk-..."
uploaded = files.create(file="./input.png")
remote = files.create(source="https://cdn.runapi.ai/public/samples/input.png")
inline = files.create(source="iVBORw0KGgo...")
print(uploaded.url)
```

Public SDK docs live at https://runapi.ai/docs#runapi-sdks and the model catalog lives at https://runapi.ai/models.

## License

Licensed under the Apache License, Version 2.0.
