# tests/conftest.py
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import create_app
from app.db.base import Base
from app.db.session import get_db
from app.core.deps import (
    get_prereq_service,
    get_wikipedia_client,
)
from app.services.prereq_service import PrerequisiteSuggestion, PrereqService


TEST_DATABASE_URL = "sqlite://"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def SessionTest(engine) -> sessionmaker:
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )


@pytest.fixture()
def db(SessionTest) -> Generator[Session, None, None]:
    """
    Per-test DB session.

    We explicitly wipe all tables after each test so tests
    don't leak data into each other.
    """
    session: Session = SessionTest()
    try:
        yield session
        session.commit()
    finally:
        # Clean up all rows from all tables between tests
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient wired to the in-memory SQLite test DB.
    """
    app = create_app()

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    class _StubPrereqService(PrereqService):
        async def generate_prerequisite_tree(self, *args, **kwargs):
            return [
                PrerequisiteSuggestion(
                    name="Core Foundations",
                    description="Review the fundamentals.",
                    parent=None,
                ),
                PrerequisiteSuggestion(
                    name="Advanced Topic",
                    description="Build on the basics.",
                    parent="Core Foundations",
                ),
            ]

    class _StubWikiClient:
        def fetch_summary(self, topic: str):
            return f"Summary for {topic}", f"https://example.com/{topic.replace(' ', '_')}"

    app.dependency_overrides[get_prereq_service] = lambda: _StubPrereqService()
    app.dependency_overrides[get_wikipedia_client] = lambda: _StubWikiClient()

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def temp_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
