"""
VietVoice TTS - Vietnamese Text-to-Speech Library
"""

from .core.model_config import ModelConfig, TTSConfig, MODEL_GENDER, MODEL_GROUP, MODEL_AREA, MODEL_EMOTION
from .core.tts_engine import TTSEngine
# Import from the high-level API module (high_level_api.py)
from .high_level_api import TTSApi, synthesize, synthesize_to_bytes

__version__ = "0.1.0"

__all__ = [
    "ModelConfig",
    "TTSConfig",  # Backward compatibility
    "TTSEngine",
    "TTSApi",
    "synthesize",
    "synthesize_to_bytes",
    "MODEL_GENDER",
    "MODEL_GROUP",
    "MODEL_AREA",
    "MODEL_EMOTION",
] 