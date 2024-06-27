from datetime import datetime

import cloudinary
import cloudinary.uploader
import cloudinary.api
# from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from entity.models import Image
from services.images import edit_image, apply_filter, resize_image, crop_image

from src.entity.models import Image, User, Role
from src.conf.config import config
from src.schemas.image import ImageUpdateSchema

import cloudinary.uploader


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
    user.image_count += 1
    await db.commit()
    await db.refresh(image)
    await db.refresh(user)
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


async def delete_image(image_id, db: AsyncSession, user: User):
    """
    Deletes an image from Cloudinary and the database.

    :param image_id: The ID of the image to delete.
    :param db: The database session.
    :return: True if deletion is successful, False otherwise.
    """

    # Retrieve the image from the database
    stmt = select(Image).filter_by(id=image_id, user=user)
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    print(image)
    if image is None:
        return False

    # Check if the user has permission to delete the image
    if user.role in [Role.admin, Role.moderator] or user.id == image.user_id:
        # Delete the image from Cloudinary
        parts = image.url.split('/')
        public_id_with_format = parts[-1]  # останній елемент у шляху
        public_id = public_id_with_format.split('.')[0]
        cloudinary.uploader.destroy(public_id)
        
        # Delete the image from the database
        await db.delete(image)
        await db.commit()
        # await db.refresh()
        return True
    else:
        return False


def edit_image_in_db(db: Session, image_id: int, transformations: list):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        new_url = edit_image(image.url.split('/')[-1], transformations)
        image.url = new_url
        db.commit()
        db.refresh(image)
    return image

def apply_filter_to_image(db: Session, image_id: int, filter_name: str):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        new_url = apply_filter(image.url.split('/')[-1], filter_name)
        image.url = new_url
        db.commit()
        db.refresh(image)
    return image

def resize_image_in_db(db: Session, image_id: int, width: int, height: int):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        new_url = resize_image(image.url.split('/')[-1], width, height)
        image.url = new_url
        db.commit()
        db.refresh(image)
    return image

def crop_image_in_db(db: Session, image_id: int, width: int, height: int, x: int, y: int):
    image = db.query(Image).filter(Image.id == image_id).first()
    if image:
        new_url = crop_image(image.url.split('/')[-1], width, height, x, y)
        image.url = new_url
        db.commit()
        db.refresh(image)
    return image
