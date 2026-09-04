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


def test_validate_optional_passes_and_rejects():
    Resource._validate_optional({"k": "a"}, "k", ["a", "b"])
    Resource._validate_optional({}, "k", ["a", "b"])
    with pytest.raises(ValidationError, match="Invalid k"):
        Resource._validate_optional({"k": "z"}, "k", ["a", "b"])


INT_SCHEMA = {
    "models": ["m"],
    "fields_by_model": {
        "m": {
            "duration_int": {"type": "integer", "min": 4, "max": 12},
            "tolerance": {"type": "integer"},
        }
    },
}


def _run_validate(params):
    resource = SampleResource(FakeHttp())
    try:
        resource._validate_contract(INT_SCHEMA, params)
        return ""
    except ValidationError as err:
        return str(err)


def test_validate_integer_rejects_non_integer_within_range():
    assert _run_validate({"model": "m", "duration_int": 11.5}) == "duration_int must be an integer between 4 and 12"


def test_validate_integer_runs_before_range():
    # A non-integer below the range reports the integer error, not the range one.
    assert _run_validate({"model": "m", "duration_int": 2.5}) == "duration_int must be an integer between 4 and 12"


def test_validate_bare_integer_has_no_range_detail():
    assert _run_validate({"model": "m", "tolerance": 3.5}) == "tolerance must be an integer"


def test_validate_integer_still_enforces_range_for_valid_int():
    assert _run_validate({"model": "m", "duration_int": 13}) == "duration_int must be between 4 and 12"


def test_validate_functional_action_uses_underscore_fields():
    resource = SampleResource(FakeHttp())
    schema = {
        "models": [],
        "fields_by_model": {
            "_": {
                "prompt": {"required": True},
                "mode": {"enum": ["fast", "quality"]},
            }
        },
    }
    resource._validate_contract(schema, {"prompt": "hello", "mode": "fast"})
    with pytest.raises(ValidationError, match="prompt is required"):
        resource._validate_contract(schema, {"mode": "fast"})
    with pytest.raises(ValidationError, match="mode must be one of: fast, quality"):
        resource._validate_contract(schema, {"prompt": "hello", "mode": "slow"})


def test_validate_integer_rejects_bool_and_whole_float():
    # bool is an int subclass but is not a valid integer value.
    assert _run_validate({"model": "m", "tolerance": True}) == "tolerance must be an integer"
    # Python keeps the float/int distinction: a whole-valued float is still a float.
    assert _run_validate({"model": "m", "tolerance": 5.0}) == "tolerance must be an integer"
    assert _run_validate({"model": "m", "tolerance": 5}) == ""


def test_validate_boolean_enum_requires_boolean_value():
    schema = {"models": ["m"], "fields_by_model": {"m": {"flag": {"enum": [True, False]}}}}
    resource = SampleResource(FakeHttp())

    resource._validate_contract(schema, {"model": "m", "flag": True})
    resource._validate_contract(schema, {"model": "m", "flag": False})
    with pytest.raises(ValidationError, match="^flag must be one of: True, False$"):
        resource._validate_contract(schema, {"model": "m", "flag": "true"})


def test_validate_array_item_count_constraints():
    schema = {
        "models": ["m"],
        "fields_by_model": {
            "m": {
                "reference_image_urls": {"min_items": 1, "max_items": 3},
            }
        },
    }
    resource = SampleResource(FakeHttp())

    with pytest.raises(ValidationError, match="^reference_image_urls must be an array$"):
        resource._validate_contract(schema, {"model": "m", "reference_image_urls": "image.png"})
    with pytest.raises(ValidationError, match="^reference_image_urls must contain between 1 and 3 items$"):
        resource._validate_contract(schema, {"model": "m", "reference_image_urls": []})
    with pytest.raises(ValidationError, match="^reference_image_urls must contain between 1 and 3 items$"):
        resource._validate_contract(schema, {"model": "m", "reference_image_urls": ["a", "b", "c", "d"]})
    with pytest.raises(ValidationError, match="^reference_image_urls must contain between 1 and 3 items$"):
        resource._validate_contract(schema, {"model": "m", "reference_image_urls": ("a", "b", "c", "d")})

    resource._validate_contract(schema, {"model": "m", "reference_image_urls": ["a", "b", "c"]})
    resource._validate_contract(schema, {"model": "m", "reference_image_urls": ("a", "b", "c")})


def test_validate_contract_runs_rules_before_field_requirements():
    schema = {
        "models": ["m"],
        "rules": [{"when": {"model": "m"}, "forbidden": ["source_task_id"]}],
        "fields_by_model": {"m": {"source_image_urls": {"required": True}}},
    }
    resource = SampleResource(FakeHttp())
    with pytest.raises(ValidationError, match="source_task_id is not allowed when model is m"):
        resource._validate_contract(schema, {"model": "m", "source_task_id": "src_1"})


def test_poll_recoerces_to_completed_class():
    resource = SampleResource(FakeHttp())
    response = TaskResponse({"id": "1", "status": "completed", "images": [{"url": "u"}]})
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
                "status": "completed",
                "response": {
                    "status": 200,
                    "content_type": "application/json",
                    "headers": {"Location": "https://runapi.ai/result"},
                    "body": {"id": "task_1", "status": "completed", "prompts": ["short prompt"]},
                },
            }
        ),
    )

    result = HybridResource(http)._run_hybrid("post", "/shorten", {"prompt": "long"})

    assert isinstance(result, HybridResponse)
    assert result.prompts == ["short prompt"]
    assert result.response_header("Location") == "https://runapi.ai/result"
    assert [call[:2] for call in http.calls] == [
        ("post", "/shorten"),
        ("get", "https://runapi.ai/api/v1/tasks/task_1"),
        ("get", "https://runapi.ai/api/v1/tasks/task_1"),
    ]
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
        ApiResponse({"id": "task_1", "status": "completed", "response": {"status": 200, "content_type": "application/json", "headers": {}, "body": {"id": "task_1", "status": "completed", "prompts": ["short prompt"]}}}),
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
                "status": "completed",
                "response": {
                    "status": 200,
                    "content_type": "application/json",
                    "headers": {},
                    "body": {"id": "task_1", "status": "completed", "prompts": ["short prompt"]},
                },
            },
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
                "status": "completed",
                "response": {
                    "status": 200,
                    "content_type": "text/vtt; charset=utf-8",
                    "headers": {},
                    "body": "WEBVTT\n\n00:00.000 --> 00:01.000\nHello",
                },
            }
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
                    "body": {"error": "Prompt rejected"},
                },
            }
        )
    )

    with pytest.raises(ValidationError, match="Prompt rejected"):
        HybridResource(http).subscribe("https://runapi.ai/api/v1/tasks/task_failure")
