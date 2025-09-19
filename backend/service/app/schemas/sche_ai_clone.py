# app/schemas/sche_ai_clone.py
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class CreateVideoResponse(BaseModel):
    """Response cho AI clone"""
    success: bool
    video_id: Optional[int] = None
    session_id: Optional[str] = None
    video_url: Optional[str] = None
    video_filename: Optional[str] = None
    status: Optional[str] = Field(default="pending")

    # Thông tin text generation (cho trường hợp 2)
    generated_target_text: Optional[str] = None
    text_generation_time: Optional[float] = None

    # Thông tin video generation
    video_generation_time: Optional[float] = None
    total_processing_time: Optional[float] = None

    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VideoListItem(BaseModel):
    """Item trong danh sách video của user"""
    id: int
    reference_text: str
    target_text: str
    language: str
    status: str
    video_url: Optional[str] = None
    video_filename: Optional[str] = None
    
    # Thông tin generation
    is_ai_generated_text: bool
    topic: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    
    # Timing
    processing_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Error info
    error_message: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GetUserVideosResponse(BaseModel):
    """Response  API get list video"""
    success: bool
    user_id: int
    total_videos: int
    videos: List[VideoListItem]
    error: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
