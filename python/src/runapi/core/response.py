"""Response metadata containers shared by transports and typed models."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Optional


class ResponseHeaders(Mapping[str, str]):
    """Case-insensitive response headers."""

    def __init__(self, headers: Optional[Mapping[str, Any]] = None) -> None:
        self._headers = {str(key).lower(): str(value) for key, value in (headers or {}).items()}

    def __getitem__(self, key: str) -> str:
        return self._headers[str(key).lower()]

    def __iter__(self) -> Iterator[str]:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def get(self, key: str, default: Any = None) -> Any:
        return self._headers.get(str(key).lower(), default)

    def to_dict(self) -> dict[str, str]:
        return dict(self._headers)


class ApiResponse(dict[str, Any]):
    """Parsed response body plus HTTP response headers.

    The object delegates common body access so existing direct transport users
    that index the returned JSON body keep working.
    """

    def __init__(self, body: Mapping[str, Any] | Sequence[Any], headers: Optional[Mapping[str, Any]] = None) -> None:
        super().__init__(body if isinstance(body, Mapping) else {})
        self.body = self if isinstance(body, Mapping) else body
        self.response_headers = headers if isinstance(headers, ResponseHeaders) else ResponseHeaders(headers)
        self.headers = self.response_headers

    def __getitem__(self, key: Any) -> Any:
        if self.body is not self:
            return self.body[key]  # type: ignore[index]
        return super().__getitem__(key)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ApiResponse):
            left = dict(self) if self.body is self else self.body
            right = dict(other) if other.body is other else other.body
            return left == right
        if self.body is self:
            return dict(self) == other
        return self.body == other
