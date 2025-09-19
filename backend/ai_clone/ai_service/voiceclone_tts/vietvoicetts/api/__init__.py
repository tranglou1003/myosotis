"""
FastAPI-based REST API for VietVoice TTS
"""

from .app import create_app
from .models import *
from .schemas import *
from .services import *

__all__ = [
    "create_app",
]
