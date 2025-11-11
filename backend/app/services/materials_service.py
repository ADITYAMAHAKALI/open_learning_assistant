# app/services/materials_service.py
from abc import ABC, abstractmethod
from typing import List
from fastapi import UploadFile

class MaterialsService(ABC):
    @abstractmethod
    async def upload_material(
        self,
        user_id: int,
        file: UploadFile,
    ) -> int:
        """Store file, create learning_material row, enqueue ingestion job. Returns material_id."""
        raise NotImplementedError

    @abstractmethod
    async def list_materials(self, user_id: int) -> List[dict]:
        raise NotImplementedError
