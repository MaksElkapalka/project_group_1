from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from src.entity.models import Comment


class CommentCreate(BaseModel):
    name: str
    image_id: int


class CommentUpdate(BaseModel):
    name: str


class CommentResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    image_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)



