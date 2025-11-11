# app/api/v1/routes/learning.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.deps import get_rag_service, get_current_user
from app.services.rag_service import RAGService
from app.db.models.user import User

router = APIRouter()


class AskQuestionRequest(BaseModel):
    material_id: int
    topic_id: Optional[int] = None
    question: str


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
