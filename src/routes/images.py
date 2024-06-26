from typing import List

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    Query,
    status)
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User, Image
from src.database.db import get_db
from src.repository import images as repository_images
from src.schemas.image import ImageSchema, ImageUpdateSchema, ImageResponse, ImageCreate
from src.services.auth import auth_service, role_required
from src.conf import messages

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload/", response_model=ImageCreate, status_code=201)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    description: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    result = await repository_images.upload_image(file.file, description, db, user)
    return result

@router.put("/update/{image_id}",
            response_model=ImageResponse,
            dependencies=[Depends(auth_service.get_current_active_user),
                          Depends(role_required(["admin"]))]
)
async def update_image_endpoint(
    body: ImageUpdateSchema,
    image_id: int, 
    db: AsyncSession = Depends(get_db)
):
    image = await repository_images.update_image(image_id, body, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return image

@router.get("/show/", response_model=List[ImageResponse])
async def get_all_images(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=10), db: AsyncSession = Depends(get_db)):
    result = await repository_images.get_all_images(limit, offset, db)
    return result

@router.get("/", response_model=ImageResponse)
async def get_image(image_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    result = await repository_images.get_image(image_id, db, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return result

@router.delete("/{image_id}",
               dependencies=[Depends(auth_service.get_current_active_user),
                             Depends(role_required(["admin"]))]
)
async def delete_image_endpoint(
    image_id: int, 
    db: AsyncSession = Depends(get_db),
):
    image = await repository_images.delete_image(image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return {"message": "Image deleted successfully"}