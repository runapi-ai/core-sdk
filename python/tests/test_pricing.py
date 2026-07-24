import httpx
import pytest

from runapi.core import ApiResponse, ClientOptions, HttpClient, PriceQuoteResponse, PriceScheduleListResponse, Pricing, PricingClient, RequestOptions, config


class FakeHttp:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body, options))
        return self._responses.pop(0)


SCHEDULE = {
    "service": "nano_banana",
    "action": "text_to_image",
    "model": "nano-banana",
    "pricing_status": "available",
    "catalog_status": "active",
    "currency": "USD",
    "billing_unit": "per_call",
    "billing_strategy": "flat",
    "unit_price_cents": 5,
    "future_field": {"preserved": True},
}


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    monkeypatch.delenv("RUNAPI_API_KEY", raising=False)
    monkeypatch.setattr(config, "api_key", None)
    yield


def test_list_schedules_uses_live_endpoint_filters_and_revalidation_options():
    options = RequestOptions(headers={"If-None-Match": '"schedule-v1"'})
    http = FakeHttp(ApiResponse({"as_of": "2026-07-23T00:00:00.000000Z", "price_schedules": [SCHEDULE]}, {"ETag": '"schedule-v2"'}))

    result = Pricing(http).list_schedules(
        service="nano_banana", action="text_to_image", model="nano-banana", options=options
    )

    assert isinstance(result, PriceScheduleListResponse)
    assert result.price_schedules[0].future_field.preserved is True
    assert result.response_header("etag") == '"schedule-v2"'
    assert http.calls == [
        ("get", "/api/v1/price_schedules?service=nano_banana&action=text_to_image&model=nano-banana", None, options)
    ]


def test_create_quote_is_anonymous_by_default_and_returns_a_typed_quote():
    http = FakeHttp(
        {
            "price_quote": {
                "service": "nano_banana",
                "action": "text_to_image",
                "model": "nano-banana",
                "pricing_status": "available",
                "currency": "USD",
                "reservation_amount_cents": 5,
                "estimate_basis": "exact",
                "as_of": "2026-07-23T00:00:00.000000Z",
            }
        }
    )

    result = Pricing(http).create_quote(
        service="nano_banana", action="text_to_image", model="nano-banana", params={"prompt": "A glass observatory"}
    )

    assert isinstance(result, PriceQuoteResponse)
    assert result.price_quote.reservation_amount_cents == 5
    assert http.calls == [
        (
            "post",
            "/api/v1/price_quotes",
            {"service": "nano_banana", "action": "text_to_image", "model": "nano-banana", "params": {"prompt": "A glass observatory"}},
            None,
        )
    ]


def test_standalone_client_allows_anonymous_schedule_requests():
    captured = {}

    def handler(request):
        captured["authorization"] = request.headers.get("authorization")
        return httpx.Response(200, json={"as_of": "2026-07-23T00:00:00.000000Z", "price_schedules": []})

    http = HttpClient(
        ClientOptions(api_key=None, base_url="https://runapi.ai"), transport=httpx.MockTransport(handler)
    )
    result = PricingClient(http_client=http).list_schedules()

    assert isinstance(result, PriceScheduleListResponse)
    assert captured["authorization"] is None


def test_schedule_revalidation_returns_none_for_not_modified():
    http = HttpClient(
        ClientOptions(api_key=None, base_url="https://runapi.ai"),
        transport=httpx.MockTransport(lambda _request: httpx.Response(304, headers={"ETag": '"schedule-v1"'})),
    )

    result = PricingClient(http_client=http).list_schedules(options=RequestOptions(headers={"If-None-Match": '"schedule-v1"'}))

    assert result is None


def test_standalone_client_uses_configured_api_key_when_a_quote_needs_auth(monkeypatch):
    monkeypatch.setattr(config, "api_key", "configured-key")
    client = PricingClient()
    try:
        assert client._http._client.headers["authorization"] == "Bearer configured-key"
    finally:
        client._http.close()
