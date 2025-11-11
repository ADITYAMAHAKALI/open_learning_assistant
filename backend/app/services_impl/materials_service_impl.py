# app/services_impl/materials_service_impl.py
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.services.materials_service import MaterialsService
from app.adapters.storage.object_storage import StorageBackend
from app.db import models


class MaterialsServiceImpl(MaterialsService):
    def __init__(
        self,
        db: Session,
        vector_store,
        storage: StorageBackend,
    ) -> None:
        self.db = db
        self.storage = storage
        self.vector_store = vector_store

    async def upload_material(
        self,
        user_id: int,
        file: UploadFile,
    ) -> int:
        # 1. store raw file via storage backend
        path = await self.storage.save(file)

        # 2. create DB row
        material = models.learning_material.LearningMaterial(
            owner_id=user_id,
            filename=file.filename,
            path=path,
            status="PENDING",
        )
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        # 3. enqueue ingestion job (Celery/RQ) – left as TODO
        # enqueue_ingestion_job(material.id)

        return material.id

    async def list_materials(self, user_id: int) -> List[dict]:
        rows = (
            self.db.query(models.learning_material.LearningMaterial)
            .filter_by(owner_id=user_id)
            .all()
        )
        return [
            {
                "id": m.id,
                "filename": m.filename,
                "status": m.status,
            }
            for m in rows
        ]
