# app/adapters/llm/base.py
from abc import ABC, abstractmethod
from typing import Tuple, List

class LLMClient(ABC):
    @abstractmethod
    async def chat(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def chat_with_followups(self, prompt: str) -> Tuple[str, List[str]]:
        """Return (answer, followup_questions)."""
        raise NotImplementedError
