from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.tag import TagSchema, TagResponse
from src.repository import tags as repository_tags
from src.entity.models import User

router = APIRouter(prefix='/tags', tags=["tags"])

@router.get("/", response_model=List[TagResponse])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = repository_tags.get_tags(skip, limit, db)
    return tags

@router.get("/{tag_id}", response_model=TagResponse)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

@router.post("/", response_model=TagResponse)
def create_tag(body: TagSchema, db: Session = Depends(get_db)):
    return repository_tags.create_tag(body, db)

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(body: TagSchema, tag_id: int, db: Session = Depends(get_db)):
    tag = repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

@router.delete("/{tag_id}", response_model=TagResponse)
def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

@router.post("/add", response_model=TagResponse)
def add_tag(photo_id: int, tag_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tag = repository_tags.add_tag(photo_id, tag_name, current_user.id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found or does not belong to the user")
    return tag
