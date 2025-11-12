import io
import os

import pytest
from fastapi import UploadFile

from app.adapters.storage.object_storage import LocalFileStorage


@pytest.mark.asyncio
async def test_local_file_storage_saves_file(temp_dir):
    storage = LocalFileStorage(base_path=temp_dir)

    content = b"hello world"
    upload_file = UploadFile(filename="test.txt", file=io.BytesIO(content))

    path = await storage.save(upload_file)

    assert os.path.exists(path)
    with open(path, "rb") as f:
        assert f.read() == content
