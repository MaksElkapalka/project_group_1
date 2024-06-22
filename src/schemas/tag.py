# from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.entity.models import Image


class TagSchema(BaseModel):
    name: str = Field(max_length=50)
    images: Image
    # last_name: str = Field(max_length=50)
    # email: Optional[EmailStr] = Field(None, max_length=100)
    # phone_number: str = Field(max_length=20)
    # birthday: Optional[date] = None
    # additional_info: Optional[str] = Field(None, max_length=255)


class ContactUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    images: Image
    # last_name: Optional[str] = Field(None, max_length=50)
    # email: Optional[EmailStr] = Field(None, max_length=100)
    # phone_number: Optional[str] = Field(None, max_length=20)
    # birthday: Optional[date] = None
    # additional_info: Optional[str] = Field(None, max_length=255)


class TagResponse(TagSchema):
    name: str

    model_config = ConfigDict(from_attributes=True)
