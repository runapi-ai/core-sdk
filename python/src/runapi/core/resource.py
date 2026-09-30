"""Base class for API resources: request coercion, param helpers, polling."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

from . import polling
from .errors import TaskFailedError, ValidationError, _parse_retry_after, error_from_response_data
from .models import BaseModel, TaskResult, TaskResponse
from .options import PollingOptions, RequestOptions
from .response import ApiResponse


class Resource:
    """Shared behavior for resource classes.

    Subclasses set ``RESPONSE_CLASS`` (the typed model for responses) and
    optionally ``COMPLETED_RESPONSE_CLASS`` (a narrowed model that ``run()``
    re-coerces to once the task completes).
    """

    RESPONSE_CLASS: Optional[type] = TaskResponse
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
        return self._coerce_response(response, response_class)

    def _coerce_response(self, response: Any, response_class: Optional[type] = None) -> Any:
        payload = response.body if isinstance(response, ApiResponse) else response
        target = response_class or type(self).RESPONSE_CLASS
        result = payload if target is None else BaseModel.coerce(payload, as_=target)
        if isinstance(response, ApiResponse):
            self._attach_response_headers(result, response.response_headers)
        return result

    def _run_hybrid(
        self,
        method: str,
        path: str,
        body: Any = None,
        options: Optional[RequestOptions] = None,
        polling_options: Optional[PollingOptions] = None,
    ) -> Any:
        """Run a terminal-or-accepted Task endpoint through one stable API."""
        request_options = self._with_idempotency_key(options) if method.upper() == "POST" else options
        response = self._http.request(method, path, body=body, options=request_options)
        if isinstance(response, ApiResponse) and response.status_code == 202:
            location = response.response_headers.get("Location")
            if not location:
                raise TaskFailedError(
                    "Accepted Task response is missing Location",
                    response_headers=response.response_headers,
                )
            return self.subscribe(
                location,
                options=request_options,
                polling_options=polling_options,
                initial_delay=self._retry_after(response.response_headers),
            )
        return self._coerce_response(response)

    def subscribe(
        self,
        location: str,
        *,
        options: Optional[RequestOptions] = None,
        polling_options: Optional[PollingOptions] = None,
        initial_delay: Optional[float] = None,
    ) -> Any:
        """Follow an opaque Task Result URL until its stored terminal response is ready."""
        return self._poll_until_complete(
            lambda: self._request("get", location, options=options, response_class=TaskResult),
            polling_options,
            initial_delay=initial_delay,
            completed=self._decode_task_result,
            failed=self._task_result_error,
        )

    def _with_idempotency_key(self, options: Optional[RequestOptions]) -> RequestOptions:
        headers = {}
        idempotency_key = None
        source_headers = (options.headers or {}) if options else {}
        for name, value in source_headers.items():
            if name.lower() != "idempotency-key":
                headers[name] = value
                continue

            normalized = str(value).strip()
            if not normalized:
                continue
            if idempotency_key is not None and idempotency_key != normalized:
                raise ValidationError("conflicting Idempotency-Key headers")
            idempotency_key = normalized

        headers["Idempotency-Key"] = idempotency_key or str(uuid4())
        return replace(options, headers=headers) if options else RequestOptions(headers=headers)

    def _decode_task_result(self, task: TaskResult) -> Any:
        response = task.response
        if response is None:
            raise TaskFailedError("Completed Task is missing its terminal response", details=task.to_dict())
        if not 200 <= response.status < 300:
            raise self._task_result_error(task)

        body = self._plain_value(response.body)
        content_type = response.content_type.lower().split(";", 1)[0].strip()
        if content_type == "application/json" or content_type.endswith("+json"):
            response_class = type(self).RESPONSE_CLASS
            result = body if response_class is None else BaseModel.coerce(body, as_=response_class)
            self._attach_response_headers(result, response.headers or {})
            return result
        if self._textual_content_type(content_type):
            if isinstance(body, bytes):
                return body.decode("utf-8")
            return "" if body is None else str(body)
        if isinstance(body, bytes):
            return body
        if isinstance(body, str):
            return body.encode("utf-8")
        return body

    def _task_result_error(self, task: TaskResult) -> Exception:
        response = task.response
        if response is None:
            return TaskFailedError("Task failed without a terminal response", details=task.to_dict())
        return error_from_response_data(
            response.status,
            self._plain_value(response.body),
            response.headers or {},
        )

    def _poll_until_complete(
        self,
        fetch: Callable[[], Any],
        polling_opts: Optional[PollingOptions] = None,
        **kwargs: Any,
    ) -> Any:
        response = polling.poll_until_complete(fetch, polling_opts or PollingOptions(), **kwargs)

        if kwargs.get("completed"):
            return response

        completed_class = type(self).COMPLETED_RESPONSE_CLASS
        if completed_class is None or isinstance(response, completed_class):
            return response

        payload = response.to_dict() if isinstance(response, BaseModel) else response
        completed = completed_class.from_dict(payload)
        if isinstance(response, BaseModel):
            completed._with_response_headers(response.response_headers)
        return completed

    @staticmethod
    def _plain_value(value: Any) -> Any:
        return value.to_dict() if isinstance(value, BaseModel) else value

    @staticmethod
    def _textual_content_type(content_type: str) -> bool:
        return content_type.startswith("text/") or content_type in {"application/srt", "application/x-subrip"}

    @staticmethod
    def _retry_after(headers: Any) -> Optional[float]:
        delay = _parse_retry_after(headers.get("Retry-After") if headers else None)
        return delay if delay and delay > 0 else None

    @staticmethod
    def _compact_params(params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in params.items()
            if not (value is None or (isinstance(value, str) and value.strip() == ""))
        }

    def _attach_response_headers(self, result: Any, headers: Any) -> None:
        if isinstance(result, BaseModel):
            result._with_response_headers(headers)
        elif isinstance(result, list):
            for item in result:
                self._attach_response_headers(item, headers)
