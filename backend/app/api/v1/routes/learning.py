# app/api/v1/routes/learning.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.deps import (
    get_rag_service,
    get_current_user,
    get_session_service,
)
from app.services.rag_service import RAGService
from app.services.session_service import SessionService
from app.db.models.user import User

router = APIRouter()


class AskQuestionRequest(BaseModel):
    material_id: int
    topic_id: Optional[int] = None
    question: str


class CreateSessionRequest(BaseModel):
    title: str = Field(..., max_length=255)
    objective: Optional[str] = Field(default=None, max_length=1024)
    material_ids: List[int]


@router.post("/ask")
async def ask_question(
    payload: AskQuestionRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    result = await rag_service.answer_question(
        user_id=current_user.id,
        material_id=payload.material_id,
        topic_id=payload.topic_id,
        question=payload.question,
    )
    return result


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_learning_session(
    payload: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return await session_service.create_session(
            user_id=current_user.id,
            title=payload.title,
            objective=payload.objective,
            material_ids=payload.material_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions")
async def list_learning_sessions(
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.list_sessions(current_user.id)


@router.get("/sessions/{session_id}")
async def get_learning_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    try:
        return await session_service.get_session(current_user.id, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
