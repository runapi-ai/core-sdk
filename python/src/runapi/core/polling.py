"""Polling loop for async task completion."""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

from .errors import TaskFailedError, TaskTimeoutError
from .models import BaseModel
from .options import PollingOptions

ACTIVE_STATUSES = ("pending", "processing")


def poll_until_complete(fetch: Callable[[], Any], options: Optional[PollingOptions] = None) -> Any:
    """Call ``fetch`` repeatedly until the task completes.

    Returns the completed response. Raises :class:`TaskFailedError` on a failed
    or unknown status, and :class:`TaskTimeoutError` once ``max_wait`` elapses.
    """
    if options is None:
        options = PollingOptions()

    deadline = time.monotonic() + options.max_wait

    while True:
        response = fetch()
        status = str(_value_for(response, "status") or "").lower()

        if status == "completed":
            return response

        if status == "failed":
            message = _value_for(response, "error") or "Task failed"
            raise TaskFailedError(message, details=_details_for(response))

        if time.monotonic() >= deadline:
            raise TaskTimeoutError(f"Task polling timed out after {options.max_wait}s")

        if status not in ACTIVE_STATUSES:
            raise TaskFailedError(f"Unknown task status: {status}", details=_details_for(response))

        time.sleep(options.poll_interval)


def _value_for(response: Any, key: str) -> Any:
    if isinstance(response, BaseModel):
        return response[key]
    if isinstance(response, dict):
        return response.get(key)
    return None


def _details_for(response: Any) -> Any:
    return response.to_dict() if isinstance(response, BaseModel) else response
