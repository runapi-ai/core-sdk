"""Multipart Upload lifecycle client."""

from __future__ import annotations

import os
from typing import Any, Optional, Sequence
from urllib.parse import quote

from .files import FileObject, FilesClient
from .models import BaseModel, optional, required
from .multipart import MultipartBody, MultipartFile
from .options import RequestOptions
from .resource import Resource


class UploadObject(BaseModel):
    id = required(str)
    object = required(str)
    bytes = required(int)
    created_at = required(int)
    filename = required(str)
    purpose = required(str)
    status = required(str)
    expires_at = required(int)
    file = optional(FileObject)


class UploadPart(BaseModel):
    id = required(str)
    object = required(str)
    created_at = required(int)
    upload_id = required(str)


class Uploads(Resource):
    ENDPOINT = "/v1/uploads"
    RESPONSE_CLASS = UploadObject

    def create(
        self,
        *,
        bytes: int,
        filename: str,
        mime_type: str,
        purpose: str = "user_data",
        options: Optional[RequestOptions] = None,
    ) -> UploadObject:
        return self._request("post", self.ENDPOINT, body={
            "bytes": bytes,
            "filename": filename,
            "mime_type": mime_type,
            "purpose": purpose,
        }, options=options)

    def add_part(
        self,
        upload_id: str,
        data: Any,
        file_name: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> UploadPart:
        path = FilesClient._file_path(data)
        body = MultipartBody(files={
            "data": MultipartFile(path=path, filename=file_name or os.path.basename(path))
        })
        return self._request(
            "post", f"{self._upload_path(upload_id)}/parts", body=body,
            options=options, response_class=UploadPart,
        )

    def complete(
        self,
        upload_id: str,
        part_ids: Sequence[str],
        options: Optional[RequestOptions] = None,
    ) -> UploadObject:
        return self._request(
            "post", f"{self._upload_path(upload_id)}/complete",
            body={"part_ids": list(part_ids)}, options=options,
        )

    def cancel(self, upload_id: str, options: Optional[RequestOptions] = None) -> UploadObject:
        return self._request(
            "post", f"{self._upload_path(upload_id)}/cancel", body={}, options=options
        )

    @classmethod
    def _upload_path(cls, upload_id: str) -> str:
        if not upload_id.strip():
            raise ValueError("upload_id is required")
        return f"{cls.ENDPOINT}/{quote(upload_id, safe='')}"
