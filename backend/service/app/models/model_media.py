import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel

class MediaTypeEnum(str, enum.Enum):
    image = "image"
    video = "video"
    audio = "audio"

class Media(BareBaseModel):
    __tablename__ = "media"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    media_type = Column(Enum(MediaTypeEnum), nullable=False)
    title = Column(String(255), nullable=False)
    artist = Column(String(255))
    file_path = Column(String(255), nullable=False)

    user = relationship("User", back_populates="media")