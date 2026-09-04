"""Polling loop for async task completion."""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

from .errors import TaskFailedError, TaskTimeoutError, _parse_retry_after
from .models import BaseModel
from .options import PollingOptions

ACTIVE_STATUSES = ("pending", "processing")


def poll_until_complete(
    fetch: Callable[[], Any],
    options: Optional[PollingOptions] = None,
    *,
    initial_delay: Optional[float] = None,
    completed: Optional[Callable[[Any], Any]] = None,
    failed: Optional[Callable[[Any], Exception]] = None,
) -> Any:
    """Call ``fetch`` repeatedly until the task completes.

    Returns the completed response. Raises :class:`TaskFailedError` on a failed
    or unknown status, and :class:`TaskTimeoutError` once ``max_wait`` elapses.
    """
    if options is None:
        options = PollingOptions()

    deadline = time.monotonic() + options.max_wait
    wait = initial_delay
    response = None

    while True:
        if wait and wait > 0:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise _timeout_error(options, response)
            time.sleep(min(wait, remaining))

        if (response is not None or (wait and wait > 0)) and time.monotonic() >= deadline:
            raise _timeout_error(options, response)

        response = fetch()
        if time.monotonic() >= deadline:
            raise _timeout_error(options, response)
        status = str(_value_for(response, "status") or "").lower()

        if status == "completed":
            return completed(response) if completed else response

        if status == "failed":
            if failed:
                raise failed(response)
            message = _value_for(response, "error") or "Task failed"
            raise TaskFailedError(
                message,
                details=_details_for(response),
                response_headers=_response_headers_for(response),
            )

        if status not in ACTIVE_STATUSES:
            raise TaskFailedError(
                f"Unknown task status: {status}",
                details=_details_for(response),
                response_headers=_response_headers_for(response),
            )

        wait = _retry_after_for(response) or options.poll_interval


def _timeout_error(options: PollingOptions, response: Any) -> TaskTimeoutError:
    return TaskTimeoutError(
        f"Task polling timed out after {options.max_wait}s",
        details=_details_for(response) if response is not None else None,
        response_headers=_response_headers_for(response) if response is not None else None,
    )


def _value_for(response: Any, key: str) -> Any:
    if isinstance(response, BaseModel):
        return response[key]
    if isinstance(response, dict):
        return response.get(key)
    return None


def _details_for(response: Any) -> Any:
    return response.to_dict() if isinstance(response, BaseModel) else response


def _response_headers_for(response: Any) -> Any:
    return response.response_headers if hasattr(response, "response_headers") else None


def _retry_after_for(response: Any) -> Optional[float]:
    headers = _response_headers_for(response)
    delay = _parse_retry_after(headers.get("Retry-After") if headers else None)
    return delay if delay and delay > 0 else None
