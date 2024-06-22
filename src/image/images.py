import cloudinary
import cloudinary.uploader
import cloudinary.api
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, Form, Depends
from src.database.db import get_db
from src.entity.models import Image
from datetime import datetime

router = APIRouter()

# TODU: прибрати з коду прямі данні підключення , всі дані зберігаються в .env і імпортуються з нього
cloudinary.config(
    cloud_name="dl3r3kuc7",
    api_key="751461151172894",
    api_secret="sNj7zesOKc2v-MV0gAC259IPnws",
)


@router.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    description: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    result = cloudinary.uploader.upload(file.file)
    image_url = result.get("url")

    image = Image(
        url=image_url,
        description=description,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return {"url": image_url, "description": description}
