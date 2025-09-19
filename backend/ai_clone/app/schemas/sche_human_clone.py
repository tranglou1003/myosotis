"""
Human Clone Schemas - Pydantic models for human cloning API
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HumanCloneStatus(str, Enum):
    """Status of human clone processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class HumanCloneRequest(BaseModel):
    """Request model for human clone generation"""
    reference_audio_base64: str = Field(
        ..., 
        description="Base64 encoded reference audio file (WAV format recommended)",
        min_length=100
    )
    reference_text: str = Field(
        ..., 
        description="Text corresponding to the reference audio",
        min_length=1,
        max_length=1000
    )
    target_text: str = Field(
        ..., 
        description="Target text to be spoken by the cloned voice",
        min_length=1,
        max_length=2000
    )
    image_base64: str = Field(
        ..., 
        description="Base64 encoded reference image (JPG/PNG format)",
        min_length=100
    )
    language: str = Field(
        default="vietnamese", 
        description="Language for voice synthesis",
        pattern="^(vietnamese|english)$"
    )
    dynamic_scale: float = Field(
        default=1.0, 
        description="Dynamic scale for talking face animation",
        ge=0.1,
        le=3.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reference_audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=",
                "reference_text": "Hello, this is my voice sample.",
                "target_text": "Welcome to our human cloning service. This is an amazing demonstration.",
                "image_base64": "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/wAALCAABAAEBAREA/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "language": "vietnamese",
                "dynamic_scale": 1.0
            }
        }


class HumanCloneResult(BaseModel):
    """Response model for human clone generation"""
    session_id: str = Field(..., description="Unique session identifier")
    status: HumanCloneStatus = Field(..., description="Processing status")
    video_url: Optional[str] = Field(None, description="URL to download the generated video")
    video_filename: Optional[str] = Field(None, description="Filename of the generated video")
    duration_seconds: Optional[float] = Field(None, description="Duration of the generated video in seconds")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time in seconds")
    message: str = Field(..., description="Status message or error description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional processing metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "video_url": "/api/v1/human-clone/download/550e8400-e29b-41d4-a716-446655440000.mp4",
                "video_filename": "550e8400-e29b-41d4-a716-446655440000.mp4",
                "duration_seconds": 15.2,
                "processing_time_seconds": 45.7,
                "message": "Human clone generated successfully",
                "metadata": {
                    "language": "vietnamese",
                    "dynamic_scale": 1.0,
                    "voice_clone_info": {"duration_seconds": 15.2},
                    "sonic_info": {"faces_detected": 1}
                },
                "created_at": "2025-08-12T10:30:00"
            }
        }


class EnvironmentStatus(BaseModel):
    """Environment health status model"""
    service: str = Field(..., description="Service name")
    status: str = Field(..., description="Overall status (healthy/unhealthy/error)")
    conda_environment: Optional[str] = Field(None, description="Conda environment info")
    cuda_status: Optional[str] = Field(None, description="CUDA availability status")
    voice_clone_status: Optional[str] = Field(None, description="Voice Clone TTS status")
    sonic_status: Optional[str] = Field(None, description="Sonic status")
    gpu: Optional[Dict[str, Any]] = Field(None, description="GPU memory information")
    directories: Optional[Dict[str, Any]] = Field(None, description="Directory status")
    timestamp: str = Field(..., description="Status check timestamp")
    error: Optional[str] = Field(None, description="Error message if status is error")

    class Config:
        json_schema_extra = {
            "example": {
                "service": "human_clone",
                "status": "healthy",
                "conda_environment": "Python 3.10.18",
                "cuda_status": "CUDA Available: True, CUDA Devices: 2",
                "voice_clone_status": "Available",
                "sonic_status": "Available",
                "gpu": {
                    "success": True,
                    "memory_info": "GPU Memory Free: 23456789123"
                },
                "directories": {
                    "temp_dir": "/app/temp_clone",
                    "public_dir": "/app/public/human_clone",
                    "temp_exists": True,
                    "public_exists": True
                },
                "timestamp": "2025-08-12T10:30:00"
            }
        }


class HumanCloneProgress(BaseModel):
    """Progress tracking model for long-running operations"""
    session_id: str = Field(..., description="Session identifier")
    status: HumanCloneStatus = Field(..., description="Current status")
    progress_percentage: float = Field(..., description="Progress percentage (0-100)", ge=0, le=100)
    current_step: str = Field(..., description="Description of current processing step")
    estimated_remaining_seconds: Optional[float] = Field(None, description="Estimated remaining time")
    message: str = Field(..., description="Current status message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "progress_percentage": 65.0,
                "current_step": "Generating talking face animation",
                "estimated_remaining_seconds": 30.5,
                "message": "Processing talking face with Sonic AI..."
            }
        }
