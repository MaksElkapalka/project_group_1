import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session
from src.entity.models import Image
from datetime import datetime


cloudinary.config(
    cloud_name='dl3r3kuc7',
    api_key='751461151172894',
    api_secret='sNj7zesOKc2v-MV0gAC259IPnws'
)

def upload_image(file, description: str, user_id: int, db: Session):
    """
    Uploads an image to Cloudinary and saves the image URL and description to the database.
    
    :param file: The image file to upload.
    :param description: The description of the image.
    :param user_id: The ID of the user uploading the image.
    :param db: The database session.
    :return: The image URL and description.
    """
    
    result = cloudinary.uploader.upload(file)
    image_url = result.get("url")
    
    
    image = Image(
        url=image_url,
        description=description,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"url": image_url, "description": description}

def update_image(image_id: int, description: str, db: Session):
    """
    Updates the description of an existing image in the database.
    
    :param image_id: The ID of the image to update.
    :param description: The new description of the image.
    :param db: The database session.
    :return: The updated image information.
    """
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        return None
    image.description = description
    image.updated_at = datetime.now()
    db.commit()
    db.refresh(image)
    return {"url": image.url, "description": description}
