"""Multipart upload payloads."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MultipartFile:
    path: str
    filename: Optional[str] = None
    content_type: Optional[str] = None


class MultipartBody:
    """A multipart/form-data request body of plain fields plus file parts."""

    def __init__(
        self,
        fields: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, MultipartFile]] = None,
    ) -> None:
        self.fields: Dict[str, Any] = {str(key): value for key, value in (fields or {}).items()}
        self.files: Dict[str, MultipartFile] = {str(key): value for key, value in (files or {}).items()}
