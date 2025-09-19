from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import os


def str_to_bool(value: str) -> bool:
    """Convert string to boolean"""
    return value.lower() in ('true', '1', 'yes', 'on')


@dataclass
class AppConfig:
    """Application configuration class with multilingual support"""
    app_name: str = "Voice Cloning Model - Multilingual TTS"
    description: str = "Advanced Vietnamese-English TTS System with F5-TTS ONNX models"
    version: str = "2.1.0"
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8888")))
    reload: bool = field(default_factory=lambda: False)  # Force disable reload for production stability
    workers: int = field(default_factory=lambda: int(os.getenv("WORKERS", "1")))
    enable_docs: bool = True
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: [
        "*"
    ])
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "info"))
    upload_dir: str = field(default_factory=lambda: os.getenv("UPLOAD_DIR", "uploads"))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", str(16 * 1024 * 1024))))  # 16MB
    allowed_audio_formats: List[str] = field(
        default_factory=lambda: ["wav", "mp3", "m4a", "flac", "ogg"]
    )
    
    # Multilingual and performance settings
    enable_multilingual: bool = field(default_factory=lambda: str_to_bool(os.getenv("ENABLE_MULTILINGUAL", "true")))
    supported_languages: List[str] = field(default_factory=lambda: ["vietnamese", "english"])
    enable_gpu_acceleration: bool = field(default_factory=lambda: str_to_bool(os.getenv("ENABLE_GPU", "true")))
    max_concurrent_requests: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT", "10")))
    enable_async_processing: bool = field(default_factory=lambda: str_to_bool(os.getenv("ENABLE_ASYNC", "true")))
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Ensure upload directory exists
        Path(self.upload_dir).mkdir(exist_ok=True)


@dataclass
class TTSModelConfig:
    """TTS model configuration with multilingual support"""
    # Language settings
    language: str = "vietnamese"  # vietnamese | english
    model_path: Optional[str] = None
    
    # Performance settings
    device: str = "auto"  # auto | cpu | cuda:0 | cuda:1
    use_gpu: bool = True
    gpu_id: Optional[int] = None  # None for auto-selection
    enable_gpu_load_balancing: bool = True
    
    # Caching and optimization
    cache_size: int = 100
    enable_model_caching: bool = True
    max_concurrent_sessions: int = 5
    
    # Timeouts and limits
    timeout: int = 300  # 5 minutes default timeout
    max_text_length: int = 10000
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.use_gpu and self.device == "cpu":
            self.device = "auto"  # Let GPU manager decide
        
        # Validate language
        from ..core.model_config import MODEL_LANGUAGES
        if self.language not in MODEL_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.language}")


@dataclass
class VoiceProfile:
    """Voice profile data model with multilingual support"""
    id: str
    name: str
    language: str  # vietnamese | english
    gender: str
    group: str
    area_or_accent: str  # area for Vietnamese, accent for English
    emotion: str
    description: Optional[str] = None
    sample_audio: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "language": self.language,
            "gender": self.gender,
            "group": self.group,
            "area_or_accent": self.area_or_accent,
            "emotion": self.emotion,
            "description": self.description,
            "sample_audio": self.sample_audio
        }


@dataclass
class ReferenceSample:
    """Reference sample data model"""
    id: str
    name: str
    description: str
    audio_path: str
    text: str
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "audio_path": self.audio_path,
            "text": self.text,
            "duration": self.duration
        }


@dataclass
class SynthesisRequest:
    """Base synthesis request model with multilingual support"""
    text: str
    language: str = "vietnamese"  # vietnamese | english
    speed: float = 1.0
    random_seed: int = 9527
    output_format: str = "wav"
    
    # Async processing options
    async_processing: bool = False
    priority: str = "normal"  # low | normal | high | urgent
    
    def validate(self):
        """Validate request parameters"""
        if not self.text or len(self.text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        if len(self.text) > 10000:
            raise ValueError("Text too long (max 10000 characters)")
        if not 0.5 <= self.speed <= 2.0:
            raise ValueError("Speed must be between 0.5 and 2.0")
        if not 1 <= self.random_seed <= 99999:
            raise ValueError("Random seed must be between 1 and 99999")
        
        # Validate language
        from ..core.model_config import MODEL_LANGUAGES
        if self.language not in MODEL_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.language}")


@dataclass
class InteractiveVoiceRequest(SynthesisRequest):
    """Interactive voice synthesis request with multilingual support"""
    gender: str = "female"
    group: str = "story"
    area_or_accent: str = "northern"  # area for Vietnamese, accent for English
    emotion: str = "neutral"
    
    # Long text processing options
    enable_chunking: bool = True
    chunk_overlap: int = 50
    prosody_consistency: float = 1.0
    
    def validate(self):
        """Validate interactive voice request"""
        super().validate()
        
        # Language-specific validation
        if self.language == "vietnamese":
            from ..core.model_config import MODEL_AREA
            if self.area_or_accent not in MODEL_AREA:
                raise ValueError(f"Invalid Vietnamese area: {self.area_or_accent}")
        elif self.language == "english":
            from ..core.model_config import MODEL_ENGLISH_ACCENTS
            if self.area_or_accent not in MODEL_ENGLISH_ACCENTS:
                raise ValueError(f"Invalid English accent: {self.area_or_accent}")


@dataclass
class VoiceCloningRequest(SynthesisRequest):
    """Voice cloning synthesis request with multilingual support"""
    use_default_sample: bool = True
    default_sample_id: Optional[str] = None
    reference_text: Optional[str] = None
    reference_audio_base64: Optional[str] = None
    reference_audio_path: Optional[str] = None
    
    # Advanced voice cloning options
    enable_chunking: bool = True
    chunk_overlap: int = 50
    voice_consistency: float = 1.0
    
    def validate(self):
        """Validate voice cloning request"""
        super().validate()
        
        if self.use_default_sample:
            if not self.default_sample_id:
                raise ValueError("Default sample ID required when using default sample")
        else:
            if not self.reference_text:
                raise ValueError("Reference text required for custom reference audio")
            if not self.reference_audio_base64 and not self.reference_audio_path:
                raise ValueError("Reference audio required (base64 or file path)")
            # Note: Reference text doesn't need to match target text exactly
            # It just helps the model understand the voice characteristics


@dataclass
class SynthesisResult:
    """Synthesis operation result with enhanced multilingual support"""
    success: bool
    language: Optional[str] = None
    job_id: Optional[str] = None  # For async processing
    audio_base64: Optional[str] = None
    audio_path: Optional[str] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    # Enhanced processing information
    gpu_used: Optional[int] = None
    chunking_used: bool = False
    chunk_count: Optional[int] = None
    performance_stats: Optional[Dict[str, Any]] = None
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary"""
        response = {
            "success": self.success,
            "language": self.language,
            "job_id": self.job_id,
            "audio_base64": self.audio_base64,
            "duration": self.duration,
            "processing_time": self.processing_time,
            "gpu_used": self.gpu_used,
            "chunking_used": self.chunking_used,
            "chunk_count": self.chunk_count,
            "performance_stats": self.performance_stats
        }
        
        if not self.success:
            response["error"] = self.error_message
            
        return response


# Async job response models
@dataclass
class AsyncJobResponse:
    """Response for async job submission"""
    success: bool
    job_id: str
    message: str
    estimated_completion_time: Optional[float] = None


@dataclass  
class JobStatusResponse:
    """Response for job status queries"""
    job_id: str
    status: str
    progress_percent: float
    message: str
    result: Optional[Dict[str, Any]] = None
    estimated_remaining_time: Optional[float] = None


class Constants:
    """Application constants with multilingual support"""
    
    # Language support
    SUPPORTED_LANGUAGES = ["vietnamese", "english"]
    
    # Voice options - Vietnamese
    VIETNAMESE_GENDERS = ["female", "male"]
    VIETNAMESE_GROUPS = ["story", "news", "audiobook", "interview", "review"]
    VIETNAMESE_AREAS = ["northern", "southern", "central"]
    VIETNAMESE_EMOTIONS = ["neutral", "serious", "monotone", "sad", "surprised", "happy", "angry"]
    
    # Voice options - English
    ENGLISH_GENDERS = ["female", "male"]
    ENGLISH_GROUPS = ["story", "news", "audiobook", "interview", "review"]
    ENGLISH_ACCENTS = ["american", "british", "australian"]
    ENGLISH_EMOTIONS = ["neutral", "serious", "monotone", "sad", "surprised", "happy", "angry"]
    
    # Audio formats
    SUPPORTED_FORMATS = ["wav", "mp3", "m4a", "flac", "ogg"]
    
    # Limits - Enhanced for long text support (5K-10K characters)
    MAX_TEXT_LENGTH = 10000  # Support up to 10K characters for interactive voice
    MAX_VOICE_CLONING_TEXT_LENGTH = 10000  # Support up to 10K characters for voice cloning
    MAX_REFERENCE_TEXT_LENGTH = 2000  # Increased from 1000 for better voice cloning
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB for reference audio
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0
    MIN_SEED = 1
    MAX_SEED = 99999
    
    # Processing limits for long text
    MAX_CHUNK_COUNT = 50  # Maximum number of chunks for very long text
    MAX_PROCESSING_TIME = 600  # Maximum processing time in seconds (10 minutes)
    CHUNK_OVERLAP_CHARS = 50  # Character overlap between chunks for context preservation
    
    # Chunking thresholds - Improved for voice cloning
    CHUNKING_THRESHOLD_CHARS = 1000  # Increased from 800 - Start chunking at 1000 characters
    OPTIMAL_CHUNK_SIZE = 1500  # Increased from 1000 - Optimal chunk size for processing
    MIN_CHUNK_SIZE = 500  # Increased from 300 - Minimum chunk size for quality
    MAX_CHUNK_SIZE = 2000  # Increased from 1200 - Maximum chunk size
    
    # Voice cloning specific limits
    MAX_REFERENCE_AUDIO_DURATION = 60  # Maximum reference audio duration in seconds
    MIN_REFERENCE_AUDIO_DURATION = 3   # Minimum reference audio duration in seconds
    VOICE_CLONING_MIN_CHUNK_SIZE = 200  # Minimum chunk size for voice cloning quality
    
    # Async processing and performance
    MAX_CONCURRENT_REQUESTS = 10  # Maximum concurrent requests
    DEFAULT_REQUEST_TIMEOUT = 300  # 5 minutes default timeout
    CLEANUP_INTERVAL = 3600  # 1 hour job cleanup interval
    MAX_REQUESTS_PER_MINUTE = 10  # Rate limiting per IP
    
    # GPU and performance constants
    GPU_MEMORY_THRESHOLD = 0.8  # 80% memory usage threshold
    MODEL_CACHE_SIZE = 2  # Cache 2 models (Vietnamese + English)
    SESSION_POOL_SIZE = 5  # ONNX session pool size per GPU
    
    # Default reference samples - Vietnamese
    VIETNAMESE_DEFAULT_SAMPLES = {
        "female_northern_neutral": {
            "id": "vn_female_northern_neutral",
            "name": "Vietnamese Female Northern Neutral",
            "language": "vietnamese",
            "description": "Neutral female voice from Northern Vietnam",
            "audio_path": "samples/vn_female_northern_neutral.wav",
            "text": "Xin chào, tôi là giọng nói nữ miền Bắc với phong cách trung tính."
        },
        "male_southern_story": {
            "id": "vn_male_southern_story", 
            "name": "Vietnamese Male Southern Story",
            "language": "vietnamese",
            "description": "Story-telling male voice from Southern Vietnam",
            "audio_path": "samples/vn_male_southern_story.wav",
            "text": "Xin chào, tôi là giọng nói nam miền Nam thích hợp cho việc kể chuyện."
        },
        "female_central_news": {
            "id": "vn_female_central_news",
            "name": "Vietnamese Female Central News",
            "language": "vietnamese",
            "description": "News-style female voice from Central Vietnam",
            "audio_path": "samples/vn_female_central_news.wav", 
            "text": "Xin chào, tôi là giọng nói nữ miền Trung phù hợp cho tin tức."
        }
    }
    
    # Default reference samples - English
    ENGLISH_DEFAULT_SAMPLES = {
        "female_american_neutral": {
            "id": "en_female_american_neutral",
            "name": "English Female American Neutral",
            "language": "english",
            "description": "Neutral female voice with American accent",
            "audio_path": "samples/en_female_american_neutral.wav",
            "text": "Hello, I am a neutral female voice with an American accent."
        },
        "male_british_story": {
            "id": "en_male_british_story",
            "name": "English Male British Story",
            "language": "english",
            "description": "Story-telling male voice with British accent",
            "audio_path": "samples/en_male_british_story.wav",
            "text": "Hello, I am a male British voice perfect for storytelling."
        },
        "female_australian_news": {
            "id": "en_female_australian_news",
            "name": "English Female Australian News",
            "language": "english",
            "description": "News-style female voice with Australian accent",
            "audio_path": "samples/en_female_australian_news.wav",
            "text": "Hello, I am a female Australian voice suitable for news."
        }
    }
    
    # Combined default samples
    DEFAULT_SAMPLES = {**VIETNAMESE_DEFAULT_SAMPLES, **ENGLISH_DEFAULT_SAMPLES}
