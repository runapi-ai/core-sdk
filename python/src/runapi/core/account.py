"""Account resources available from every Provider Client."""

from __future__ import annotations

from typing import Optional

from .models import BaseModel, required
from .options import RequestOptions
from .resource import Resource


class AccountRecord(BaseModel):
    id = required(int)
    name = required(str)


class AccountInfoResponse(BaseModel):
    id = required(int)
    name = required(str)
    email = required(str)
    account = required(AccountRecord)


class AccountBalanceResponse(BaseModel):
    balance_cents = required(int)
    paid_balance_cents = required(int)
    bonus_balance_cents = required(int)
    spent_cents_today = required(int)
    spent_cents_total = required(int)


class Account(Resource):
    """Read the authenticated user's account information and balance."""

    INFO_ENDPOINT = "/api/v1/me"
    BALANCE_ENDPOINT = "/api/v1/me/balance"

    def info(self, options: Optional[RequestOptions] = None) -> AccountInfoResponse:
        return self._request("get", self.INFO_ENDPOINT, options=options, response_class=AccountInfoResponse)

    def balance(self, options: Optional[RequestOptions] = None) -> AccountBalanceResponse:
        return self._request("get", self.BALANCE_ENDPOINT, options=options, response_class=AccountBalanceResponse)
