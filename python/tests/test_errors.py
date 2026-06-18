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


def test_extracts_message_from_errors_array():
    error = errors.error_from_response(response(400, body='{"errors":["First error"]}'))
    assert error.message == "First error"


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
        "status": 401,
        "request_id": "req-1",
    }


def test_server_error_defaults_and_overrides():
    assert errors.ServerError().status == 500
    assert errors.ServerError("Bad gateway", status=502).status == 502


def test_service_unavailable_defaults_to_503():
    assert errors.ServiceUnavailableError().status == 503


def test_extracts_message_from_errors_array_of_dicts():
    # Regression: an errors-array whose elements are dicts must yield the dict's
    # message string, not the raw dict.
    error = errors.error_from_response(
        response(400, body='{"errors":[{"field":"prompt","message":"too long"}]}')
    )
    assert error.message == "too long"
