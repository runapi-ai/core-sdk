import base64
import hashlib
import os
import tempfile

import pytest

from runapi.core import FilesClient


PREPARED = {
    "signed_id": "signed-blob-id",
    "upload_url": "https://file.runapi.ai/temp/user-uploads/key",
    "headers": {"Content-Type": "application/octet-stream"},
}


class FakeHttp:
    def __init__(self, response):
        self._response = response
        self.calls = []
        self.uploads = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body))
        if path.endswith("/prepare"):
            return PREPARED
        return self._response

    def upload(self, url, headers, body):
        self.uploads.append((url, headers, body))


UPLOAD = {
    "file_name": "image.png",
    "url": "https://cdn.runapi.ai/x.png",
    "size_bytes": 3,
    "mime_type": "image/png",
    "created_at": "2026-01-01T00:00:00Z",
    "expires_at": "2026-01-08T00:00:00Z",
}


def test_requires_exactly_one_source():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)
    with pytest.raises(ValueError):
        client.create()
    with pytest.raises(ValueError):
        client.create(file="x", source="y")


def test_create_with_remote_source_sends_url_source_object():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)
    result = client.create(source="https://runapi.ai/in.png")

    method, path, body = fake.calls[0]
    assert method == "post"
    assert path == "/api/v1/files"
    assert body == {"source": {"type": "url", "url": "https://runapi.ai/in.png"}}
    assert result.url == UPLOAD["url"]
    assert result.size_bytes == 3


def test_create_with_uppercase_url_scheme_sends_url_source_object():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    client.create(source="HTTPS://cdn.runapi.ai/public/samples/in.png")

    _, _, body = fake.calls[0]
    assert body == {"source": {"type": "url", "url": "HTTPS://cdn.runapi.ai/public/samples/in.png"}}


def test_create_with_base64_source_sends_base64_source_object():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)
    source = "cG5n"

    client.create(source=source, file_name="image.png")

    _, _, body = fake.calls[0]
    assert body == {
        "source": {"type": "base64", "data": source},
        "file_name": "image.png",
    }


def test_create_with_source_object_sends_canonical_source_object():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    client.create(source={"type": "url", "url": "https://cdn.runapi.ai/public/samples/in.png"})

    _, _, body = fake.calls[0]
    assert body == {"source": {"type": "url", "url": "https://cdn.runapi.ai/public/samples/in.png"}}


def test_create_with_local_file_uploads_directly():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as handle:
        handle.write(b"png")
        path = handle.name
    try:
        result = client.create(file=path)
    finally:
        os.unlink(path)

    # prepare then confirm; bytes never travel through the API
    assert [call[1] for call in fake.calls] == ["/api/v1/files/prepare", "/api/v1/files/confirm"]
    _, _, prepare_body = fake.calls[0]
    assert prepare_body["filename"] == os.path.basename(path)
    assert prepare_body["byte_size"] == 3
    assert prepare_body["checksum"] == base64.b64encode(hashlib.md5(b"png").digest()).decode("ascii")

    # bytes go straight to the issued upload URL with its headers
    assert fake.uploads == [(PREPARED["upload_url"], PREPARED["headers"], b"png")]

    _, _, confirm_body = fake.calls[1]
    assert confirm_body == {"signed_id": "signed-blob-id"}
    assert result.url == UPLOAD["url"]


def test_create_uses_explicit_file_name():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as handle:
        handle.write(b"png")
        path = handle.name
    try:
        client.create(file=path, file_name="custom.png")
    finally:
        os.unlink(path)

    _, _, prepare_body = fake.calls[0]
    assert prepare_body["filename"] == "custom.png"


def test_create_with_pathlib_path_keeps_full_path():
    # Regression: a pathlib.Path must keep its full path, not collapse to the
    # basename (Path.name), so the later open() reads the right file.
    import pathlib

    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)
    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as handle:
        handle.write(b"png")
        path = handle.name
    try:
        client.create(file=pathlib.Path(path))
    finally:
        os.unlink(path)

    # the full path was read (checksum of the real bytes), not a basename miss
    _, _, prepare_body = fake.calls[0]
    assert prepare_body["checksum"] == base64.b64encode(hashlib.md5(b"png").digest()).decode("ascii")
    assert fake.uploads[0][2] == b"png"


def test_create_rejects_blank_source():
    # Regression: a blank source must fail locally, not POST an empty body.
    client = FilesClient(api_key="k", http_client=FakeHttp(UPLOAD))
    with pytest.raises(ValueError):
        client.create(source="")
    with pytest.raises(ValueError):
        client.create(source="   ")
