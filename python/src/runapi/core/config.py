"""Module-level configuration shared across RunAPI clients.

Mirrors Ruby's global ``RunApi.api_key`` / ``RunApi.base_url``. Values are read
at request time, so ``configure()`` (or assigning these attributes directly)
affects clients constructed afterwards.
"""

import sys
from typing import Optional

from .constants import DEFAULT_BASE_URL

api_key: Optional[str] = None
base_url: str = DEFAULT_BASE_URL


def configure(api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
    """Set global configuration. Only non-None arguments are applied."""
    module = sys.modules[__name__]
    if api_key is not None:
        module.api_key = api_key
    if base_url is not None:
        module.base_url = base_url
