from typing import List
from fastapi import APIRouter, HTTPException, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.database.db import get_db
from src.schemas.tag import TagSchema, TagResponse
from src.repository import tags as repository_tags
from src.services.auth import auth_service
from src.entity.models import User
from src.conf import messages

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagResponse])
async def read_tags(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    tags = await repository_tags.get_tags(skip, limit, db)
    if tags is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND
        )
    return tags


@router.get("/{tag_name}", response_model=TagResponse)
async def read_tag(tag_name: str, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_name, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND
        )
    return tag


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(body: TagSchema, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.create_tag(body, db)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    body: TagSchema, tag_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    tag = await repository_tags.update_tag(tag_id, body, db)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND
        )
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag(tag_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.TAG_NOT_FOUND
        )
    return tag


@router.post(
    "/add_tag_for_image",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_tag_for_image_handler(
    tag_name: str,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    tag = await repository_tags.add_tag_for_image(tag_name, image_id, user, db)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found or does not belong to the user",
        )
    return tag
