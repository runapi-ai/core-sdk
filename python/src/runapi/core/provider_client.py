"""Shared foundation for model-line Provider Clients."""

from __future__ import annotations

from typing import Any, Optional

from .account import Account
from .auth import resolve_api_key
from .files import FilesClient
from .http_client import HttpClient
from .options import ClientOptions
from .pricing import Pricing


class ProviderClient:
    """Resolve auth and expose universal resources on every model-line client."""

    def __init__(self, api_key: Optional[str] = None, **options: Any) -> None:
        resolved_api_key = resolve_api_key(api_key)
        client_options = ClientOptions(api_key=resolved_api_key, **options)
        self._http = client_options.http_client or HttpClient(client_options)
        self.files = FilesClient(http=self._http)
        self.account = Account(self._http)
        self.pricing = Pricing(self._http)
