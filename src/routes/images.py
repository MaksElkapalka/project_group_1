from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User, Image
from src.database.db import get_db
from src.repository import images as repository_images
from src.schemas.image import ImageSchema, ImageUpdateSchema, ImageResponse
from  src.services.auth import auth_service
from src.schemas.image import ImageEdit, ImageFilter, ImageResize, ImageCrop


router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload/", response_model=ImageResponse, status_code=201)
async def upload_image_endpoint(file: UploadFile = File(...), description: str = Form(...), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    result = await repository_images.upload_image(file.file, description, db, user)
    return result

@router.put("/update/{image_id}")
async def update_image_endpoint(body: ImageUpdateSchema,
                                image_id: int, 
                                db: AsyncSession = Depends(get_db),
                                user: User = Depends(auth_service.get_current_user)):
    image = await repository_images.update_image(image_id, body, db, user)
    if image is None:
        raise HTTPException(
            status_code=404,
            detail=f"Image not found"
            )
    return image

@router.get("/show/", response_model=list[ImageResponse])
async def get_all_images(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=10), db: AsyncSession = Depends(get_db)):
    result = await repository_images.get_all_images(limit, offset, db)
    return result

@router.get("/", response_model=ImageResponse)
async def get_image(image_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    result = await repository_images.get_image(image_id, db, user)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Image not found"
            )
    return result

@router.delete("/{image_id}")
async def delete_image_endpoint(
    image_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    deleted = await repository_images.delete_image(image_id, db, user)
    if not deleted:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this image"
        )
    return {"message": "Image deleted successfully"}


@router.put("/edit/{image_id}")
async def edit_image(image_id: int, image_edit: ImageEdit, db: Session = Depends(get_db)):
    image = repository_images.edit_image_in_db(db, image_id, image_edit.transformations)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/filter/{image_id}")
async def apply_filter(image_id: int, image_filter: ImageFilter, db: Session = Depends(get_db)):
    image = repository_images.apply_filter_to_image(db, image_id, image_filter.filter_name)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/resize/{image_id}")
async def resize_image(image_id: int, image_resize: ImageResize, db: Session = Depends(get_db)):
    image = repository_images.resize_image_in_db(db, image_id, image_resize.width, image_resize.height)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/crop/{image_id}")
async def crop_image(image_id: int, image_crop: ImageCrop, db: Session = Depends(get_db)):
    image = repository_images.crop_image_in_db(db, image_id, image_crop.width, image_crop.height, image_crop.x, image_crop.y)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
