from runapi.core.multipart import MultipartBody
from runapi.core.uploads import Uploads


class FakeHttp:
    def __init__(self):
        self.calls = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body))
        if path.endswith("/parts"):
            return {"id": "part_123", "object": "upload.part", "created_at": 1, "upload_id": "upload_123"}
        return {
            "id": "upload_123", "object": "upload", "bytes": 3, "created_at": 1,
            "filename": "data.bin", "purpose": "user_data", "status": "pending", "expires_at": 2,
        }


def test_upload_lifecycle(tmp_path):
    part = tmp_path / "part.bin"
    part.write_bytes(b"abc")
    fake = FakeHttp()
    uploads = Uploads(fake)

    uploads.create(bytes=3, filename="data.bin", mime_type="application/octet-stream")
    uploads.add_part("upload_123", part)
    uploads.complete("upload_123", ["part_123"])
    uploads.cancel("upload_123")

    assert fake.calls[0][1:] == ("/v1/uploads", {
        "bytes": 3, "filename": "data.bin", "mime_type": "application/octet-stream", "purpose": "user_data"
    })
    assert fake.calls[1][1] == "/v1/uploads/upload_123/parts"
    assert isinstance(fake.calls[1][2], MultipartBody)
    assert fake.calls[2][2] == {"part_ids": ["part_123"]}
    assert fake.calls[3][1] == "/v1/uploads/upload_123/cancel"
