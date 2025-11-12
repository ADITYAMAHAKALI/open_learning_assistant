import io

import pytest
from fastapi import UploadFile

from app.services_impl.materials_service_impl import MaterialsServiceImpl
from app.adapters.storage.object_storage import LocalFileStorage
from app.db.models.user import User
from app.db.models.learning_material import LearningMaterial


class DummyVectorStore:
    def __init__(self):
        self.indexed = []

    def index_chunk(self, *args, **kwargs):
        self.indexed.append((args, kwargs))

@pytest.fixture()
def materials_service(db, temp_dir):
    # create or reuse a test user
    user = db.query(User).filter_by(email="materials@example.com").first()
    if not user:
        user = User(email="materials@example.com", hashed_password="x")
        db.add(user)
        db.commit()
        db.refresh(user)

    storage = LocalFileStorage(base_path=temp_dir)
    vector_store = DummyVectorStore()

    service = MaterialsServiceImpl(
        db=db,
        vector_store=vector_store,
        storage=storage,
    )
    return service, user


@pytest.mark.asyncio
async def test_upload_material_creates_db_row(materials_service):
    service, user = materials_service

    content = b"dummy pdf bytes"
    upload_file = UploadFile(
        filename="test.pdf",
        file=io.BytesIO(content),
    )

    material_id = await service.upload_material(user_id=user.id, file=upload_file)
    assert material_id is not None

    rows = (
        service.db.query(LearningMaterial)
        .filter_by(owner_id=user.id)
        .all()
    )
    assert len(rows) == 1
    m = rows[0]
    assert m.id == material_id
    assert m.filename == "test.pdf"
    assert m.status == "PENDING"


@pytest.mark.asyncio
async def test_list_materials_returns_basic_fields(materials_service):
    service, user = materials_service

    mat = LearningMaterial(
        owner_id=user.id,
        filename="foo.pdf",
        path="/tmp/foo.pdf",
        status="READY",
    )
    service.db.add(mat)
    service.db.commit()
    service.db.refresh(mat)

    result = await service.list_materials(user_id=user.id)
    assert len(result) == 1
    assert result[0]["id"] == mat.id
    assert result[0]["filename"] == "foo.pdf"
    assert result[0]["status"] == "READY"
