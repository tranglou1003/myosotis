"""
Configuration management for TTS inference with multilingual support
"""

import os
import urllib.request
import urllib.error
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


# Model constants
MODEL_GENDER = ["male", "female"]
MODEL_GROUP = ["story", "news", "audiobook", "interview", "review"]
MODEL_AREA = ["northern", "southern", "central"]
MODEL_EMOTION = ["neutral", "serious", "monotone", "sad", "surprised", "happy", "angry"]

# Language support constants
MODEL_LANGUAGES = ["vietnamese", "english"]
MODEL_ENGLISH_ACCENTS = ["american", "british", "australian"]

# Language-specific configurations
LANGUAGE_CONFIGS = {
    "vietnamese": {
        "areas": ["northern", "southern", "central"],
        "default_model_path": "~/.cache/vietvoicetts",
        "default_model_filename": "model-bin.pt",
        "default_model_url": "https://huggingface.co/nguyenvulebinh/VietVoice-TTS/resolve/main/model-bin.pt"
    },
    "english": {
        "accents": ["american", "british", "australian"],
        "default_model_path": "model_english",
        "default_model_filename": "model_1000000.pt",
        "default_model_url": "https://huggingface.co/F5-TTS/F5-TTS/resolve/main/F5TTS_Base/model_1000000.pt"
    }
}


@dataclass
class ModelConfig:
    """Configuration for TTS model inference with multilingual support"""
    
    # Language settings - NEW MULTILINGUAL SUPPORT
    language: str = "vietnamese"  # vietnamese | english
    
    # Model settings - Enhanced for dual language support
    model_url: Optional[str] = None  # Will be set based on language if not provided
    model_cache_dir: Optional[str] = None  # Will be set based on language if not provided
    model_filename: Optional[str] = None  # Will be set based on language if not provided
    
    # Alternative model paths for multilingual setup
    vietnamese_model_path: str = "~/.cache/vietvoicetts"
    english_model_path: str = "model_english"
    
    # Core inference settings
    nfe_step: int = 32
    fuse_nfe: int = 1
    sample_rate: int = 24000
    speed: float = 1.0
    random_seed: int = 9527
    hop_length: int = 256
    
    # Text processing
    pause_punctuation: str = r".,?!:"
    
    # Audio processing
    cross_fade_duration: float = 0.1  # Duration in seconds for cross-fading between chunks
    max_chunk_duration: float = 45.0  # Increased back to 45.0, will be dynamically adjusted based on reference audio
    min_target_duration: float = 1.0  # Minimum duration in seconds for target audio
    
    # GPU and performance settings - NEW for dual RTX 5090 support
    use_gpu: bool = True  # Enable GPU acceleration
    gpu_id: Optional[int] = None  # Specific GPU ID to use (None for auto-selection)
    preferred_gpu_id: Optional[int] = None  # None for auto-selection, 0 or 1 for specific GPU
    use_gpu_load_balancing: bool = True  # Enable automatic GPU load balancing
    enable_model_caching: bool = True  # Enable model session caching
    max_concurrent_requests: int = 10  # Maximum concurrent requests
    
    # ONNX Runtime settings
    log_severity_level: int = 4
    log_verbosity_level: int = 4
    inter_op_num_threads: int = 0
    intra_op_num_threads: int = 0
    enable_cpu_mem_arena: bool = True

    def __post_init__(self):
        """Post-initialization validation with multilingual support"""
        # Validate language selection first
        if self.language not in MODEL_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.language}. Supported: {MODEL_LANGUAGES}")
        
        # Set language-specific defaults based on user's choice
        self._set_language_defaults()
        
        # For English, check if local model exists and update paths accordingly
        if self.language == "english":
            english_local_model = "/home/quangnm/seadev_backend_backup/ai_service/voiceclone_tts/model_english/model_1000000.pt"
            from pathlib import Path
            if Path(english_local_model).exists():
                self.model_url = None  # Disable URL download
                self.model_cache_dir = "/home/quangnm/seadev_backend_backup/ai_service/voiceclone_tts/model_english"
                self.model_filename = "model_1000000.pt"
        
        # Validate paths
        self.validate_paths()
    
    def _set_language_defaults(self):
        """Set default paths and URLs based on selected language"""
        lang_config = LANGUAGE_CONFIGS[self.language]
        
        if self.model_url is None:
            self.model_url = lang_config["default_model_url"]
        
        if self.model_cache_dir is None:
            self.model_cache_dir = lang_config["default_model_path"]
            
        if self.model_filename is None:
            self.model_filename = lang_config["default_model_filename"]
    
    @property
    def model_path(self) -> str:
        """Get the full path to the cached model file"""
        if self.language == "english" and not self.model_cache_dir.startswith("/"):
            # For English, use relative path from project root
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / self.model_cache_dir / self.model_filename)
        else:
            from pathlib import Path
            cache_dir = Path(self.model_cache_dir).expanduser()
            return str(cache_dir / self.model_filename)
    
    def get_language_specific_params(self) -> Dict[str, Any]:
        """Get language-specific parameters for voice synthesis"""
        if self.language == "vietnamese":
            return {
                "voice_params": ["gender", "group", "area", "emotion"],
                "areas": MODEL_AREA,
                "default_area": "northern"
            }
        elif self.language == "english":
            return {
                "voice_params": ["gender", "group", "accent", "emotion"],
                "accents": MODEL_ENGLISH_ACCENTS,
                "default_accent": "american"
            }
        return {}
    
    def _create_ssl_context(self):
        """Create SSL context for secure downloads with fallback options"""
        try:
            # Try to create default SSL context first
            context = ssl.create_default_context()
            return context
        except Exception:
            # If default context fails, create unverified context as fallback
            print("⚠️  Warning: Using unverified SSL context due to certificate issues")
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
    
    def _download_with_ssl_fallback(self, url: str, file_path: Path, progress_hook=None):
        """Download file with SSL fallback mechanism"""
        # Method 1: Try with default SSL context
        try:
            print("🔐 Attempting secure download...")
            urllib.request.urlretrieve(url, file_path, progress_hook)
            print(f"\n✅ Secure download successful!")
            return
        except urllib.error.URLError as e:
            if "SSL" in str(e) or "CERTIFICATE" in str(e):
                print(f"🔒 SSL error encountered: {e}")
                print("🔄 Trying with custom SSL context...")
            else:
                raise e
        
        # Method 2: Try with custom SSL context
        try:
            ssl_context = self._create_ssl_context()
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, file_path, progress_hook)
            print(f"\n✅ Download successful with custom SSL context!")
            return
        except Exception as e:
            print(f"❌ Custom SSL context failed: {e}")
        
        # Method 3: Last resort - unverified SSL (not recommended for production)
        try:
            print("⚠️  Attempting unverified download (not recommended for production)...")
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, file_path, progress_hook)
            print(f"\n⚠️  Download completed with unverified SSL!")
            print("📋 Please update your system certificates for better security.")
            return
        except Exception as e:
            raise RuntimeError(f"All download methods failed. Last error: {e}")
    
    def ensure_model_downloaded(self) -> str:
        """Ensure model is downloaded and cached, return path to model file"""
        print(f"[DEBUG] ensure_model_downloaded: language={self.language}, model_path={self.model_path}")
        
        model_path = Path(self.model_path)
        cache_dir = model_path.parent
        
        # For English, check if local model exists
        if self.language == "english":
            if not model_path.exists():
                raise RuntimeError(f"English model file not found at {model_path}. Please check the path.")
            print(f"♻️  Using local English model: {model_path}")
            return str(model_path)

        # For Vietnamese, use download logic
        
        # For Vietnamese, keep original logic
        cache_dir.mkdir(parents=True, exist_ok=True)
        if not model_path.exists():
            print(f"📥 Downloading model from {self.model_url}")
            print(f"💾 Saving to {model_path}")
            try:
                def progress_hook(block_num, block_size, total_size):
                    if total_size > 0:
                        percent = min(100, (block_num * block_size * 100) // total_size)
                        print(f"\r📊 Downloading: {percent}%", end='', flush=True)
                self._download_with_ssl_fallback(self.model_url, model_path, progress_hook)
            except Exception as e:
                if model_path.exists():
                    model_path.unlink()
                    print(f"🧹 Cleaned up partial download")
                error_msg = f"Failed to download model from {self.model_url}: {e}"
                suggestions = [
                    "1. Check your internet connection",
                    "2. Verify the model URL is accessible",
                    "3. Check if you're behind a corporate firewall",
                    "4. Try updating system certificates: sudo apt-get update && sudo apt-get install ca-certificates",
                    "5. Consider downloading the model manually and placing it in the cache directory"
                ]
                full_error = f"{error_msg}\n\nTroubleshooting suggestions:\n" + "\n".join(suggestions)
                raise RuntimeError(full_error)
        else:
            print(f"♻️  Using cached model: {model_path}")
        return str(model_path)
    
    def validate_paths(self):
        """Validate that required files exist or can be downloaded"""
        print(f"[DEBUG] validate_paths: language={self.language}, model_path={self.model_path}")
        try:
            # Ensure model is available (download if needed for Vietnamese, check existence for English)
            self.ensure_model_downloaded()
        except Exception as e:
            raise RuntimeError(f"Model validation failed: {e}")
    
    def validate_with_reference_audio(self, reference_audio_path: str) -> bool:
        """Validate configuration against a reference audio file"""
        try:
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(reference_audio_path).set_channels(1).set_frame_rate(self.sample_rate)
            ref_duration = len(audio_segment) / 1000.0  # Convert to seconds
            
            safety_margin = 1.0
            required_min_duration = ref_duration + safety_margin + self.min_target_duration
            
            if self.max_chunk_duration < required_min_duration:
                print(f"❌ Configuration Error:")
                print(f"   Reference audio: {ref_duration:.1f}s")
                print(f"   Min target duration: {self.min_target_duration:.1f}s") 
                print(f"   Safety margin: {safety_margin:.1f}s")
                print(f"   Required max_chunk_duration: >{required_min_duration:.1f}s")
                print(f"   Current max_chunk_duration: {self.max_chunk_duration:.1f}s")
                return False
            else:
                print(f"✅ Configuration valid:")
                print(f"   Reference audio: {ref_duration:.1f}s")
                print(f"   Max chunk duration: {self.max_chunk_duration:.1f}s")
                print(f"   Available target duration: {self.max_chunk_duration - ref_duration - safety_margin:.1f}s")
                return True
                
        except Exception as e:
            print(f"❌ Error validating reference audio: {e}")
            return False
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "ModelConfig":
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }


# Backward compatibility alias
TTSConfig = ModelConfig