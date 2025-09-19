from pydantic import BaseModel
from typing import Optional
from enum import Enum

class MediaTypeEnum(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"

class MediaCreate(BaseModel):
    user_id: int
    media_type: MediaTypeEnum
    title: str
    artist: Optional[str]

class MediaResponse(BaseModel):
    id: int
    user_id: int
    media_type: MediaTypeEnum
    title: str
    artist: Optional[str]
    file_path: str

    class Config:
       from_attributes = True
