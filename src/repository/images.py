from datetime import datetime

import cloudinary
import cloudinary.uploader
# from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.entity.models import Image, User
from src.conf.config import config
from src.schemas.image import ImageUpdateSchema




cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET
)

async def upload_image(file: UploadFile, description: str, db: AsyncSession, user: User):
    """
    Uploads an image to Cloudinary and saves the image URL and description to the database.
    
    :param file: The image file to upload.
    :param description: The description of the image.
    :param user_id: The ID of the user uploading the image.
    :param db: The database session.
    :return: The image URL and description.
    """
    
    result = await run_in_threadpool(cloudinary.uploader.upload, file)
    image_url = result.get("url")
    
    
    image = Image(
        url=image_url,
        description=description,
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image

async def update_image(image_id: int,
                       body: ImageUpdateSchema,  
                       db: AsyncSession, 
                       user: User):
    """
    Updates the description of an existing image in the database.
    
    :param image_id: The ID of the image to update.
    :param description: The new description of the image.
    :param db: The database session.
    :return: The updated image information.
    """
    # image = db.query(Image).filter(Image.id == image_id).first()
    stmt = select(Image). filter_by(id=image_id, user=user)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    if image:
        image.description = body.description
        image.updated_at = datetime.now()
        db.commit()
        db.refresh(image)
        return image


    # if not image:
    #     return None
    # image.description = description
    # image.updated_at = datetime.now()
    # db.commit()
    # db.refresh(image)
    # return {"url": image.url, "description": description}

async def get_all_images(limit: int, 
                         offset: int,
                         db: AsyncSession):
    stmt = select(Image).offset(offset).limit(limit)
    images = await db.execute(stmt)
    return images.scalars().all()

async def get_image(image_id: int, db: AsyncSession, user: User):
    stmt = select(Image).filter_by(id=image_id, user=user)
    image = await db.execute(stmt)
    return image.scalar_one_or_none()