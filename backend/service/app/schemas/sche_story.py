from pydantic import BaseModel, Field, validator, model_validator
from datetime import datetime, date
from typing import Optional
import enum

class StoryType(str, enum.Enum):
    image = "image"
    audio = "audio"
    video = "video"

class StoryLifeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Story title")
    type: StoryType = Field(..., description="Type of story")
    description: Optional[str] = Field(None, max_length=5000, description="Story description")
    file_path: Optional[str] = Field(None, max_length=500, description="File path")
    start_time: Optional[date] = Field(None, description="Story start time")
    end_time: Optional[date] = Field(None, description="Story end time")

class StoryLifeCreateRequest(StoryLifeBase):
    user_id: int = Field(..., gt=0, description="User ID who creates the story")

class StoryLifeUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    description: Optional[str] = Field(None, max_length=5000)
    start_time: Optional[date] = None
    end_time: Optional[date] = None

    @validator("start_time", "end_time", pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def check_time_order(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError("end_time must be greater than or equal to start_time")
        return self

class StoryLifeResponse(StoryLifeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
