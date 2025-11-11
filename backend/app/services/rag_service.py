# app/services/rag_service.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RAGService(ABC):
    @abstractmethod
    async def answer_question(
        self,
        user_id: int,
        material_id: int,
        topic_id: int | None,
        question: str,
    ) -> Dict[str, Any]:
        """Return answer + sources + followups."""
        raise NotImplementedError
