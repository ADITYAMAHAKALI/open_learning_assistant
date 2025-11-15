import pytest

from app.services_impl.prereq_llm_impl import PrereqLLMImpl
from app.adapters.llm.base import LLMClient


class DummyLLM(LLMClient):
    def __init__(self, response: str):
        self.response = response

    async def chat(self, prompt: str) -> str:  # type: ignore[override]
        return self.response

    async def chat_with_followups(self, prompt: str):  # type: ignore[override]
        return "answer", []


@pytest.mark.asyncio
async def test_prereq_llm_parses_nodes():
    response = """
    Here is your plan:
    {"nodes": [
        {"name": "Vectors", "description": "Basics", "parent": null},
        {"name": "Matrices", "description": "Matrix intro", "parent": "Vectors"}
    ]}
    """
    service = PrereqLLMImpl(llm=DummyLLM(response))

    nodes = await service.generate_prerequisite_tree(
        session_title="Linear Algebra",
        objective="Understand matrices",
        materials=[{"filename": "notes.pdf"}],
    )

    assert len(nodes) == 2
    assert nodes[1].parent == "Vectors"


@pytest.mark.asyncio
async def test_prereq_llm_returns_fallback_when_invalid_json():
    service = PrereqLLMImpl(llm=DummyLLM("not json"))

    nodes = await service.generate_prerequisite_tree(
        session_title="Calculus",
        objective="Master derivatives",
        materials=[],
    )

    assert len(nodes) == 1
    assert nodes[0].name == "Calculus"
