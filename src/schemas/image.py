from typing import Optional, List 

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

class ImageEdit(BaseModel):
    transformations: List[str]

class ImageFilter(BaseModel):
    filter_name: str

class ImageResize(BaseModel):
    width: int
    height: int

class ImageCrop(BaseModel):
    width: int
    height: int
    x: int
    y: int
