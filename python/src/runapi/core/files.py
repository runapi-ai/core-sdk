"""File upload client.

Shared infrastructure for every model line that takes file inputs: upload a
local file or register a remote URL and receive a usable file reference.
"""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any, Mapping, Optional, Union

from . import auth
from .http_client import HttpClient
from .models import BaseModel, optional, required
from .options import ClientOptions, RequestOptions
from .resource import Resource


class UploadResponse(BaseModel):
    file_name = required(str)
    url = required(str)
    size_bytes = required(int)
    mime_type = required(str)
    created_at = required(str)
    expires_at = required(str)


class FilesClient(Resource):
    ENDPOINT = "/api/v1/files"
    PREPARE_ENDPOINT = f"{ENDPOINT}/prepare"
    CONFIRM_ENDPOINT = f"{ENDPOINT}/confirm"

    RESPONSE_CLASS = UploadResponse

    def __init__(self, api_key: Optional[str] = None, **options: Any) -> None:
        resolved_api_key = auth.resolve_api_key(api_key)
        client_options = ClientOptions(api_key=resolved_api_key, **options)
        http = client_options.http_client or HttpClient(client_options)
        super().__init__(http)

    def create(
        self,
        file: Any = None,
        source: Optional[Union[str, Mapping[str, Any]]] = None,
        file_name: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        """Upload a local ``file`` (path or file-like) or register a remote ``source`` URL.

        Exactly one of ``file`` or ``source`` is required.

        Args:
            file: Local file path or file-like object to upload.
            source: Remote URL, base64 data, or canonical source object to
                register instead of uploading a local file.
            file_name: Optional name to record for the uploaded file.
            options: Optional per-request options.

        Returns:
            The upload response with the usable file reference.
        """
        self._validate_source(file, source)

        if file is not None:
            return self._upload_direct(file, file_name, options)

        body = self._compact_params(
            {"source": self._source_object(source), "file_name": file_name}
        )
        return self._request("post", self.ENDPOINT, body=body, options=options)

    def _upload_direct(self, file: Any, file_name: Optional[str], options: Optional[RequestOptions]) -> Any:
        """Local files upload straight to storage: ask for a pre-authorized target,
        PUT the bytes there (never through the API), then confirm. The caller still
        makes a single create call."""
        path = self._file_path(file)
        with open(path, "rb") as handle:
            data = handle.read()

        prepared = self._http.request(
            "post",
            self.PREPARE_ENDPOINT,
            body=self._compact_params(
                {
                    "filename": file_name or os.path.basename(path),
                    "byte_size": len(data),
                    "checksum": base64.b64encode(hashlib.md5(data).digest()).decode("ascii"),
                }
            ),
            options=options,
        )

        self._http.upload(prepared["upload_url"], headers=prepared["headers"], body=data)

        return self._request(
            "post", self.CONFIRM_ENDPOINT, body={"signed_id": prepared["signed_id"]}, options=options
        )

    @staticmethod
    def _validate_source(file: Any, source: Optional[Union[str, Mapping[str, Any]]]) -> None:
        def present(value: Any) -> bool:
            if value is None:
                return False
            if isinstance(value, str):
                return value.strip() != ""
            return True

        provided = sum(1 for value in (file, source) if present(value))
        if provided != 1:
            raise ValueError("Exactly one source is required: file or source")

    @staticmethod
    def _source_object(source: Optional[Union[str, Mapping[str, Any]]]) -> Any:
        if isinstance(source, Mapping):
            return dict(source)

        if isinstance(source, str):
            value = source.strip()
            if value.lower().startswith(("http://", "https://")):
                return {"type": "url", "url": value}
            return {"type": "base64", "data": value}

        return source

    @staticmethod
    def _file_path(file: Any) -> str:
        if isinstance(file, str):
            return file
        # pathlib.Path (and any os.PathLike) must keep their full path; Path.name
        # would return only the basename, breaking the later open().
        if isinstance(file, os.PathLike):
            return os.fspath(file)
        name = getattr(file, "name", None)
        if name:
            return name
        raise ValueError("file must be a file path or a file-like object with a name")
