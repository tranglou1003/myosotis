from sqlalchemy import Column, Integer, String, Text, Enum, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.model_base import BareBaseModel

class StoryType(str, enum.Enum):
    image = "image"
    audio = "audio"
    video = "video"  # Added video type

class Story(BareBaseModel):
    __tablename__ = "story_life"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(Enum(StoryType), nullable=False)
    description = Column(Text)
    file_path = Column(String(500)) 
    start_time = Column(Date)
    end_time = Column(Date)

    user = relationship("User", back_populates="stories")