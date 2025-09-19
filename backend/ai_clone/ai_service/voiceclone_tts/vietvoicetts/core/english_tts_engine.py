"""
English TTS Engine using F5-TTS Library
Real implementation for high-quality English speech synthesis
"""

import os
import logging
import tempfile
import numpy as np
import soundfile as sf
from typing import Optional

try:
    from f5_tts.api import F5TTS
except ImportError:
    F5TTS = None

logger = logging.getLogger(__name__)

# Global model cache for performance optimization
_model_cache = {}
_cache_lock = None

def _get_cache_lock():
    """Get thread-safe cache lock"""
    global _cache_lock
    if _cache_lock is None:
        import threading
        _cache_lock = threading.RLock()
    return _cache_lock


class EnglishTTSEngine:
    """English TTS Engine using F5-TTS library for high-quality synthesis"""
    
    def __init__(self, config):
        """Initialize the English TTS engine"""
        self.config = config
        self.model = None
        self.model_dir = getattr(config, 'english_model_dir', '/home/hieu/ai_giasu/voiceclone_tts/model_english')
        self.sample_rate = getattr(config, 'sample_rate', 24000)
        self.device = None  # Will be set during model loading
        
        # Create a model session manager for compatibility with the API services
        from .model import ModelSessionManager
        from .model_config import ModelConfig
        
        # Create English-specific model config
        english_config = ModelConfig(
            language="english",
            english_model_path=self.model_dir
        )
        self.model_session_manager = ModelSessionManager(english_config)
        
        logger.info("Initializing English TTS Engine with F5-TTS")
        self._load_model()
    
    def _load_model(self):
        """Load the F5-TTS model with caching and smart device selection"""
        if F5TTS is None:
            raise ImportError("F5-TTS library not installed. Run: pip install f5-tts")
        
        # Create cache key based on model directory and config
        cache_key = f"f5tts_{self.model_dir}_{self.sample_rate}"
        
        # Check if model is already cached
        with _get_cache_lock():
            if cache_key in _model_cache:
                cached_model, cached_device = _model_cache[cache_key]
                self.model = cached_model
                self.device = cached_device
                logger.info(f"Using cached F5-TTS model on {cached_device}")
                return

        try:
            import torch
            
            # Smart device selection with GPU testing
            device = self._select_optimal_device()
            self.device = device
            
            # First try to use the local model files
            model_path = os.path.join(self.model_dir, 'model_1000000.pt')
            config_path = os.path.join(self.model_dir, 'config.yaml')
            vocab_path = os.path.join(self.model_dir, 'vocab.txt')
            
            # Check if local model files exist
            local_files_exist = all(os.path.exists(path) for path in [model_path, config_path, vocab_path])
            
            if local_files_exist:
                logger.info(f"Using local F5-TTS model from {model_path}")
                # Initialize F5TTS with local model
                self.model = F5TTS(
                    model="F5TTS_v1_Base",  # Correct model name
                    ckpt_file=model_path,
                    vocab_file=vocab_path,
                    ode_method="euler",
                    use_ema=True,
                    device=device
                )
            else:
                logger.info("Using pre-trained F5-TTS model from HuggingFace")
                # Use pre-trained model from HuggingFace
                self.model = F5TTS(
                    model="F5TTS_v1_Base",  # Correct model name
                    ode_method="euler",
                    use_ema=True,
                    device=device
                )
            
            # Cache the model for future use
            with _get_cache_lock():
                _model_cache[cache_key] = (self.model, device)
            
            logger.info(f"F5-TTS model loaded successfully on {device} and cached")
            
        except Exception as e:
            logger.error(f"Failed to load F5-TTS model: {e}")
            raise RuntimeError(f"Could not initialize F5-TTS: {e}")
    
    def _select_optimal_device(self):
        """Select the optimal device for F5-TTS with smart GPU testing"""
        import torch
        
        # Check environment variable for forced device selection
        forced_device = os.environ.get('F5_TTS_DEVICE', None)
        if forced_device:
            logger.info(f"Using forced device from environment: {forced_device}")
            return forced_device
        
        if not torch.cuda.is_available():
            logger.info("CUDA not available, using CPU")
            return "cpu"
        
        try:
            # Test GPU compatibility with a more comprehensive test
            device = "cuda:0"  # Try first GPU
            torch.cuda.set_device(0)
            
            # More thorough GPU compatibility test
            test_size = 1000
            test_tensor = torch.randn(test_size, test_size, device=device, dtype=torch.float32)
            result = torch.mm(test_tensor, test_tensor.T)  # Matrix multiplication test
            result = result.cpu()  # Move back to CPU
            
            # Test memory allocation/deallocation
            torch.cuda.empty_cache()
            
            logger.info(f"GPU compatibility test passed, using {device} for F5-TTS")
            return device
            
        except Exception as e:
            logger.warning(f"GPU compatibility test failed: {e}")
            logger.info("Falling back to CPU for F5-TTS to ensure stability")
            return "cpu"
    
    def _get_default_reference(self, gender="female"):
        """Get default reference audio for voice cloning based on gender"""
        # For F5-TTS, we need to provide a reference audio file
        
        # Gender-specific reference texts and files
        if gender.lower() == "female":
            ref_text = "There is no greater harm than that of time wasted."
            ref_filename = "ref_female.wav"
        else:
            ref_text = "Our distrust is very expensive."
            ref_filename = "ref_male.wav"
        
        # Check for gender-specific reference files
        default_ref_path = os.path.join(self.model_dir, ref_filename)
        
        # Try to find any existing audio file in the model directory for reference
        import glob
        audio_files = glob.glob(os.path.join(self.model_dir, "*.wav")) + \
                     glob.glob(os.path.join(self.model_dir, "*.mp3")) + \
                     glob.glob(os.path.join(self.model_dir, "*.flac"))
        
        if os.path.exists(default_ref_path):
            logger.info(f"Using gender-specific reference: {default_ref_path}")
            return default_ref_path, ref_text
        elif audio_files:
            # Fallback to first available audio file
            default_ref_path = audio_files[0]
            logger.info(f"Using existing audio file as reference: {default_ref_path}")
            return default_ref_path, ref_text
        else:
            # Create a simple reference audio file as last resort
            logger.warning("No reference audio found, creating synthetic reference")
            return self._create_default_reference_audio(), ref_text
    
    def _create_default_reference_audio(self):
        """Create a basic reference audio file for F5-TTS"""
        try:
            # Create a simple reference audio with a neutral tone
            sample_rate = self.sample_rate
            duration = 2.0  # 2 seconds
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Create a more natural sounding reference using multiple frequencies
            # This creates a more voice-like sound than a pure sine wave
            fundamental = 150  # Fundamental frequency for a neutral voice
            audio = (np.sin(2 * np.pi * fundamental * t) * 0.3 +
                    np.sin(2 * np.pi * fundamental * 2 * t) * 0.1 +
                    np.sin(2 * np.pi * fundamental * 3 * t) * 0.05)
            
            # Add some variation to make it more voice-like
            audio = audio * (1 + 0.1 * np.sin(2 * np.pi * 2 * t))
            
            # Apply a simple envelope
            envelope = np.exp(-t * 0.5)  # Decay envelope
            audio = audio * envelope
            
            # Save to default reference file
            default_ref_path = os.path.join(self.model_dir, "default_ref.wav")
            sf.write(default_ref_path, audio.astype(np.float32), sample_rate)
            
            logger.info(f"Created default reference audio: {default_ref_path}")
            return default_ref_path
            
        except Exception as e:
            logger.error(f"Failed to create default reference audio: {e}")
            # Fall back to creating a temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_path = f.name
            
            # Create minimal audio
            audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate)) * 0.3
            sf.write(temp_path, audio.astype(np.float32), sample_rate)
            return temp_path
    
    def _synthesize_f5tts(self, text: str, reference_audio=None, reference_text=None, gender="female"):
        """Synthesize speech using F5-TTS"""
        try:
            # F5-TTS always requires reference audio and text
            if reference_audio is None or reference_text is None:
                reference_audio, reference_text = self._get_default_reference(gender)
            
            # Ensure we have valid reference values
            if reference_audio is None or reference_text is None:
                raise ValueError("Could not get valid reference audio and text for F5-TTS")
            
            # Generate speech using F5-TTS with required parameters
            logger.info(f"Using reference audio: {reference_audio}")
            logger.info(f"Reference text: {reference_text}")
            
            result = self.model.infer(
                ref_file=reference_audio,
                ref_text=reference_text,
                gen_text=text,
                remove_silence=True
            )
            
            # Handle different return formats from F5-TTS
            if isinstance(result, tuple):
                if len(result) == 2:
                    generated_audio, sample_rate = result
                elif len(result) == 3:
                    generated_audio, sample_rate, _ = result  # Third value might be spectrogram
                else:
                    # Take first two values
                    generated_audio, sample_rate = result[0], result[1]
            else:
                # Single return value
                generated_audio = result
                sample_rate = self.sample_rate
            
            # Convert to numpy array if needed
            if hasattr(generated_audio, 'numpy'):
                generated_audio = generated_audio.numpy()
            elif hasattr(generated_audio, 'cpu'):
                generated_audio = generated_audio.cpu().numpy()
            
            # Ensure sample_rate is integer
            if hasattr(sample_rate, 'item'):
                sample_rate = int(sample_rate.item())
            elif not isinstance(sample_rate, int):
                sample_rate = int(sample_rate)
            
            # Ensure correct format  
            if generated_audio.dtype != np.float32:
                generated_audio = generated_audio.astype(np.float32)
            
            # Normalize audio
            if np.max(np.abs(generated_audio)) > 0:
                generated_audio = generated_audio / np.max(np.abs(generated_audio)) * 0.95
            
            return generated_audio, sample_rate
            
        except Exception as e:
            logger.error(f"F5-TTS synthesis failed: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}")
    
    def synthesize(self, text: str, reference_audio: Optional[str] = None, 
                  reference_text: Optional[str] = None, output_path: Optional[str] = None,
                  reference_audio_path: Optional[str] = None, gender: str = "female", **kwargs):
        """
        Synthesize English speech from text using F5-TTS
        
        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio for voice cloning (backward compatibility)
            reference_audio_path: Path to reference audio for voice cloning
            reference_text: Text corresponding to reference audio
            output_path: Path to save output audio file
            gender: Voice gender for default reference selection (female/male)
            
        Returns:
            Tuple of (audio_data: np.ndarray, generation_time: float)
        """
        try:
            import time
            start_time = time.time()
            
            logger.info(f"Synthesizing English text: {text[:50]}... (gender: {gender})")
            
            # Handle backward compatibility for reference_audio parameter
            ref_audio_path = reference_audio or reference_audio_path
            
            # Generate audio using F5-TTS with gender-specific reference
            audio_data, sample_rate = self._synthesize_f5tts(
                text, 
                ref_audio_path, 
                reference_text,
                gender
            )
            
            # Create output file if not specified
            if output_path is None:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    output_path = f.name
            
            # Ensure audio is 1D array like Vietnamese TTS
            if len(audio_data.shape) > 1:
                audio_data = audio_data.reshape(-1)
            
            # Save audio file using the same format as Vietnamese TTS
            sf.write(output_path, audio_data, sample_rate, format='WAVEX')
            
            generation_time = time.time() - start_time
            
            logger.info(f"English synthesis completed: {output_path}")
            
            # Return audio data and generation time to match Vietnamese TTS interface
            # Keep as float32 like Vietnamese TTS
            return audio_data, generation_time
            
        except Exception as e:
            logger.error(f"English TTS synthesis failed: {e}")
            raise RuntimeError(f"Failed to synthesize English speech: {e}")
    
    def is_available(self) -> bool:
        """Check if the English TTS engine is available"""
        return self.model is not None
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'model') and self.model is not None:
            # F5-TTS doesn't require explicit cleanup, but we can clear the reference
            self.model = None
            logger.info("English TTS engine cleaned up")
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return ['en', 'english']


# Backward compatibility - create factory function
def create_english_tts_engine(config):
    """Factory function to create English TTS engine (backward compatibility)"""
    return EnglishTTSEngine(config)
