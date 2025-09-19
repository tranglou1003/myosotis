# app/models/model_ai_clone.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.model_base import Base
from datetime import datetime


class AICloneVideo(Base):
    """Model cho ideo AI Clone đã tạo"""
    
    __tablename__ = "ai_clone_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Input information
    reference_text = Column(String(800), nullable=False, comment="Text trong audio mẫu")
    target_text = Column(Text, nullable=False, comment="Text mà AI sẽ nói")
    language = Column(String(20), default="english", comment="Ngôn ngữ")
    dynamic_scale = Column(Float, default=1.0, comment="Mức độ animation")
    
    # Content generation info (nếu target_text được AI tạo)
    is_ai_generated_text = Column(Boolean, default=False, comment="Target text có được AI tạo không")
    topic = Column(String(500), nullable=True, comment="Chủ đề ")
    description = Column(Text, nullable=True, comment="Mô tả")
    keywords = Column(String(700), nullable=True, comment="Từ khóa")
    
    # Processing info
    session_id = Column(String(100), nullable=True, comment="Session ID từ AI service")
    status = Column(String(20), default="pending", comment="Trạng thái: pending, processing, completed, failed")
    
    # Output info
    video_url = Column(String(500), nullable=True, comment="URL của video")
    video_filename = Column(String(200), nullable=True, comment="Name file ")
    processing_time = Column(Float, nullable=True, comment="Tgian xử lý (giây)")
    
    # Error info
    error_message = Column(Text, nullable=True, comment="Lỗi")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True, comment="Tgian done")
    
    # Relationship
    user = relationship("User", back_populates="ai_clone_videos")
