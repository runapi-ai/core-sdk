"""Error hierarchy and HTTP-response-to-error mapping for the RunAPI SDK."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional

from .response import ResponseHeaders

_HTML_MARKER = re.compile(r"<!doctype|<html", re.IGNORECASE)
_TITLE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_H1 = re.compile(r"<h1>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_ENTITY = re.compile(r"&[a-z]+;", re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")


class Error(Exception):
    """Base error for all RunAPI SDK failures.

    Carries the HTTP status, request id, and parsed response details when
    available.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        status: Optional[int] = None,
        request_id: Optional[str] = None,
        details: Any = None,
        response_headers: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.request_id = request_id
        self.details = details
        self.response_headers = (
            response_headers if isinstance(response_headers, ResponseHeaders) else ResponseHeaders(response_headers)
        )

    def response_header(self, name: str) -> Optional[str]:
        return self.response_headers.get(name)

    @property
    def runapi_task_id(self) -> Optional[str]:
        return self.response_header("X-RunAPI-Task-Id")

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "error": type(self).__name__,
            "message": self.message,
            "status": self.status,
            "request_id": self.request_id,
            "details": self.details,
        }
        return {key: value for key, value in data.items() if value is not None}


class AuthenticationError(Error):
    """API key is missing or invalid (HTTP 401)."""

    def __init__(self, message: str = "Unauthorized", *, status: int = 401, **kwargs: Any) -> None:
        super().__init__(message, status=status, **kwargs)


class RateLimitError(Error):
    """Rate limit exceeded (HTTP 429). Includes the retry-after delay."""

    def __init__(
        self,
        message: str = "Too many requests",
        *,
        status: int = 429,
        retry_after: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status=status, **kwargs)
        self.retry_after = retry_after


class InsufficientCreditsError(Error):
    """Account has insufficient credits (HTTP 402)."""

    def __init__(self, message: str = "Insufficient credits", *, status: int = 402, **kwargs: Any) -> None:
        super().__init__(message, status=status, **kwargs)


class NotFoundError(Error):
    """Requested resource does not exist (HTTP 404)."""

    def __init__(self, message: str = "Not found", *, status: int = 404, **kwargs: Any) -> None:
        super().__init__(message, status=status, **kwargs)


class ValidationError(Error):
    """Request validation failed (HTTP 400 / 422), or a client-side check failed."""

    def __init__(self, message: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class ServiceUnavailableError(Error):
    """Service is temporarily unavailable (HTTP 503)."""

    def __init__(self, message: str = "Service unavailable", *, status: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(message, status=503 if status is None else status, **kwargs)


class ConflictError(Error):
    """Request conflicts with the current resource state (HTTP 409)."""

    def __init__(self, message: str = "Conflict", *, status: int = 409, **kwargs: Any) -> None:
        super().__init__(message, status=status, **kwargs)


class ServerError(Error):
    """Server encountered an internal error (HTTP 5xx)."""

    def __init__(self, message: str = "Server error", *, status: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(message, status=500 if status is None else status, **kwargs)


class NetworkError(Error):
    """Network connection failed or the request could not be sent."""

    def __init__(self, message: str = "Network error", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class TimeoutError(Error):  # noqa: A001 - intentional SDK error name, parallels other SDKs
    """HTTP request exceeded the configured timeout."""

    def __init__(self, message: str = "Request timed out", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class TaskTimeoutError(Error):
    """Polling for task completion exceeded the maximum wait time."""

    def __init__(self, message: str = "Task polling timed out", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


class TaskFailedError(Error):
    """Async task failed during processing."""

    def __init__(self, message: str = "Task failed", **kwargs: Any) -> None:
        super().__init__(message, **kwargs)


STATUS_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    501: ServerError,
    502: ServerError,
    503: ServiceUnavailableError,
    504: ServerError,
    505: ServerError,
}

DEFAULT_MESSAGES = {
    400: "Bad request",
    401: "Unauthorized",
    402: "Insufficient credits",
    404: "Not found",
    408: "Request timeout",
    409: "Conflict",
    413: "Payload too large",
    415: "Unsupported media type",
    422: "Validation failed",
    429: "Too many requests",
    503: "Service unavailable",
}


def error_from_response(response: "Any") -> Error:
    """Build the appropriate error from an ``httpx.Response``.

    Maps the status code to a specific error class and extracts the message,
    request id, response details, and (for 429) the retry-after delay.
    """
    status = response.status_code
    request_id = response.headers.get("x-request-id")

    parsed_body = _parse_body(response.text)
    message = _extract_message(parsed_body) or DEFAULT_MESSAGES.get(status) or "Request failed"

    error_class = STATUS_MAP.get(status, Error)

    kwargs: Dict[str, Any] = {
        "status": status,
        "request_id": request_id,
        "details": parsed_body,
        "response_headers": response.headers,
    }
    if error_class is RateLimitError:
        kwargs["retry_after"] = _parse_retry_after(response.headers.get("retry-after"))

    return error_class(message, **kwargs)


def _parse_body(body: Optional[str]) -> Any:
    if not body:
        return None
    if _HTML_MARKER.search(body):
        return _extract_html_error(body)
    try:
        return json.loads(body)
    except ValueError:
        return body


def _extract_html_error(html: str) -> Dict[str, Any]:
    match = _TITLE.search(html) or _H1.search(html)
    error_text = match.group(1) if match else "HTML Error Page"
    error_text = _TAG.sub("", _ENTITY.sub(" ", error_text)).strip()
    return {
        "error": error_text,
        "is_html_error": True,
        "message": f"Server returned HTML error page: {error_text}",
    }


def _extract_message(body: Any) -> Optional[str]:
    if not isinstance(body, dict):
        return None

    error = body.get("error")
    if isinstance(error, dict):
        message = error.get("message")
    else:
        message = error

    if message:
        return message

    errors = body.get("errors")
    if isinstance(errors, list) and errors:
        first = errors[0]
        return first.get("message") if isinstance(first, dict) else first

    return body.get("message") or body.get("detail") or body.get("errorMessage") or body.get("msg")


def _parse_retry_after(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        pass

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return (parsed - datetime.now(timezone.utc)).total_seconds()
