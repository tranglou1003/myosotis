"""
Core TTS engine modules with multilingual support and GPU optimization
"""

from .model_config import (
    ModelConfig, TTSConfig, 
    MODEL_GENDER, MODEL_GROUP, MODEL_AREA, MODEL_EMOTION,
    MODEL_LANGUAGES, MODEL_ENGLISH_ACCENTS, LANGUAGE_CONFIGS
)
from .model import ModelSessionManager
from .tts_engine import TTSEngine
from .text_processor import TextProcessor
from .audio_processor import AudioProcessor
from .advanced_text_processor import AdvancedTextProcessor, ChunkInfo, TextAnalysis
from .performance_optimizer import PerformanceOptimizer, PerformanceMetrics, ProcessingStats
from .voice_context_manager import VoiceContextManager, VoiceContext, ChunkVoiceState
from .model_cache import GlobalModelCache, get_global_cache, clear_global_cache, shutdown_global_cache

# New multilingual and performance components
from .gpu_manager import GPUManager, get_gpu_manager, initialize_gpu_manager, shutdown_gpu_manager
from .request_queue import (
    RequestQueueManager, TTSJob, JobStatus, JobPriority,
    get_queue_manager, initialize_queue_manager, shutdown_queue_manager
)

__all__ = [
    # Core components
    "ModelConfig",
    "TTSConfig",  # Backward compatibility
    "ModelSessionManager",
    "TTSEngine",
    "TextProcessor",
    "AudioProcessor",
    "AdvancedTextProcessor",
    "ChunkInfo",
    "TextAnalysis",
    "PerformanceOptimizer",
    "PerformanceMetrics",
    "ProcessingStats",
    "VoiceContextManager",
    "VoiceContext",
    "ChunkVoiceState",
    
    # Language constants
    "MODEL_GENDER",
    "MODEL_GROUP",
    "MODEL_AREA",
    "MODEL_EMOTION",
    "MODEL_LANGUAGES",
    "MODEL_ENGLISH_ACCENTS",
    "LANGUAGE_CONFIGS",
    
    # GPU and performance management
    "GPUManager",
    "get_gpu_manager",
    "initialize_gpu_manager", 
    "shutdown_gpu_manager",
    
    # Request queue management
    "RequestQueueManager",
    "TTSJob",
    "JobStatus",
    "JobPriority",
    "get_queue_manager",
    "initialize_queue_manager",
    "shutdown_queue_manager",
] 