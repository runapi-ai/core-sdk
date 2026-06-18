"""Client, request, and polling option dataclasses."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from . import config, constants


@dataclass
class ClientOptions:
    """Configuration for an API client.

    ``http_client`` lets callers inject a custom transport (for tests or
    advanced use). When set, the SDK delegates all HTTP calls to it instead of
    building its own :class:`HttpClient`. It must expose
    ``request(method, path, body=None, options=None)``.
    """

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_base_delay: Optional[float] = None
    retry_max_delay: Optional[float] = None
    http_client: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.base_url is None:
            self.base_url = config.base_url
        if self.timeout is None:
            self.timeout = constants.HTTP_REQUEST_TIMEOUT
        if self.max_retries is None:
            self.max_retries = constants.MAX_RETRIES
        if self.retry_base_delay is None:
            self.retry_base_delay = constants.RETRY_BASE_DELAY
        if self.retry_max_delay is None:
            self.retry_max_delay = constants.RETRY_MAX_DELAY


@dataclass
class RequestOptions:
    """Per-request overrides of client-level defaults."""

    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    max_retries: Optional[int] = None


@dataclass
class PollingOptions:
    """Options for polling async task completion."""

    poll_interval: int = field(default=constants.POLLING_INTERVAL)
    max_wait: int = field(default=constants.POLLING_MAX_WAIT)
