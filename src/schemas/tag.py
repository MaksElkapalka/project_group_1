from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TagSchema(BaseModel):
    name: str = Field(max_length=50)


class TagUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50)


class TagResponse(TagSchema):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
