from runapi.core import Account, AccountBalanceResponse, AccountInfoResponse


class FakeHttp:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body, options))
        return self._responses.pop(0)


def test_info_returns_typed_account_details():
    http = FakeHttp({"id": 1, "name": "Developer", "email": "developer@example.com", "account": {"id": 2, "name": "Acme"}})

    result = Account(http).info()

    assert isinstance(result, AccountInfoResponse)
    assert result.account.name == "Acme"
    assert http.calls == [("get", "/api/v1/me", None, None)]


def test_balance_returns_typed_balance_details():
    http = FakeHttp(
        {
            "balance_cents": 5000,
            "paid_balance_cents": 4000,
            "bonus_balance_cents": 1000,
            "spent_cents_today": 100,
            "spent_cents_total": 2000,
        }
    )

    result = Account(http).balance()

    assert isinstance(result, AccountBalanceResponse)
    assert result.balance_cents == 5000
    assert http.calls == [("get", "/api/v1/me/balance", None, None)]
