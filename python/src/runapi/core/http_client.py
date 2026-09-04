"""HTTP transport built on ``httpx.Client`` with retries and multipart support."""

from __future__ import annotations

import json
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

import httpx

from . import constants
from .errors import NetworkError, RateLimitError, TimeoutError, ValidationError, error_from_response
from .multipart import MultipartBody
from .options import ClientOptions, RequestOptions
from .response import ApiResponse

_NO_BODY = object()


class HttpClient:
    """Synchronous HTTP client.

    ``httpx.Client`` keeps connections alive across requests, so no explicit
    connection pool is needed. Pass ``transport`` to inject an
    ``httpx.MockTransport`` in tests.
    """

    def __init__(self, options: ClientOptions, *, transport: Optional[httpx.BaseTransport] = None) -> None:
        self._options = options
        headers = {
            "Accept": "application/json",
            "User-Agent": constants.SDK_USER_AGENT,
        }
        if options.api_key:
            headers["Authorization"] = f"Bearer {options.api_key}"
        self._client = httpx.Client(
            base_url=options.base_url,
            timeout=options.timeout,
            transport=transport,
            headers=headers,
        )
        # A bare client for direct uploads: the pre-authorized upload URL lives
        # outside the API host and must not receive the API key.
        self._upload_client = httpx.Client(timeout=options.timeout, transport=transport)

    def request(
        self,
        method: str,
        path: str,
        body: Any = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        self._validate_request_url(path)
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
                    if self._retryable_request(method, headers) and retries < max_retries:
                        retries += 1
                        time.sleep(self._retry_delay(retries, TimeoutError(str(exc))))
                        continue
                    raise TimeoutError(str(exc))
                except httpx.TransportError as exc:
                    if self._retryable_request(method, headers) and retries < max_retries:
                        retries += 1
                        time.sleep(self._retry_delay(retries, NetworkError(str(exc))))
                        continue
                    raise NetworkError(str(exc))

                if response.status_code == 304:
                    return None

                if response.is_success:
                    body = self._parse_body(response.text)
                    if body is None:
                        return None
                    if isinstance(body, (dict, list)):
                        return ApiResponse(body, response.headers, status_code=response.status_code)
                    return body

                error = error_from_response(response)
                if (
                    self._retryable_request(method, headers)
                    and response.status_code in constants.RETRYABLE_STATUS_CODES
                    and retries < max_retries
                ):
                    retries += 1
                    time.sleep(self._retry_delay(retries, error))
                    continue

                raise error
        finally:
            for handle in opened:
                handle.close()

    def upload(self, url: str, headers: Dict[str, str], body: bytes) -> None:
        """PUT bytes straight to a pre-authorized upload URL with the exact headers
        issued for it. No auth, no retries: the URL is single-use and the body is
        not safe to replay."""
        try:
            response = self._upload_client.put(url, content=body, headers=headers)
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc))
        except httpx.TransportError as exc:
            raise NetworkError(str(exc))

        if not response.is_success:
            raise error_from_response(response)

    def request_bytes(
        self,
        method: str,
        path: str,
        options: Optional[RequestOptions] = None,
    ) -> bytes:
        """Return a successful response body without text decoding."""
        self._validate_request_url(path)
        max_retries = self._options.max_retries
        if options is not None and options.max_retries is not None:
            max_retries = options.max_retries
        headers = {str(key): str(value) for key, value in (options.headers or {}).items()} if options else {}
        timeout = options.timeout if (options and options.timeout is not None) else httpx.USE_CLIENT_DEFAULT
        method = method.upper()
        retries = 0

        while True:
            try:
                response = self._client.request(method, path, headers=headers, timeout=timeout)
            except httpx.TimeoutException as exc:
                raise TimeoutError(str(exc))
            except httpx.TransportError as exc:
                raise NetworkError(str(exc))
            if response.is_success:
                return response.content
            error = error_from_response(response)
            if (
                self._retryable_request(method, headers)
                and response.status_code in constants.RETRYABLE_STATUS_CODES
                and retries < max_retries
            ):
                retries += 1
                time.sleep(self._retry_delay(retries, error))
                continue
            raise error

    def close(self) -> None:
        self._client.close()
        self._upload_client.close()

    def _build_payload(
        self, body: Any
    ) -> Tuple[Any, Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Any]]:
        if isinstance(body, MultipartBody):
            files = []
            for key, value in body.fields.items():
                values = value if isinstance(value, (list, tuple)) else [value]
                files.extend((key, (None, str(item))) for item in values)
            opened: List[Any] = []
            for key, part in body.files.items():
                handle = open(part.path, "rb")
                opened.append(handle)
                filename = part.filename
                if part.content_type:
                    files.append((key, (filename, handle, part.content_type)))
                else:
                    files.append((key, (filename, handle)))
            return None, None, files, opened
        if body is not None:
            return body, None, None, []
        return None, None, None, []

    def _retryable_request(self, method: str, headers: Dict[str, str]) -> bool:
        return method in constants.IDEMPOTENT_METHODS or (
            method == "POST"
            and any(name.lower() == "idempotency-key" and str(value).strip() for name, value in headers.items())
        )

    def _validate_request_url(self, path: str) -> None:
        requested = urlsplit(path)
        if not requested.scheme and not requested.netloc:
            return
        configured = urlsplit(str(self._options.base_url))
        if self._origin(requested) != self._origin(configured):
            raise ValidationError("Request URL must use the configured RunAPI origin")

    @staticmethod
    def _origin(url: Any) -> Tuple[str, str, Optional[int]]:
        scheme = url.scheme.lower()
        port = url.port or ({"http": 80, "https": 443}.get(scheme))
        return scheme, (url.hostname or "").lower(), port

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
