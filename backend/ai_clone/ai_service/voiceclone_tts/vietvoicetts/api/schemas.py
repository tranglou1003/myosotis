"""
Pydantic schemas for API request/response models with multilingual support
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum

from ..core.model_config import (
    MODEL_GENDER, MODEL_GROUP, MODEL_AREA, MODEL_EMOTION,
    MODEL_LANGUAGES, MODEL_ENGLISH_ACCENTS
)
from ..core.request_queue import JobPriority


class Language(str, Enum):
    VIETNAMESE = "vietnamese"
    ENGLISH = "english"


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class VoiceGroup(str, Enum):
    STORY = "story"
    NEWS = "news"
    AUDIOBOOK = "audiobook"
    INTERVIEW = "interview"
    REVIEW = "review"


class VietnameseArea(str, Enum):
    NORTHERN = "northern"
    SOUTHERN = "southern"
    CENTRAL = "central"


class EnglishAccent(str, Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"


class VoiceEmotion(str, Enum):
    NEUTRAL = "neutral"
    SERIOUS = "serious"
    MONOTONE = "monotone"
    SAD = "sad"
    SURPRISED = "surprised"
    HAPPY = "happy"
    ANGRY = "angry"


class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class BaseResponse(BaseModel):
    success: bool = True


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseResponse):
    status: str
    message: str
    system_info: Optional[Dict[str, Any]] = None


class VoiceOptionsResponse(BaseResponse):
    voice_options: Dict[str, Any]
    advanced_options: Dict[str, Any]
    supported_languages: List[str]


class InteractiveVoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[Language] = Language.VIETNAMESE
    gender: Optional[VoiceGender] = VoiceGender.FEMALE
    group: Optional[VoiceGroup] = VoiceGroup.STORY
    
    # Area for Vietnamese, Accent for English - dynamic validation
    area_or_accent: Optional[str] = "northern"  # Default Vietnamese area
    
    emotion: Optional[VoiceEmotion] = VoiceEmotion.NEUTRAL
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    random_seed: Optional[int] = Field(9527, ge=1, le=99999)
    
    # Advanced processing options
    enable_chunking: Optional[bool] = True
    chunk_overlap: Optional[int] = Field(50, ge=0, le=200)
    prosody_consistency: Optional[float] = Field(1.0, ge=0.5, le=1.5)
    
    # Async processing
    async_processing: Optional[bool] = False
    priority: Optional[JobPriority] = JobPriority.NORMAL
    
    @validator('area_or_accent')
    def validate_area_or_accent(cls, v, values):
        """Validate area_or_accent based on language"""
        language = values.get('language', Language.VIETNAMESE)
        
        if language == Language.VIETNAMESE:
            if v not in [area.value for area in VietnameseArea]:
                raise ValueError(f"Invalid Vietnamese area: {v}")
        elif language == Language.ENGLISH:
            if v not in [accent.value for accent in EnglishAccent]:
                raise ValueError(f"Invalid English accent: {v}")
        
        return v


class VoiceCloningRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[Language] = Language.VIETNAMESE
    use_default_sample: bool = True
    default_sample_id: Optional[str] = None
    reference_text: Optional[str] = None
    reference_audio_base64: Optional[str] = None
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)
    random_seed: Optional[int] = Field(9527, ge=1, le=99999)
    
    # Advanced processing options
    enable_chunking: Optional[bool] = True
    chunk_overlap: Optional[int] = Field(50, ge=0, le=200)
    voice_consistency: Optional[float] = Field(1.0, ge=0.5, le=1.5)
    
    # Async processing
    async_processing: Optional[bool] = False
    priority: Optional[JobPriority] = JobPriority.NORMAL


class SynthesisResponse(BaseResponse):
    audio_data: Optional[str] = None  # Base64 encoded audio
    generation_time: Optional[float] = None
    total_time: Optional[float] = None
    parameters_used: Optional[Dict[str, Any]] = None
    audio_size_bytes: Optional[int] = None
    voice_cloning: Optional[bool] = None
    audio_file_path: Optional[str] = None
    audio_filename: Optional[str] = None
    
    # Enhanced multilingual info
    language: Optional[str] = None
    gpu_used: Optional[int] = None
    chunking_used: Optional[bool] = None
    chunk_count: Optional[int] = None
    processing_stats: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class AsyncJobResponse(BaseResponse):
    job_id: str
    message: str
    estimated_completion_time: Optional[float] = None


class JobStatusResponse(BaseResponse):
    job_id: str
    status: str
    progress_percent: float
    stage: str
    message: str
    estimated_remaining_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    created_at: Optional[float] = None
    started_at: Optional[float] = None
    duration: Optional[float] = None


class ReferenceSamplesResponse(BaseResponse):
    samples: Dict[str, Any]
    total_samples: int
    languages: List[str]


class SystemStatusResponse(BaseResponse):
    gpu_status: Dict[str, Any]
    queue_status: Dict[str, Any]
    performance_stats: Dict[str, Any]
    system_resources: Dict[str, Any]


class SynthesisResponse(BaseResponse):
    audio_data: str
    audio_format: str = "wav"
    generation_time: float
    total_time: float
    parameters_used: Dict[str, Any]
    audio_size_bytes: int
    voice_cloning: bool = False
    audio_file_path: Optional[str] = None  # Path to saved audio file
    audio_filename: Optional[str] = None   # Filename of saved audio file
    # Enhanced fields for long text processing
    chunking_used: bool = False
    chunk_count: int = 1
    processing_stats: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    voice_consistency_score: Optional[float] = None


class ProcessingProgressResponse(BaseResponse):
    stage: str  # analysis, chunking, synthesis, concatenation, complete
    progress: float  # 0-100
    message: str
    chunk_info: Optional[Dict[str, Any]] = None
    estimated_remaining_time: Optional[float] = None
    errors: Optional[List[str]] = None


class TextAnalysisResponse(BaseResponse):
    text_length: int
    estimated_speaking_time: float
    language_complexity: float
    prosody_patterns: List[str]
    requires_chunking: bool
    optimal_chunk_size: int
    estimated_processing_time: float
    memory_requirement: float


class ReferenceSamplesResponse(BaseResponse):
    reference_samples: List[Dict[str, Any]]
    total_count: int
    upload_info: Dict[str, Any]


# Async Processing Schemas
class AsyncJobRequest(BaseModel):
    """Base request for async job processing"""
    job_type: str = Field(..., description="Type of job (interactive_voice | voice_cloning)")
    priority: Optional[JobPriority] = JobPriority.NORMAL
    

class AsyncJobResponse(BaseModel):
    """Response for async job submission"""
    job_id: str
    status: str
    message: str
    estimated_completion_time: Optional[float] = None
    queue_position: Optional[int] = None


class JobStatusResponse(BaseModel):
    """Response for job status query"""
    job_id: str
    status: str
    progress: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    estimated_remaining_time: Optional[float] = None
