from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from runapi.core import ApiResponse, BaseModel, ClientOptions, HttpClient, Resource, TaskResponse, optional, required
from runapi.core.errors import TaskTimeoutError, ValidationError
from runapi.core.options import PollingOptions, RequestOptions


class CompletedResponse(TaskResponse):
    id = required(str)
    images = required([lambda: DummyImage])


class DummyImage(BaseModel):
    url = optional(str)


class FakeHttp:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []
        self.options = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body))
        self.options.append(options)
        return self._responses.pop(0)


class SampleResource(Resource):
    RESPONSE_CLASS = TaskResponse
    COMPLETED_RESPONSE_CLASS = CompletedResponse


class HybridResponse(TaskResponse):
    prompts = required([str])


class HybridResource(Resource):
    RESPONSE_CLASS = HybridResponse


def test_request_coerces_to_response_class():
    resource = SampleResource(FakeHttp({"id": "1", "status": "pending"}))
    result = resource._request("post", "/x", body={"a": 1})
    assert isinstance(result, TaskResponse)
    assert result.id == "1"


def test_request_attaches_response_headers_to_model():
    resource = SampleResource(
        FakeHttp(ApiResponse({"id": "1", "status": "pending"}, {"X-RunAPI-Task-Id": "task-ref-1"}))
    )
    result = resource._request("post", "/x", body={"a": 1})
    assert isinstance(result, TaskResponse)
    assert result.runapi_task_id == "task-ref-1"
    assert result.response_headers["X-RunAPI-Task-Id"] == "task-ref-1"
    assert result.to_dict() == {"id": "1", "status": "pending"}


def test_request_attaches_response_headers_to_array_items():
    resource = SampleResource(
        FakeHttp(ApiResponse([{"id": "1", "status": "pending"}], {"X-RunAPI-Task-Id": "task-ref-1"}))
    )

    result = resource._request("post", "/x", body={"a": 1})

    assert len(result) == 1
    assert isinstance(result[0], TaskResponse)
    assert result[0].runapi_task_id == "task-ref-1"
    assert result[0].response_headers["X-RunAPI-Task-Id"] == "task-ref-1"
    assert result[0].to_dict() == {"id": "1", "status": "pending"}


def test_compact_params_drops_none_and_blank():
    assert Resource._compact_params({"a": 1, "b": None, "c": "", "d": "  ", "e": "x"}) == {"a": 1, "e": "x"}


def test_poll_recoerces_to_completed_class():
    resource = SampleResource(FakeHttp())
    response = TaskResponse({"id": "1", "status": "completed", "usage": {"cost": 0.05}, "images": [{"url": "u"}]})
    result = resource._poll_until_complete(lambda: response, PollingOptions(poll_interval=0, max_wait=1))
    assert isinstance(result, CompletedResponse)
    assert result.images[0].url == "u"


def test_run_hybrid_uses_opaque_location_and_decodes_completed_json(monkeypatch):
    slept = []
    monkeypatch.setattr("runapi.core.polling.time.sleep", lambda seconds: slept.append(seconds))
    http = FakeHttp(
        ApiResponse(
            {"id": "task_1", "status": "processing"},
            {"Location": "https://runapi.ai/api/v1/tasks/task_1", "Retry-After": "3"},
            status_code=202,
        ),
        ApiResponse({"id": "task_1", "status": "processing"}, {"Retry-After": "2"}),
        ApiResponse(
            {
                "id": "task_1",
                "status": "completed", "usage": {"cost": 0.05},
                "response": {
                    "status": 200,
                    "content_type": "application/json",
                    "headers": {"Location": "https://runapi.ai/result"},
                    "body": {"id": "task_1", "status": "completed", "usage": {"cost": 0.05}, "prompts": ["short prompt"]}}}
        ),
    )

    result = HybridResource(http)._run_hybrid("post", "/shorten", {"prompt": "long"})

    assert isinstance(result, HybridResponse)
    assert result.prompts == ["short prompt"]
    assert result.response_header("Location") == "https://runapi.ai/result"
    assert [call[:2] for call in http.calls] == [
        ("post", "/shorten"),
        ("get", "https://runapi.ai/api/v1/tasks/task_1"),
        ("get", "https://runapi.ai/api/v1/tasks/task_1")]
    assert slept == [3.0, 2.0]


def test_run_hybrid_honors_http_date_retry_after(monkeypatch):
    slept = []
    monkeypatch.setattr("runapi.core.polling.time.sleep", lambda seconds: slept.append(seconds))
    now = datetime.now(timezone.utc)
    initial_retry_after = format_datetime(now + timedelta(seconds=30), usegmt=True)
    polling_retry_after = format_datetime(now + timedelta(seconds=60), usegmt=True)
    http = FakeHttp(
        ApiResponse({"id": "task_1", "status": "processing"}, {"Location": "/api/v1/tasks/task_1", "Retry-After": initial_retry_after}, status_code=202),
        ApiResponse({"id": "task_1", "status": "processing"}, {"Retry-After": polling_retry_after}),
        ApiResponse({"id": "task_1", "status": "completed", "usage": {"cost": 0.05}, "response": {"status": 200, "content_type": "application/json", "headers": {}, "body": {"id": "task_1", "status": "completed", "usage": {"cost": 0.05}, "prompts": ["short prompt"]}}}),
    )

    HybridResource(http)._run_hybrid("post", "/shorten", {"prompt": "long"})

    assert slept[0] > 20
    assert slept[1] > 50


def test_run_hybrid_follows_a_real_http_stub_and_reuses_generated_key(monkeypatch):
    monkeypatch.setattr("runapi.core.polling.time.sleep", lambda _seconds: None)
    idempotency_keys = []

    def handler(request):
        if request.method == "POST":
            idempotency_keys.append(request.headers["idempotency-key"])
            return httpx.Response(
                202,
                json={"id": "task_1", "status": "processing"},
                headers={"Location": "/api/v1/tasks/task_1", "Retry-After": "0"},
            )
        return httpx.Response(
            200,
            json={
                "id": "task_1",
                "status": "completed", "usage": {"cost": 0.05},
                "response": {
                    "status": 200,
                    "content_type": "application/json",
                    "headers": {},
                    "body": {"id": "task_1", "status": "completed", "usage": {"cost": 0.05}, "prompts": ["short prompt"]}}},
        )

    http = HttpClient(
        ClientOptions(api_key="test-key", base_url="https://runapi.ai", max_retries=0),
        transport=httpx.MockTransport(handler),
    )

    result = HybridResource(http)._run_hybrid("post", "/shorten", {"prompt": "long"})

    assert result.prompts == ["short prompt"]
    assert len(idempotency_keys) == 1
    assert idempotency_keys[0]


def test_run_hybrid_preserves_caller_idempotency_key():
    http = FakeHttp({"prompts": ["short prompt"]})
    options = RequestOptions(headers={"idempotency-key": "caller-logical-task"})

    result = HybridResource(http)._run_hybrid("post", "/shorten", {"prompt": "long"}, options=options)

    assert result.prompts == ["short prompt"]
    assert http.options[0].headers == {"Idempotency-Key": "caller-logical-task"}
    assert options.headers == {"idempotency-key": "caller-logical-task"}


def test_run_hybrid_replaces_blank_idempotency_key():
    http = FakeHttp({"prompts": ["short prompt"]})

    HybridResource(http)._run_hybrid(
        "post",
        "/shorten",
        {"prompt": "long"},
        options=RequestOptions(headers={"idempotency-key": "  "}),
    )

    assert http.options[0].headers["Idempotency-Key"].strip()


def test_run_hybrid_rejects_conflicting_idempotency_keys():
    options = RequestOptions(headers={"Idempotency-Key": "first", "idempotency-key": "second"})

    with pytest.raises(ValidationError, match="conflicting Idempotency-Key headers"):
        HybridResource(FakeHttp())._run_hybrid("post", "/shorten", {"prompt": "long"}, options=options)


def test_polling_clamps_initial_delay_to_max_wait(monkeypatch):
    clock = {"now": 0.0}
    sleeps = []
    fetches = []

    monkeypatch.setattr("runapi.core.polling.time.monotonic", lambda: clock["now"])

    def sleep(seconds):
        sleeps.append(seconds)
        clock["now"] += seconds

    monkeypatch.setattr("runapi.core.polling.time.sleep", sleep)

    with pytest.raises(TaskTimeoutError, match="timed out after 1s"):
        HybridResource(FakeHttp())._poll_until_complete(
            lambda: fetches.append(True),
            PollingOptions(poll_interval=1, max_wait=1),
            initial_delay=30,
        )

    assert sleeps == [1.0]
    assert fetches == []


def test_polling_clamps_retry_after_to_max_wait(monkeypatch):
    clock = {"now": 0.0}
    sleeps = []
    fetches = []

    monkeypatch.setattr("runapi.core.polling.time.monotonic", lambda: clock["now"])

    def sleep(seconds):
        sleeps.append(seconds)
        clock["now"] += seconds

    monkeypatch.setattr("runapi.core.polling.time.sleep", sleep)

    def fetch():
        fetches.append(True)
        return ApiResponse({"id": "task_1", "status": "processing"}, {"Retry-After": "30"})

    with pytest.raises(TaskTimeoutError, match="timed out after 1s"):
        HybridResource(FakeHttp())._poll_until_complete(
            fetch,
            PollingOptions(poll_interval=1, max_wait=1),
        )

    assert sleeps == [1.0]
    assert fetches == [True]


def test_subscribe_returns_text_srt_and_vtt_without_coercing_to_bytes(monkeypatch):
    monkeypatch.setattr("runapi.core.polling.time.sleep", lambda _seconds: None)
    http = FakeHttp(
        ApiResponse(
            {
                "id": "task_text",
                "status": "completed", "usage": {"cost": 0.05},
                "response": {
                    "status": 200,
                    "content_type": "text/vtt; charset=utf-8",
                    "headers": {},
                    "body": "WEBVTT\n\n00:00.000 --> 00:01.000\nHello"}}
        )
    )

    assert HybridResource(http).subscribe(
        "https://runapi.ai/api/v1/tasks/task_text"
    ) == "WEBVTT\n\n00:00.000 --> 00:01.000\nHello"


def test_subscribe_maps_failed_task_checkpoint_to_public_error(monkeypatch):
    monkeypatch.setattr("runapi.core.polling.time.sleep", lambda _seconds: None)
    http = FakeHttp(
        ApiResponse(
            {
                "id": "task_failure",
                "status": "failed",
                "response": {
                    "status": 422,
                    "content_type": "application/json",
                    "headers": {},
                    "body": {"error": "Prompt rejected"}}}
        )
    )

    with pytest.raises(ValidationError, match="Prompt rejected"):
        HybridResource(http).subscribe("https://runapi.ai/api/v1/tasks/task_failure")
