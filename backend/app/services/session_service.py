# app/services/session_service.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SessionService(ABC):
    @abstractmethod
    async def create_session(
        self,
        user_id: int,
        title: str,
        objective: str | None,
        material_ids: List[int],
    ) -> Dict[str, Any]:
        """Create a learning session and prerequisite tree."""
        raise NotImplementedError

    @abstractmethod
    async def list_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_session(self, user_id: int, session_id: int) -> Dict[str, Any]:
        raise NotImplementedError
