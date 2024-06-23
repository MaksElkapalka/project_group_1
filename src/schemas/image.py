from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class ImageSchema(BaseModel):
    url: str
    description: str

class ImageUpdateSchema(BaseModel):
    description: Optional[str] = None

class ImageResponse(BaseModel):
    id: int
    url: str
    description: str

    model_config = ConfigDict(from_attributes=True)

