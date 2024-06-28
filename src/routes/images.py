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
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.database.db import get_db
from src.repository import images as repository_images
from src.schemas.image import ImageUpdateSchema, ImageResponse, ImageCreate, Transformation, ImageUrlSchema, Roundformation
from src.services.auth import auth_service, role_required
from src.conf import messages
from src.services.qr import generate_qr_code

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/upload/", response_model=ImageCreate, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    description: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """The upload_image function uploads an image to Cloudinary and saves the image URL and description to the database.

    Args:
        file (UploadFile, optional): The image file to upload.
        description (str, optional): The description of the image.
        db (AsyncSession, optional): Pass in the database session.
        user (User, optional): Current user.

    Returns:
        ImageCreate: Created image.
    """
    result = await repository_images.upload_image(file.file, description, db, user)
    return result

@router.post("/transform/{image_id}", response_model=ImageResponse)
async def tnsform_image(
    image_id: int,
    transformation: str = Form(...),  
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    image = await repository_images.get_image(image_id, db, user)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    
    transformed_url = repository_images.transform_image(image.url, transformation)
    
    qr_code = generate_qr_code(transformed_url)
    
    transformed_image = await repository_images.save_transformed_image(image_id, transformed_url, qr_code, db)
    
    return transformed_image

@router.put("/update/{image_id}",
            response_model=ImageResponse,
            dependencies=[Depends(auth_service.get_current_active_user),
                          Depends(role_required(["admin"]))]
)
async def update_image(
    body: ImageUpdateSchema,
    image_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """The update_image function updates the description of an existing image in the database.

    Args:
        image_id (int): Pass in the image object that is being updated.
        body (ImageUpdateSchema): The new description of the image.
        db (AsyncSession): Pass in the database session.

    Returns:
        ImageResponse: Updated image
    """
    image = await repository_images.update_image(image_id, body, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return image

@router.get("/show/", response_model=List[ImageResponse])
async def get_all_images(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=10), db: AsyncSession = Depends(get_db)):
    """The get_all_images function displays a list of images with specified pagination parameters.

    Args:
        limit (int): The maximum number of images to return.
        offset (int): Skips the offset rows before beginning to return the rows.
        db (AsyncSession): Pass in the database session.

    Returns:
        List: List of image objects.
    """
    result = await repository_images.get_all_images(limit, offset, db)
    return result


@router.get("/", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """The get_image function displays specific user's image.

    Args:
        image_id (int): Pass in the image object in database.
        db (AsyncSession): Pass in the database session.
        user (User): Specific user.

    Returns:
        ImageResponse: Image
    """
    result = await repository_images.get_image(image_id, db, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return result

@router.delete("/{image_id}",
               dependencies=[Depends(auth_service.get_current_active_user),
                             Depends(role_required(["admin"]))]
)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """The delete_image  function deletes an image from Cloudinary and the database.

    Args:
        image_id (int): Pass in the image object in database.
        db (AsyncSession): Pass in the database session.

    Returns:
        Dict: A dictionary with the message key.
    """
    image = await repository_images.delete_image(image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.IMAGE_NOT_FOUND)
    return {"message": "Image deleted successfully"}

@router.post("/transform")
async def transform_image_endpoint(image: ImageUrlSchema, 
                                   transformation: Transformation, 
                                   user: User = Depends(auth_service.get_current_user),
                                   db: AsyncSession = Depends(get_db)):
    transformations = transformation.model_dump()
    transformed_url = await repository_images.get_transformed_url(image.url, transformations, user, db)
    return {"transformed_url": transformed_url}

@router.post("/transform/avatar")
async def transform_image_for_avatar(image: ImageUrlSchema, 
                                   transformation: Roundformation, 
                                   user: User = Depends(auth_service.get_current_user),
                                   db: AsyncSession = Depends(get_db)):
    transformations = transformation.model_dump()
    transformed_url = await repository_images.get_foravatar_url(image.url, transformations, user, db)
    return {"transformed_url": transformed_url}