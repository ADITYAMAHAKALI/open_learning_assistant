# app/services_impl/prereq_llm_impl.py
from __future__ import annotations

import json
import re
from typing import List

from app.adapters.llm.base import LLMClient
from app.services.prereq_service import PrereqService, PrerequisiteSuggestion


class PrereqLLMImpl(PrereqService):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def generate_prerequisite_tree(
        self,
        session_title: str,
        objective: str | None,
        materials: List[dict],
    ) -> List[PrerequisiteSuggestion]:
        prompt = self._build_prompt(session_title, objective, materials)
        response = await self.llm.chat(prompt)
        suggestions = self._parse_response(response, session_title, objective)
        return suggestions

    def _build_prompt(
        self,
        session_title: str,
        objective: str | None,
        materials: List[dict],
    ) -> str:
        material_lines = [
            f"- {item.get('filename', 'Unknown material')}"
            for item in materials
        ]
        material_block = "\n".join(material_lines) if material_lines else "(no files)"
        goal = objective or "Develop a structured learning path."
        return f"""
You are an expert learning designer. A student created a learning session called "{session_title}".
They want to accomplish the following goal: {goal}.
They will study the following materials:
{material_block}

Propose a prerequisite tree that a student can follow. Return STRICT JSON with the following shape:
{{
  "nodes": [
    {{
      "name": "Concept name",
      "description": "1-2 sentence summary of the concept",
      "parent": "Parent concept name or null if this is the root"
    }}
  ]
}}
Limit yourself to at most 6 nodes and keep names short.
"""

    def _parse_response(
        self,
        response: str,
        session_title: str,
        objective: str | None,
    ) -> List[PrerequisiteSuggestion]:
        payload = self._extract_json(response)
        if payload is None:
            return [
                PrerequisiteSuggestion(
                    name=session_title,
                    description=objective or "Learning objective",
                    parent=None,
                )
            ]

        nodes = payload.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            return [
                PrerequisiteSuggestion(
                    name=session_title,
                    description=objective or "Learning objective",
                    parent=None,
                )
            ]

        suggestions: List[PrerequisiteSuggestion] = []
        for node in nodes:
            name = (node or {}).get("name")
            description = (node or {}).get("description")
            parent = (node or {}).get("parent")
            if not name:
                continue
            suggestions.append(
                PrerequisiteSuggestion(
                    name=str(name).strip(),
                    description=str(description or "").strip(),
                    parent=str(parent).strip() if parent else None,
                )
            )

        if not suggestions:
            suggestions.append(
                PrerequisiteSuggestion(
                    name=session_title,
                    description=objective or "Learning objective",
                    parent=None,
                )
            )
        return suggestions

    def _extract_json(self, text: str) -> dict | None:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None
