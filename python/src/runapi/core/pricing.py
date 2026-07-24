"""Live Pricing API resources."""

from __future__ import annotations

from typing import Any, Optional

from .auth import resolve_optional_api_key
from .models import BaseModel, optional, required
from .http_client import HttpClient
from .options import ClientOptions, RequestOptions
from .resource import Resource


class PriceSchedule(BaseModel):
    service = required(str)
    action = required(str)
    model = optional(str)
    pricing_status = required(str)
    catalog_status = required(str)
    currency = required(str)
    billing_unit = optional(str)
    billing_strategy = optional(str)
    unit_price_cents = optional(int)
    input_price_per_1m_cents = optional(int)
    output_price_per_1m_cents = optional(int)
    cache_read_price_per_1m_cents = optional(int)
    cache_write_5m_price_per_1m_cents = optional(int)
    cache_write_1h_price_per_1m_cents = optional(int)
    billing_config = optional()


class PriceScheduleListResponse(BaseModel):
    as_of = required(str)
    price_schedules = required([PriceSchedule])


class PriceQuote(BaseModel):
    service = required(str)
    action = required(str)
    model = optional(str)
    pricing_status = required(str)
    currency = required(str)
    reservation_amount_cents = required(int)
    estimate_basis = required(str)
    as_of = required(str)


class PriceQuoteResponse(BaseModel):
    price_quote = required(PriceQuote)


class Pricing(Resource):
    """Read current price schedules and create reservation estimates."""

    SCHEDULES_ENDPOINT = "/api/v1/price_schedules"
    QUOTES_ENDPOINT = "/api/v1/price_quotes"

    def list_schedules(
        self,
        service: Optional[str] = None,
        action: Optional[str] = None,
        model: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> Optional[PriceScheduleListResponse]:
        filters = self._compact_params({"service": service, "action": action, "model": model})
        path = self.SCHEDULES_ENDPOINT
        if filters:
            from urllib.parse import urlencode

            path = f"{path}?{urlencode(filters)}"
        return self._request("get", path, options=options, response_class=PriceScheduleListResponse)

    def create_quote(
        self,
        service: str,
        action: str,
        model: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        options: Optional[RequestOptions] = None,
    ) -> PriceQuoteResponse:
        body = {"service": service, "action": action, "model": model, "params": params}
        return self._request(
            "post", self.QUOTES_ENDPOINT, body=self._compact_params(body), options=options, response_class=PriceQuoteResponse
        )


class PricingClient(Pricing):
    """Standalone Pricing client with optional API authentication."""

    def __init__(self, api_key: Optional[str] = None, **options: Any) -> None:
        client_options = ClientOptions(api_key=resolve_optional_api_key(api_key), **options)
        super().__init__(client_options.http_client or HttpClient(client_options))
