from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from src.database.db import get_db
from repository.images import upload_image, update_image

router = APIRouter()

@router.post("/upload/")
async def upload_image_endpoint(file: UploadFile = File(...), description: str = Form(...), user_id: int = Form(...), db: Session = Depends(get_db)):
    result = upload_image(file.file, description, user_id, db)
    return result

@router.put("/update/{image_id}")
async def update_image_endpoint(image_id: int, description: str = Form(...), db: Session = Depends(get_db)):
    result = update_image(image_id, description, db)
    if not result:
        return {"error": "Image not found"}
    return result




