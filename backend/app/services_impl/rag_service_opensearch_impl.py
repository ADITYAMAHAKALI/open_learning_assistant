# app/services_impl/rag_service_opensearch_impl.py
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.rag_service import RAGService
from app.adapters.llm.base import LLMClient
from app.adapters.vectorstore.opensearch_vectorstore import OpenSearchVectorStore

class RAGServiceOpenSearchImpl(RAGService):
    def __init__(
        self,
        db: Session,
        vector_store: OpenSearchVectorStore,
        llm: LLMClient,
    ) -> None:
        self.db = db
        self.vector_store = vector_store
        self.llm = llm

    async def answer_question(
        self,
        user_id: int,
        material_id: int,
        topic_id: int | None,
        question: str,
    ) -> Dict[str, Any]:
        # 1. retrieval
        docs = self.vector_store.search(
            query=question,
            material_id=material_id,
            topic_id=topic_id,
            k=5,
        )

        context_blocks = [d["content"] for d in docs]
        sources = [
            {"chunk_id": d["chunk_id"], "page": d.get("page")}
            for d in docs
        ]

        # 2. prompt LLM
        prompt = self._build_prompt(question, context_blocks)
        answer, followups = await self.llm.chat_with_followups(prompt)

        return {
            "answer": answer,
            "sources": sources,
            "followups": followups,
        }

    def _build_prompt(self, question: str, context_blocks: list[str]) -> str:
        context = "\n\n---\n\n".join(context_blocks)
        return f"""
You are a helpful tutoring assistant.

Use ONLY the context below to answer the question.
If something is unclear or missing, say so explicitly.

Context:
{context}

Question: {question}

Return a clear explanation suitable for a student.
"""
