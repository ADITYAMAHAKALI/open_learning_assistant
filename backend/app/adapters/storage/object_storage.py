# app/adapters/storage/object_storage.py
import os
from uuid import uuid4
from abc import ABC, abstractmethod
from fastapi import UploadFile

from app.core.config import settings


class StorageBackend(ABC):
    """
    Abstract storage backend.
    """

    @abstractmethod
    async def save(self, file: UploadFile) -> str:
        """
        Persist the uploaded file and return a path / URI that can be used later.
        """
        raise NotImplementedError


class LocalFileStorage(StorageBackend):
    """
    Local filesystem storage.

    Writes files under STORAGE_BASE_PATH (e.g. /data/materials inside the container),
    which is mounted as a volume in docker-compose.
    """

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = base_path or settings.STORAGE_BASE_PATH
        os.makedirs(self.base_path, exist_ok=True)

    async def save(self, file: UploadFile) -> str:
        contents = await file.read()
        ext = os.path.splitext(file.filename or "")[1]
        filename = f"{uuid4().hex}{ext}"
        path = os.path.join(self.base_path, filename)

        with open(path, "wb") as f:
            f.write(contents)

        # Return absolute path inside the container. For now we just store this in DB.
        return path
