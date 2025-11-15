# app/services/prereq_service.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class PrerequisiteSuggestion:
    name: str
    description: str
    parent: str | None = None


class PrereqService(ABC):
    @abstractmethod
    async def generate_prerequisite_tree(
        self,
        session_title: str,
        objective: str | None,
        materials: List[dict],
    ) -> List[PrerequisiteSuggestion]:
        """Return a list of prerequisite node suggestions."""
        raise NotImplementedError
