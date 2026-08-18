# RunAPI Core Python SDK

The RunAPI Core Python SDK provides shared authentication, HTTP, retry, error, Files, Uploads, and polling primitives for RunAPI model packages. Install `runapi-core` only when you are building SDK infrastructure or shared Python tooling; application code should normally install a concrete model package such as `runapi-flux-2`.

## Install

```bash
pip install runapi-core
```

## Notes

Use the core package for common client options, error classes, request helpers, file uploads, live pricing, account resources, and task polling behavior that Provider Clients share. Configure it globally or per client:

```python
import runapi.core as runapi

runapi.configure(api_key="sk-...")  # or set RUNAPI_API_KEY in the environment
```

## Request identifiers

RunAPI accepts an optional `X-Client-Request-Id` header on public API calls. Use printable ASCII values up to 512 characters. Accepted values are echoed in the response and stored with the RunAPI task for support and reconciliation.

Task-creation calls also accept an optional opaque `Idempotency-Key` up to 512 characters. Generate one value per logical task and reuse it only with identical input after an unknown result. Reusing the value with different input returns `409 Conflict`; do not derive it from `X-Client-Request-Id`.

High-level Python Provider Client resource methods accept per-request options and keep response headers on the returned model object. This example uses the Suno Provider Client; install `runapi-suno` to run it.

```python
import os

from runapi.core import RequestOptions
from runapi.suno import SunoClient

client = SunoClient(api_key=os.environ["RUNAPI_API_KEY"])
options = RequestOptions(
    headers={
        "X-Client-Request-Id": "order-123",
        "Idempotency-Key": "opaque-logical-task-123",
    },
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

The existing `files.create()` method keeps its temporary URL behavior. Every Provider Client also exposes persistent Files and multipart Uploads:

```python
file = client.files.create_file(file="./knowledge.pdf", purpose="user_data")
content = client.files.content(file.id)

upload = client.uploads.create(
    bytes=1048576,
    filename="archive.bin",
    mime_type="application/octet-stream",
)
part = client.uploads.add_part(upload.id, data="./archive.part-01")
completed = client.uploads.complete(upload.id, part_ids=[part.id])
```

Use `files.list()`, `retrieve()`, and `delete_file()` for the remaining File lifecycle. See https://runapi.ai/docs/resources/files for limits and REST examples.

Public SDK docs live at https://runapi.ai/docs/resources/sdks and the model catalog lives at https://runapi.ai/models.

## Universal resources

Every Provider Client exposes `files`, `account`, and `pricing` through one shared HTTP client. `pricing.list_schedules()` reads the current schedule, and `pricing.create_quote()` estimates a reservation without creating a Task. The schedule and ordinary quote calls do not require an API key; a quote that uses an existing Task as pricing context requires the key for that Task's Account.

```python
from runapi.core import RequestOptions
from runapi.flux import FluxClient

client = FluxClient(api_key="sk-...")
schedules = client.pricing.list_schedules(
    service="flux",
    action="text_to_image",
    options=RequestOptions(headers={"If-None-Match": '"previous-etag"'}),
)
quote = client.pricing.create_quote(
    service="flux",
    action="text_to_image",
    model="flux-pro",
    params={"prompt": "A glass observatory"},
)
```

Task responses expose persisted billing facts at `response.billing`: `reservation`, `settlement`, and `refund` are typed objects when recorded and `None` when the historical fact is absent. These facts describe that Task and are not recalculated from the current schedule.

## License

Licensed under the Apache License, Version 2.0.
