import pytest

from app.services_impl.session_service_impl import SessionServiceImpl
from app.services.prereq_service import PrerequisiteSuggestion, PrereqService
from app.adapters.wiki.wikipedia_client import WikipediaClient
from app.db import models


class FakePrereqService(PrereqService):
    async def generate_prerequisite_tree(self, *args, **kwargs):
        return [
            PrerequisiteSuggestion(
                name="Basics",
                description="Start here",
                parent=None,
            ),
            PrerequisiteSuggestion(
                name="Next",
                description="Then this",
                parent="Basics",
            ),
        ]


class FakeWiki(WikipediaClient):
    def __init__(self) -> None:
        pass

    def fetch_summary(self, topic: str):  # type: ignore[override]
        return f"Summary for {topic}", f"https://example.com/{topic}"


@pytest.mark.asyncio
async def test_session_service_creates_session_with_multiple_materials(db):
    user = models.user.User(email="user@example.com", hashed_password="pwd")
    material1 = models.learning_material.LearningMaterial(
        owner_id=1,
        filename="file1.pdf",
        path="/tmp/file1.pdf",
        status="READY",
    )
    material2 = models.learning_material.LearningMaterial(
        owner_id=1,
        filename="file2.pdf",
        path="/tmp/file2.pdf",
        status="READY",
    )
    db.add(user)
    db.flush()
    material1.owner_id = user.id
    material2.owner_id = user.id
    db.add_all([material1, material2])
    db.commit()

    service = SessionServiceImpl(db, FakePrereqService(), FakeWiki())
    session = await service.create_session(
        user_id=user.id,
        title="Study Plan",
        objective="Learn things",
        material_ids=[material1.id, material2.id],
    )

    assert len(session["materials"]) == 2
    assert len(session["prerequisites"]) == 2
    assert any(node["parent_id"] for node in session["prerequisites"])


@pytest.mark.asyncio
async def test_session_service_list_and_get(db):
    user = models.user.User(email="another@example.com", hashed_password="pwd")
    material = models.learning_material.LearningMaterial(
        owner_id=1,
        filename="intro.pdf",
        path="/tmp/intro.pdf",
        status="READY",
    )
    db.add(user)
    db.flush()
    material.owner_id = user.id
    db.add(material)
    db.commit()

    service = SessionServiceImpl(db, FakePrereqService(), FakeWiki())
    created = await service.create_session(
        user_id=user.id,
        title="Quick Plan",
        objective="",
        material_ids=[material.id],
    )

    sessions = await service.list_sessions(user.id)
    assert len(sessions) == 1
    assert sessions[0]["id"] == created["id"]

    detail = await service.get_session(user.id, created["id"])
    assert detail["id"] == created["id"]


@pytest.mark.asyncio
async def test_session_service_validates_material_ownership(db):
    user = models.user.User(email="wrong@example.com", hashed_password="pwd")
    db.add(user)
    db.flush()

    service = SessionServiceImpl(db, FakePrereqService(), FakeWiki())
    with pytest.raises(ValueError):
        await service.create_session(
            user_id=user.id,
            title="Bad",
            objective=None,
            material_ids=[999],
        )
