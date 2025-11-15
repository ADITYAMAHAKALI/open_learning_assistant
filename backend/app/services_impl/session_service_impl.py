# app/services_impl/session_service_impl.py
from __future__ import annotations

from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.services.session_service import SessionService
from app.services.prereq_service import PrereqService, PrerequisiteSuggestion
from app.adapters.wiki.wikipedia_client import WikipediaClient
from app.db import models


class SessionServiceImpl(SessionService):
    def __init__(
        self,
        db: Session,
        prereq_service: PrereqService,
        wiki_client: WikipediaClient,
    ) -> None:
        self.db = db
        self.prereq_service = prereq_service
        self.wiki_client = wiki_client

    async def create_session(
        self,
        user_id: int,
        title: str,
        objective: str | None,
        material_ids: List[int],
    ) -> Dict[str, Any]:
        clean_title = (title or "").strip()
        if not clean_title:
            raise ValueError("Session title is required")

        if not material_ids:
            raise ValueError("Select at least one learning material")

        unique_ids = self._normalize_material_ids(material_ids)
        materials = self._get_user_materials(user_id, unique_ids)
        if len(materials) != len(unique_ids):
            raise ValueError("One or more materials were not found")

        material_map = {m.id: m for m in materials}

        normalized_objective = (
            objective.strip() if objective and objective.strip() else None
        )

        try:
            session = models.learning_session.LearningSession(
                user_id=user_id,
                title=clean_title,
                objective=normalized_objective,
            )
            self.db.add(session)
            self.db.flush()

            for material_id in unique_ids:
                material = material_map[material_id]
                link = models.learning_session_material.LearningSessionMaterial(
                    session_id=session.id,
                    material_id=material.id,
                )
                self.db.add(link)
            self.db.flush()

            material_descriptors = [
                {"filename": material_map[mid].filename} for mid in unique_ids
            ]

            suggestions = await self.prereq_service.generate_prerequisite_tree(
                session_title=clean_title,
                objective=normalized_objective,
                materials=material_descriptors,
            )

            created_nodes = self._persist_prerequisites(session.id, suggestions)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(session)
        session.prerequisite_nodes = created_nodes
        return self._serialize_session(session)

    async def list_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(models.learning_session.LearningSession)
            .filter(models.learning_session.LearningSession.user_id == user_id)
            .order_by(models.learning_session.LearningSession.created_at.desc())
            .all()
        )
        return [self._serialize_session_summary(row) for row in rows]

    async def get_session(self, user_id: int, session_id: int) -> Dict[str, Any]:
        session = (
            self.db.query(models.learning_session.LearningSession)
            .filter(
                models.learning_session.LearningSession.user_id == user_id,
                models.learning_session.LearningSession.id == session_id,
            )
            .first()
        )
        if not session:
            raise ValueError("Learning session not found")
        return self._serialize_session(session)

    def _get_user_materials(
        self, user_id: int, material_ids: List[int]
    ) -> List[models.learning_material.LearningMaterial]:
        rows = (
            self.db.query(models.learning_material.LearningMaterial)
            .filter(
                models.learning_material.LearningMaterial.owner_id == user_id,
                models.learning_material.LearningMaterial.id.in_(material_ids),
            )
            .all()
        )
        return rows

    def _persist_prerequisites(
        self,
        session_id: int,
        suggestions: List[PrerequisiteSuggestion],
    ) -> List[models.prerequisite_node.PrerequisiteNode]:
        stored: dict[str, models.prerequisite_node.PrerequisiteNode] = {}
        for suggestion in suggestions:
            normalized_name = (suggestion.name or "").strip()
            if not normalized_name:
                continue
            key = normalized_name.lower()
            if key in stored:
                continue

            summary = None
            url = None
            try:
                summary, url = self.wiki_client.fetch_summary(normalized_name)
            except Exception:
                summary, url = None, None

            node = models.prerequisite_node.PrerequisiteNode(
                session_id=session_id,
                name=normalized_name,
                description=(suggestion.description or None),
                wikipedia_summary=self._truncate(summary),
                wikipedia_url=url,
            )
            self.db.add(node)
            self.db.flush()
            stored[key] = node

        for suggestion in suggestions:
            normalized_child = (suggestion.name or "").strip().lower()
            normalized_parent = (suggestion.parent or "").strip().lower()
            if normalized_child and normalized_parent:
                child = stored.get(normalized_child)
                parent = stored.get(normalized_parent)
                if child and parent:
                    child.parent_id = parent.id
                    self.db.add(child)
        self.db.flush()
        return list(stored.values())

    def _normalize_material_ids(self, material_ids: List[int]) -> List[int]:
        normalized: list[int] = []
        seen: set[int] = set()
        for mid in material_ids:
            try:
                as_int = int(mid)
            except (TypeError, ValueError):
                raise ValueError("Material ids must be integers") from None
            if as_int <= 0:
                raise ValueError("Material ids must be positive")
            if as_int not in seen:
                seen.add(as_int)
                normalized.append(as_int)
        return normalized

    def _serialize_session(self, session) -> Dict[str, Any]:
        materials = [
            {
                "id": link.material.id,
                "filename": link.material.filename,
                "status": link.material.status,
            }
            for link in session.material_links
        ]
        nodes = [
            {
                "id": node.id,
                "name": node.name,
                "description": node.description,
                "parent_id": node.parent_id,
                "wikipedia_summary": node.wikipedia_summary,
                "wikipedia_url": node.wikipedia_url,
            }
            for node in sorted(
                session.prerequisite_nodes,
                key=lambda n: (n.parent_id or 0, n.id or 0),
            )
        ]
        return {
            "id": session.id,
            "title": session.title,
            "objective": session.objective,
            "materials": materials,
            "prerequisites": nodes,
        }

    def _serialize_session_summary(self, session) -> Dict[str, Any]:
        return {
            "id": session.id,
            "title": session.title,
            "objective": session.objective,
            "material_count": len(session.material_links),
            "prerequisite_count": len(session.prerequisite_nodes),
        }

    def _truncate(self, text: str | None, limit: int = 600) -> str | None:
        if not text:
            return None
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."
