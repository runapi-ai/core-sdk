"""Base class for API resources: request coercion, param helpers, polling."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence

from . import polling
from .errors import ValidationError
from .models import BaseModel, TaskResponse
from .options import PollingOptions, RequestOptions


class Resource:
    """Shared behavior for resource classes.

    Subclasses set ``RESPONSE_CLASS`` (the typed model for responses) and
    optionally ``COMPLETED_RESPONSE_CLASS`` (a narrowed model that ``run()``
    re-coerces to once the task completes).
    """

    RESPONSE_CLASS: type = TaskResponse
    COMPLETED_RESPONSE_CLASS: Optional[type] = None

    def __init__(self, http: Any) -> None:
        self._http = http

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        options: Optional[RequestOptions] = None,
        response_class: Optional[type] = None,
    ) -> Any:
        response = self._http.request(method, path, body=body, options=options)
        return BaseModel.coerce(response, as_=response_class or type(self).RESPONSE_CLASS)

    @staticmethod
    def _compact_params(params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in params.items()
            if not (value is None or (isinstance(value, str) and value.strip() == ""))
        }

    @staticmethod
    def _validate_optional(params: Dict[str, Any], key: str, allowed: Sequence[Any]) -> None:
        value = params.get(key)
        if value is None:
            return
        if value not in allowed:
            joined = ", ".join(str(option) for option in allowed)
            raise ValidationError(f"Invalid {key}: {value}. Must be one of: {joined}")

    def _poll_until_complete(
        self, fetch: Callable[[], Any], polling_opts: Optional[PollingOptions] = None
    ) -> Any:
        response = polling.poll_until_complete(fetch, polling_opts or PollingOptions())

        completed_class = type(self).COMPLETED_RESPONSE_CLASS
        if completed_class is None or isinstance(response, completed_class):
            return response

        payload = response.to_dict() if isinstance(response, BaseModel) else response
        return completed_class.from_dict(payload)
