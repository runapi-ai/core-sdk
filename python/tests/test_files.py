import os
import tempfile

import pytest

from runapi.core import FilesClient
from runapi.core.multipart import MultipartBody


class FakeHttp:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body))
        return self._response


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
    result = client.create(source="https://example.com/in.png")

    method, path, body = fake.calls[0]
    assert method == "post"
    assert path == "/api/v1/files"
    assert body == {"source": {"type": "url", "url": "https://example.com/in.png"}}
    assert result.url == UPLOAD["url"]
    assert result.size_bytes == 3


def test_create_with_uppercase_url_scheme_sends_url_source_object():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    client.create(source="HTTPS://example.com/in.png")

    _, _, body = fake.calls[0]
    assert body == {"source": {"type": "url", "url": "HTTPS://example.com/in.png"}}


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

    client.create(source={"type": "url", "url": "https://example.com/in.png"})

    _, _, body = fake.calls[0]
    assert body == {"source": {"type": "url", "url": "https://example.com/in.png"}}


def test_create_with_local_file_builds_multipart():
    fake = FakeHttp(UPLOAD)
    client = FilesClient(api_key="k", http_client=fake)

    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as handle:
        handle.write(b"png")
        path = handle.name
    try:
        client.create(file=path)
    finally:
        os.unlink(path)

    _, _, body = fake.calls[0]
    assert isinstance(body, MultipartBody)
    assert "file" in body.files
    assert body.files["file"].filename == os.path.basename(path)


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

    _, _, body = fake.calls[0]
    assert body.files["file"].filename == "custom.png"
    assert body.fields == {"file_name": "custom.png"}


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

    _, _, body = fake.calls[0]
    assert body.files["file"].path == path
    assert body.files["file"].filename == os.path.basename(path)


def test_create_rejects_blank_source():
    # Regression: a blank source must fail locally, not POST an empty body.
    client = FilesClient(api_key="k", http_client=FakeHttp(UPLOAD))
    with pytest.raises(ValueError):
        client.create(source="")
    with pytest.raises(ValueError):
        client.create(source="   ")
