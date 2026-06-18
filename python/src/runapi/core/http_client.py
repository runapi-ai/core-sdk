"""HTTP transport built on ``httpx.Client`` with retries and multipart support."""

from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

from . import constants
from .errors import NetworkError, RateLimitError, TimeoutError, error_from_response
from .multipart import MultipartBody
from .options import ClientOptions, RequestOptions

_NO_BODY = object()


class HttpClient:
    """Synchronous HTTP client.

    ``httpx.Client`` keeps connections alive across requests, so no explicit
    connection pool is needed. Pass ``transport`` to inject an
    ``httpx.MockTransport`` in tests.
    """

    def __init__(self, options: ClientOptions, *, transport: Optional[httpx.BaseTransport] = None) -> None:
        self._options = options
        self._client = httpx.Client(
            base_url=options.base_url,
            timeout=options.timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {options.api_key}",
                "Accept": "application/json",
                "User-Agent": constants.SDK_USER_AGENT,
            },
        )

    def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        max_retries = self._options.max_retries
        if options is not None and options.max_retries is not None:
            max_retries = options.max_retries

        headers = {str(key): str(value) for key, value in (options.headers or {}).items()} if options else {}
        timeout = options.timeout if (options and options.timeout is not None) else httpx.USE_CLIENT_DEFAULT

        json_body, data, files, opened = self._build_payload(body)
        method = method.upper()
        retries = 0

        try:
            while True:
                try:
                    response = self._client.request(
                        method,
                        path,
                        json=json_body,
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=timeout,
                    )
                except httpx.TimeoutException as exc:
                    raise TimeoutError(str(exc))
                except httpx.TransportError as exc:
                    raise NetworkError(str(exc))

                if response.is_success:
                    return self._parse_body(response.text)

                error = error_from_response(response)
                if self._retryable(method, response.status_code) and retries < max_retries:
                    retries += 1
                    time.sleep(self._retry_delay(retries, error))
                    continue

                raise error
        finally:
            for handle in opened:
                handle.close()

    def close(self) -> None:
        self._client.close()

    def _build_payload(
        self, body: Any
    ) -> Tuple[Any, Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Any]]:
        if isinstance(body, MultipartBody):
            data = {key: str(value) for key, value in body.fields.items()}
            files: Dict[str, Any] = {}
            opened: List[Any] = []
            for key, part in body.files.items():
                handle = open(part.path, "rb")
                opened.append(handle)
                filename = part.filename
                if part.content_type:
                    files[key] = (filename, handle, part.content_type)
                else:
                    files[key] = (filename, handle)
            return None, data, files, opened
        if body is not None:
            return body, None, None, []
        return None, None, None, []

    def _retryable(self, method: str, status: int) -> bool:
        return method in constants.IDEMPOTENT_METHODS and status in constants.RETRYABLE_STATUS_CODES

    def _retry_delay(self, attempt: int, error: Any) -> float:
        if isinstance(error, RateLimitError) and error.retry_after and error.retry_after > 0:
            return error.retry_after
        base = self._options.retry_base_delay * (2 ** (attempt - 1))
        jitter = random.random() * base * 0.5
        return min(base + jitter, self._options.retry_max_delay)

    @staticmethod
    def _parse_body(body: Optional[str]) -> Any:
        if not body:
            return None
        try:
            return json.loads(body)
        except ValueError:
            return body
