"""API key resolution."""

import os
from typing import Optional

from . import config
from .errors import AuthenticationError

ENV_VAR_NAME = "RUNAPI_API_KEY"

MISSING_KEY_MESSAGE = (
    "API key is required. Pass api_key or set the RUNAPI_API_KEY environment variable."
)


def resolve_api_key(explicit: Optional[str] = None) -> str:
    """Resolve the API key, in priority order:

    1. the explicit argument
    2. the global ``runapi.core`` configuration (``config.api_key``)
    3. the ``RUNAPI_API_KEY`` environment variable

    All sources are trimmed; blank values are treated as missing. Raises
    :class:`AuthenticationError` when no source yields a value.
    """
    resolved = resolve_optional_api_key(explicit)
    if not resolved:
        raise AuthenticationError(MISSING_KEY_MESSAGE)
    return resolved


def resolve_optional_api_key(explicit: Optional[str] = None) -> Optional[str]:
    """Resolve an API key without requiring one for public resources."""
    return _normalize(explicit) or _normalize(config.api_key) or _normalize(os.environ.get(ENV_VAR_NAME))


def _normalize(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    return trimmed or None
