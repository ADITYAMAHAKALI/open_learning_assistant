import pytest

from app.services_impl.rag_service_opensearch_impl import RAGServiceOpenSearchImpl


class DummyLLM:
    async def chat_with_followups(self, prompt: str):
        return "This is the answer", ["Q1?", "Q2?", "Q3?"]


class DummyVectorStore:
    def search(self, query, material_id, topic_id, k=5):
        return [
            {
                "chunk_id": "c1",
                "content": "Context chunk 1",
                "page": 1,
            },
            {
                "chunk_id": "c2",
                "content": "Context chunk 2",
                "page": 2,
            },
        ]


@pytest.mark.asyncio
async def test_rag_service_returns_answer_sources_followups(db):
    llm = DummyLLM()
    vector_store = DummyVectorStore()

    service = RAGServiceOpenSearchImpl(
        db=db,
        vector_store=vector_store,
        llm=llm,
    )

    result = await service.answer_question(
        user_id=1,
        material_id=1,
        topic_id=None,
        question="What is X?",
    )

    assert result["answer"] == "This is the answer"
    assert len(result["sources"]) == 2
    assert result["sources"][0]["chunk_id"] == "c1"
    assert len(result["followups"]) == 3
