from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field
from src.schemas.comments import CommentToImage
from src.schemas.tag import TagImage


class ImageSchema(BaseModel):
    url: str
    description: str

class ImageCreate(BaseModel):
    url: str
    description: str
    created_at: datetime

class ImageUpdateSchema(BaseModel):
    description: Optional[str] = None


class ImageResponse(BaseModel):
    id: int
    url: str
    description: str
    tags: Optional[List[TagImage]] = None
    comments: Optional[List[CommentToImage]] = None

    model_config = ConfigDict(from_attributes=True)

