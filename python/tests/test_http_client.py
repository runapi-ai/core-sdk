import os
import tempfile

import httpx
import pytest

from runapi.core import constants, errors, http_client
from runapi.core.http_client import HttpClient
from runapi.core.multipart import MultipartBody, MultipartFile
from runapi.core.options import ClientOptions, RequestOptions


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch):
    monkeypatch.setattr(http_client.time, "sleep", lambda _seconds: None)


def make_client(handler, **overrides):
    options = ClientOptions(
        api_key="test-key",
        base_url="https://runapi.ai",
        max_retries=overrides.get("max_retries", 2),
        retry_base_delay=0.01,
        retry_max_delay=0.05,
    )
    return HttpClient(options, transport=httpx.MockTransport(handler))


def test_returns_parsed_json_on_success():
    client = make_client(lambda request: httpx.Response(200, json={"id": "123"}))
    assert client.request("get", "/api/v1/test") == {"id": "123"}


def test_sends_bearer_and_user_agent():
    captured = {}

    def handler(request):
        captured["auth"] = request.headers.get("authorization")
        captured["ua"] = request.headers.get("user-agent")
        return httpx.Response(200, json={})

    make_client(handler).request("get", "/api/v1/test")
    assert captured["auth"] == "Bearer test-key"
    assert captured["ua"] == constants.SDK_USER_AGENT


def test_sends_json_body_for_post():
    captured = {}

    def handler(request):
        captured["body"] = request.content
        captured["content_type"] = request.headers.get("content-type")
        return httpx.Response(200, json={"id": "1"})

    result = make_client(handler).request("post", "/api/v1/test", body={"prompt": "hello"})
    assert result == {"id": "1"}
    assert captured["body"] == b'{"prompt":"hello"}'
    assert captured["content_type"] == "application/json"


def test_sends_multipart_without_json_content_type():
    captured = {}

    def handler(request):
        captured["content_type"] = request.headers.get("content-type")
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as handle:
        handle.write(b"png")
        path = handle.name
    try:
        body = MultipartBody(
            fields={"file_name": "image.png"},
            files={"file": MultipartFile(path=path, filename="image.png", content_type="image/png")},
        )
        make_client(handler).request("post", "/api/v1/files", body=body)
    finally:
        os.unlink(path)

    assert captured["content_type"].startswith("multipart/form-data")
    assert b"image.png" in captured["body"]
    assert b"png" in captured["body"]


def test_returns_none_for_empty_body():
    client = make_client(lambda request: httpx.Response(204))
    assert client.request("delete", "/api/v1/test") is None


def test_returns_raw_string_for_non_json():
    client = make_client(lambda request: httpx.Response(200, text="plain text"))
    assert client.request("get", "/api/v1/test") == "plain text"


@pytest.mark.parametrize(
    "status,error_class",
    [
        (401, errors.AuthenticationError),
        (402, errors.InsufficientCreditsError),
        (404, errors.NotFoundError),
        (422, errors.ValidationError),
        (429, errors.RateLimitError),
        (503, errors.ServiceUnavailableError),
    ],
)
def test_error_mapping(status, error_class):
    client = make_client(lambda request: httpx.Response(status, json={"error": "fail"}))
    with pytest.raises(error_class):
        client.request("get", "/api/v1/test")


def test_retries_idempotent_get_on_503():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, json={"error": "down"})
        return httpx.Response(200, json={"ok": True})

    assert make_client(handler).request("get", "/api/v1/test") == {"ok": True}
    assert calls["n"] == 2


def test_does_not_retry_post_on_503():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(503, json={"error": "down"})

    with pytest.raises(errors.ServiceUnavailableError):
        make_client(handler).request("post", "/api/v1/test")
    assert calls["n"] == 1


def test_respects_retry_after(monkeypatch):
    slept = []
    monkeypatch.setattr(http_client.time, "sleep", lambda seconds: slept.append(seconds))
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, json={"error": "rate"}, headers={"Retry-After": "1"})
        return httpx.Response(200, json={"ok": True})

    assert make_client(handler).request("get", "/api/v1/test") == {"ok": True}
    assert slept == [1.0]


def test_respects_max_retries_override():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(503, json={"error": "down"})

    with pytest.raises(errors.ServiceUnavailableError):
        make_client(handler).request("get", "/api/v1/test", options=RequestOptions(max_retries=0))
    assert calls["n"] == 1


def test_timeout_maps_to_timeout_error():
    def handler(request):
        raise httpx.ConnectTimeout("timed out")

    with pytest.raises(errors.TimeoutError, match="timed out"):
        make_client(handler).request("get", "/api/v1/test")


def test_transport_error_maps_to_network_error():
    def handler(request):
        raise httpx.ConnectError("getaddrinfo failed")

    with pytest.raises(errors.NetworkError, match="getaddrinfo failed"):
        make_client(handler).request("get", "/api/v1/test")


def test_merges_custom_request_headers():
    captured = {}

    def handler(request):
        captured["custom"] = request.headers.get("x-custom")
        return httpx.Response(200, json={})

    make_client(handler).request("get", "/api/v1/test", options=RequestOptions(headers={"X-Custom": "value"}))
    assert captured["custom"] == "value"


def test_stringifies_non_string_header_values():
    # Regression: a non-str header value must be stringified (like multipart
    # fields), not passed through to httpx which raises TypeError.
    captured = {}

    def handler(request):
        captured["trace"] = request.headers.get("x-trace")
        return httpx.Response(200, json={})

    make_client(handler).request("get", "/api/v1/test", options=RequestOptions(headers={"X-Trace": 123}))
    assert captured["trace"] == "123"
