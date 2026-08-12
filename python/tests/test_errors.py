import time

import httpx
import pytest

from runapi.core import errors


def response(status, body="", headers=None):
    return httpx.Response(status, headers=headers or {}, text=body)


@pytest.mark.parametrize(
    "status,error_class",
    [
        (401, errors.AuthenticationError),
        (402, errors.InsufficientCreditsError),
        (404, errors.NotFoundError),
        (409, errors.ConflictError),
        (422, errors.ValidationError),
        (429, errors.RateLimitError),
        (503, errors.ServiceUnavailableError),
        (500, errors.ServerError),
        (502, errors.ServerError),
    ],
)
def test_maps_status_to_error_class(status, error_class):
    error = errors.error_from_response(response(status))
    assert isinstance(error, error_class)
    assert error.status == status


def test_maps_unmapped_status_to_base_error():
    error = errors.error_from_response(response(418))
    assert type(error) is errors.Error
    assert error.status == 418
    assert error.message == "Request failed"


def test_default_message_for_known_status():
    assert errors.error_from_response(response(401)).message == "Unauthorized"


def test_retry_after_seconds():
    error = errors.error_from_response(response(429, headers={"retry-after": "30"}))
    assert isinstance(error, errors.RateLimitError)
    assert error.retry_after == 30.0


def test_retry_after_http_date():
    future = (
        time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time() + 60))
    )
    error = errors.error_from_response(response(429, headers={"retry-after": future}))
    assert error.retry_after == pytest.approx(60, abs=2)


def test_extracts_request_id():
    error = errors.error_from_response(response(500, headers={"x-request-id": "req-123"}))
    assert error.request_id == "req-123"


def test_extracts_message_from_error_string():
    error = errors.error_from_response(response(400, body='{"error":"Custom error message"}'))
    assert error.message == "Custom error message"


def test_extracts_message_from_nested_error():
    error = errors.error_from_response(response(400, body='{"error":{"message":"Nested message"}}'))
    assert error.message == "Nested message"


def test_preserves_explicit_http_error_code_and_leaves_missing_code_none():
    explicit = errors.error_from_response(
        response(409, body='{"error":{"code":"source_task_not_ready","message":"wait"}}')
    )
    missing = errors.error_from_response(response(409, body='{"error":{"message":"wait"}}'))

    assert explicit.code == "source_task_not_ready"
    assert missing.code is None


def test_continuation_errors_preserve_codes_and_status_classification():
    cases = [
        (400, "invalid_resource_id", errors.ValidationError),
        (409, "request_conflict", errors.ConflictError),
        (409, "source_task_not_ready", errors.ConflictError),
        (422, "source_task_unusable", errors.ValidationError),
        (422, "continuation_not_supported", errors.ValidationError),
        (429, "rate_limited", errors.RateLimitError),
        (503, "continuation_unavailable", errors.ServiceUnavailableError),
    ]

    for status, code, error_class in cases:
        error = errors.error_from_response(
            response(status, body=f'{{"error":{{"code":"{code}","message":"failed"}}}}')
        )
        assert isinstance(error, error_class)
        assert error.status == status
        assert error.code == code


def test_does_not_extract_message_from_legacy_errors_array():
    error = errors.error_from_response(response(400, body='{"errors":["First error"]}'))
    assert error.message == "Bad request"


def test_handles_html_error_page():
    body = "<!DOCTYPE html><html><head><title>502 Bad Gateway</title></head><body><h1>Bad Gateway</h1></body></html>"
    error = errors.error_from_response(response(502, body=body))
    assert error.message == "502 Bad Gateway"
    assert error.details["is_html_error"] is True


def test_handles_empty_body():
    error = errors.error_from_response(response(500, body=""))
    assert isinstance(error, errors.ServerError)
    assert error.message == "Request failed"
    assert error.details is None


def test_handles_malformed_json():
    error = errors.error_from_response(response(400, body="not json"))
    assert error.details == "not json"


def test_to_dict_is_compact():
    error = errors.AuthenticationError("Bad key", request_id="req-1")
    assert error.to_dict() == {
        "error": "AuthenticationError",
        "message": "Bad key",
        "code": "authentication",
        "status": 401,
        "request_id": "req-1",
    }


def test_server_error_defaults_and_overrides():
    assert errors.ServerError().status == 500
    assert errors.ServerError("Bad gateway", status=502).status == 502


def test_service_unavailable_defaults_to_503():
    assert errors.ServiceUnavailableError().status == 503


def test_resource_validation_uses_summary_and_preserves_field_errors():
    error = errors.error_from_response(
        response(422, body='{"error":"Validation failed","errors":{"prompt":["too long"]}}')
    )
    assert error.message == "Validation failed"
    assert error.details["errors"] == {"prompt": ["too long"]}
