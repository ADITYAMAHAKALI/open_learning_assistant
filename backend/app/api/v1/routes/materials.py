# app/api/v1/routes/materials.py
from fastapi import APIRouter, Depends, UploadFile, File, status
from typing import List

from app.core.deps import get_materials_service, get_current_user
from app.services.materials_service import MaterialsService
from app.db.models.user import User

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_material(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: MaterialsService = Depends(get_materials_service),
):
    material_id = await service.upload_material(user_id=current_user.id, file=file)
    return {"material_id": material_id}


@router.get("/", response_model=List[dict])
async def list_materials(
    current_user: User = Depends(get_current_user),
    service: MaterialsService = Depends(get_materials_service),
):
    return await service.list_materials(current_user.id)
