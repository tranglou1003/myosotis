"""
Business logic and services for TTS API with long text support
"""

import base64
import tempfile
import time
import os
import uuid
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

from ..core import ModelConfig, TTSEngine
from ..core.model_config import MODEL_GENDER, MODEL_GROUP, MODEL_AREA, MODEL_EMOTION
from ..core.advanced_text_processor import AdvancedTextProcessor
from ..core.performance_optimizer import PerformanceOptimizer
from ..core.model_cache import get_global_cache
from ..core.performance_optimization import (
    get_optimized_manager, get_performance_monitor, get_request_batcher
)
from .schemas import SynthesisResponse
from .exceptions import TTSError, ValidationError
from .models import Constants, SynthesisResult, ReferenceSample


class TTSService:
    """Service class for TTS operations with long text support"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig(language="english")
        self._tts_engine: Optional[TTSEngine] = None
        # Setup results directory
        self.results_dir = Path(__file__).parent.parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize long text processing components
        self.advanced_text_processor = AdvancedTextProcessor()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Temporarily disable optimized manager to fix event loop issue
        # TODO: Re-enable after fixing async initialization
        # self.optimized_manager = get_optimized_manager()
        # self.performance_monitor = get_performance_monitor()
        # self.request_batcher = get_request_batcher()
        
        # Use simple performance monitor for now
        from vietvoicetts.core.performance_optimization import SimplePerformanceMonitor
        self.performance_monitor = SimplePerformanceMonitor()
        
        # Get global model cache (fallback)
        self.model_cache = get_global_cache()
    
    @property
    def tts_engine(self) -> TTSEngine:
        """Lazy initialization of TTS engine with optimized caching"""
        if self._tts_engine is None:
            start_time = time.time()
            
            # Create TTS engine with config - let it handle its own model loading
            self._tts_engine = TTSEngine(self.config)
            
            load_time = time.time() - start_time
            self.performance_monitor.record_request(load_time, cache_hit=False)
            
        return self._tts_engine
    
    def _generate_output_filename(self, prefix: str = "tts") -> str:
        """Generate unique filename for audio output"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.wav"
    
    def _get_output_path(self, filename: str) -> str:
        """Get full path for output file"""
        return str(self.results_dir / filename)
    
    def analyze_text_for_processing(self, text: str) -> Dict[str, Any]:
        """Analyze text and return processing recommendations"""
        analysis = self.advanced_text_processor.analyze_text_structure(text)
        performance_metrics = self.performance_optimizer.calculate_performance_metrics(text)
        
        return {
            "text_length": analysis.total_length,
            "estimated_speaking_time": analysis.estimated_speaking_time,
            "language_complexity": analysis.language_complexity,
            "prosody_patterns": analysis.prosody_patterns,
            "requires_chunking": analysis.requires_chunking,
            "optimal_chunk_size": analysis.optimal_chunk_size,
            "estimated_processing_time": performance_metrics.estimated_processing_time,
            "memory_requirement": performance_metrics.memory_requirement,
            "chunk_count": performance_metrics.optimal_chunk_count,
            "processing_complexity": performance_metrics.processing_complexity
        }
    
    def synthesize_interactive_voice(
        self,
        text: str,
        language: str = "vietnamese",
        gender: str = "female",
        group: str = "story", 
        area_or_accent: str = "northern",
        emotion: str = "neutral",
        speed: float = 1.0,
        random_seed: int = 9527,
        enable_chunking: bool = True,
        chunk_overlap: int = 50,
        prosody_consistency: float = 1.0,
        progress_callback: Optional[callable] = None
    ) -> SynthesisResponse:
        """Synthesize speech with interactive voice customization and long text support"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            start_time = time.time()
            
            # Input validation
            text = text.strip()
            if not text:
                raise ValidationError("Text cannot be empty")
            
            if len(text) > Constants.MAX_TEXT_LENGTH:
                raise ValidationError(f"Text too long. Maximum {Constants.MAX_TEXT_LENGTH} characters.")
            
            logger.info(f"Starting interactive voice synthesis for {len(text)} characters")
            
            # Analyze text for processing strategy
            analysis_data = self.analyze_text_for_processing(text)
            
            # Generate output filename
            filename = self._generate_output_filename("interactive_voice")
            output_path = self._get_output_path(filename)
            
            # Determine area/accent parameter based on language
            area_param = area_or_accent if language == "vietnamese" else None
            accent_param = area_or_accent if language == "english" else None
            
            # Update config with speed, seed, and language
            synthesis_config = ModelConfig(
                language=language,
                speed=speed,
                random_seed=random_seed
            )
            
            # Start generation timer right before actual synthesis
            generation_start_time = time.time()
            
            # Choose synthesis method based on text length and analysis
            if analysis_data["requires_chunking"] and enable_chunking:
                # Use long text synthesis with cached model
                audio_data, _ = self._synthesize_long_text_cached(
                    text, output_path, synthesis_config,
                    gender=gender, group=group, area=area_param, emotion=emotion,
                    chunk_overlap=chunk_overlap, prosody_consistency=prosody_consistency,
                    progress_callback=progress_callback
                )
                chunking_used = True
                chunk_count = analysis_data["chunk_count"]
            else:
                # Use standard synthesis with cached model
                model_session_manager = self.model_cache.get_model(synthesis_config)
                audio_data, _ = self._synthesize_with_cached_model(
                    text, output_path, model_session_manager, synthesis_config,
                    gender=gender, group=group, area=area_param, emotion=emotion
                )
                chunking_used = False
                chunk_count = 1
            
            generation_time = time.time() - generation_start_time
            total_time = time.time() - start_time
            
            # Convert audio to base64
            audio_base64 = self._audio_to_base64(audio_data)
            
            # Calculate audio size - handle both bytes and numpy arrays
            if isinstance(audio_data, bytes):
                audio_size = len(audio_data)
            elif hasattr(audio_data, 'dtype'):
                # numpy array - calculate based on dtype
                if audio_data.dtype == np.int16:
                    audio_size = len(audio_data) * 2  # int16 = 2 bytes per sample
                elif audio_data.dtype == np.float32:
                    audio_size = len(audio_data) * 4  # float32 = 4 bytes per sample
                else:
                    audio_size = audio_data.nbytes  # fallback to total bytes
            else:
                audio_size = len(audio_data) * 2  # default assumption
            
            logger.info(f"Interactive voice synthesis completed in {total_time:.2f}s")
            
            # Create URL path for the audio file
            url_path = f"/results/{filename}"
            
            return SynthesisResponse(
                audio_data=audio_base64,
                generation_time=generation_time,
                total_time=total_time,
                parameters_used={
                    "language": language,
                    "gender": gender,
                    "group": group,
                    "area_or_accent": area_or_accent,
                    "emotion": emotion,
                    "speed": speed,
                    "random_seed": random_seed,
                    "chunking_enabled": enable_chunking,
                    "chunk_overlap": chunk_overlap,
                    "prosody_consistency": prosody_consistency
                },
                audio_size_bytes=audio_size,
                voice_cloning=False,
                audio_file_path=url_path,
                audio_filename=filename,
                chunking_used=chunking_used,
                chunk_count=chunk_count,
                processing_stats=analysis_data,
                performance_metrics={
                    "processing_time": total_time,
                    "generation_time": generation_time,
                    "audio_duration": len(audio_data) / 24000.0,  # Assuming 24kHz sample rate
                    "characters_per_second": len(text) / total_time if total_time > 0 else 0
                }
            )
                
        except Exception as e:
            logger.error(f"Interactive voice synthesis failed: {str(e)}")
            raise TTSError(f"Interactive voice synthesis failed: {str(e)}")
    
    def synthesize_voice_cloning(
        self,
        text: str,
        language: str = "vietnamese",
        use_default_sample: bool = True,
        default_sample_id: str = "sample1",
        reference_text: Optional[str] = None,
        reference_audio_base64: Optional[str] = None,
        speed: float = 1.0,
        random_seed: int = 9527,
        enable_chunking: bool = True,
        chunk_overlap: int = 50,
        voice_consistency: float = 1.0,
        progress_callback: Optional[callable] = None
    ) -> SynthesisResponse:
        """Synthesize speech with voice cloning and long text support"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            start_time = time.time()
            
            # Input validation
            text = text.strip()
            if not text:
                raise ValidationError("Text cannot be empty")
            
            if len(text) > Constants.MAX_VOICE_CLONING_TEXT_LENGTH:
                raise ValidationError(f"Text too long for voice cloning. Maximum {Constants.MAX_VOICE_CLONING_TEXT_LENGTH} characters.")
            
            logger.info(f"Starting voice cloning synthesis for {len(text)} characters")
            
            # Validate reference inputs
            if not use_default_sample:
                if not reference_text:
                    raise ValidationError("Reference text is required when not using default sample")
                
                reference_text = reference_text.strip()
                if not reference_text:
                    raise ValidationError("Reference text cannot be empty")
                
                if len(reference_text) > Constants.MAX_REFERENCE_TEXT_LENGTH:
                    raise ValidationError(f"Reference text too long. Maximum {Constants.MAX_REFERENCE_TEXT_LENGTH} characters.")
                
                if not reference_audio_base64:
                    raise ValidationError("Reference audio is required when not using default sample")
            
            # Analyze text for processing strategy
            analysis_data = self.analyze_text_for_processing(text)
            
            # Generate output filename
            filename = self._generate_output_filename("voice_cloning")
            output_path = self._get_output_path(filename)
            
            # Update config
            synthesis_config = ModelConfig(
                language=language,
                speed=speed,
                random_seed=random_seed
            )
            
            # Prepare reference audio
            reference_audio_path = None
            if not use_default_sample:
                reference_audio_path = self._prepare_reference_audio(reference_audio_base64)
            
            try:
                # Choose synthesis method based on text length
                if analysis_data["requires_chunking"] and enable_chunking:
                    # Use long text synthesis with voice cloning
                    audio_data, generation_time = self._synthesize_long_text_cloning(
                        text, output_path, synthesis_config,
                        use_default_sample=use_default_sample,
                        default_sample_id=default_sample_id,
                        reference_audio_path=reference_audio_path,
                        reference_text=reference_text,
                        chunk_overlap=chunk_overlap,
                        voice_consistency=voice_consistency,
                        progress_callback=progress_callback
                    )
                    chunking_used = True
                    chunk_count = analysis_data["chunk_count"]
                else:
                    # Use standard synthesis
                    with TTSEngine(synthesis_config) as engine:
                        if use_default_sample:
                            if language == "english":
                                # For English, simply select voice by voice_id, no complex filtering
                                sample_audio_path, sample_text = engine.model_session_manager.select_sample(
                                    voice_id=default_sample_id
                                )
                            else:
                                # Vietnamese - use default selection
                                sample_audio_path, sample_text = engine.model_session_manager.select_sample()
                            
                            audio_data, generation_time = engine.synthesize(
                                text=text,
                                reference_audio=sample_audio_path,
                                reference_text=sample_text,
                                output_path=output_path
                            )
                        else:
                            audio_data, generation_time = engine.synthesize(
                                text=text,
                                reference_audio=reference_audio_path,
                                reference_text=reference_text,
                                output_path=output_path
                            )
                    chunking_used = False
                    chunk_count = 1
                
            finally:
                # Clean up temporary reference audio file
                if reference_audio_path and not use_default_sample:
                    try:
                        os.unlink(reference_audio_path)
                    except:
                        pass
            
            total_time = time.time() - start_time
            
            # Convert audio to base64
            audio_base64 = self._audio_to_base64(audio_data)
            
            # Calculate audio size - handle both bytes and numpy arrays
            if isinstance(audio_data, bytes):
                audio_size = len(audio_data)
            elif hasattr(audio_data, 'dtype'):
                # numpy array - calculate based on dtype
                if audio_data.dtype == np.int16:
                    audio_size = len(audio_data) * 2  # int16 = 2 bytes per sample
                elif audio_data.dtype == np.float32:
                    audio_size = len(audio_data) * 4  # float32 = 4 bytes per sample
                else:
                    audio_size = audio_data.nbytes  # fallback to total bytes
            else:
                audio_size = len(audio_data) * 2  # default assumption
            
            logger.info(f"Voice cloning synthesis completed in {total_time:.2f}s")
            
            # Create a URL path instead of the full file system path
            url_path = f"/results/{filename}"
            
            return SynthesisResponse(
                audio_data=audio_base64,
                generation_time=generation_time,
                total_time=total_time,
                parameters_used={
                    "text_length": len(text),
                    "use_default_sample": use_default_sample,
                    "default_sample_id": default_sample_id if use_default_sample else None,
                    "reference_text_length": len(reference_text) if reference_text else 0,
                    "speed": speed,
                    "random_seed": random_seed,
                    "chunking_enabled": enable_chunking,
                    "chunk_overlap": chunk_overlap,
                    "voice_consistency": voice_consistency
                },
                audio_size_bytes=audio_size,
                voice_cloning=True,
                audio_file_path=url_path,
                audio_filename=filename,
                chunking_used=chunking_used,
                chunk_count=chunk_count,
                processing_stats=analysis_data,
                performance_metrics={
                    "processing_time": total_time,
                    "generation_time": generation_time,
                    "audio_duration": len(audio_data) / 24000.0,
                    "characters_per_second": len(text) / total_time if total_time > 0 else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Voice cloning synthesis failed: {str(e)}")
            raise TTSError(f"Voice cloning synthesis failed: {str(e)}")
    
    def _synthesize_long_text(self, text: str, output_path: str, config: ModelConfig,
                            gender: str = "female", group: str = "story", 
                            area: str = "northern", emotion: str = "neutral",
                            chunk_overlap: int = 50, prosody_consistency: float = 1.0,
                            progress_callback: Optional[callable] = None) -> Tuple[bytes, float]:
        """Synthesize long text using advanced chunking"""
        
        with TTSEngine(config) as engine:
            audio_data, generation_time = engine.synthesize_long_text_optimized(
                text=text,
                gender=gender,
                group=group,
                area=area,
                emotion=emotion,
                output_path=output_path,
                progress_callback=progress_callback
            )
        
        return audio_data.tobytes(), generation_time
    
    def _synthesize_long_text_cloning(self, text: str, output_path: str, config: ModelConfig,
                                    use_default_sample: bool = True,
                                    default_sample_id: str = "sample1",
                                    reference_audio_path: Optional[str] = None,
                                    reference_text: Optional[str] = None,
                                    chunk_overlap: int = 50,
                                    voice_consistency: float = 1.0,
                                    progress_callback: Optional[callable] = None) -> Tuple[bytes, float]:
        """Synthesize long text with voice cloning"""
        
        with TTSEngine(config) as engine:
            if use_default_sample:
                # Get sample from model session manager
                if config.language == "english":
                    # For English, use voice_id directly
                    sample_audio_path, sample_text = engine.model_session_manager.select_sample(
                        voice_id=default_sample_id
                    )
                else:
                    # Vietnamese - use default selection
                    sample_audio_path, sample_text = engine.model_session_manager.select_sample()
                    
                audio_data, generation_time = engine.synthesize_long_text_optimized(
                    text=text,
                    reference_audio=sample_audio_path,
                    reference_text=sample_text,
                    output_path=output_path,
                    progress_callback=progress_callback
                )
            else:
                audio_data, generation_time = engine.synthesize_long_text_optimized(
                    text=text,
                    reference_audio=reference_audio_path,
                    reference_text=reference_text,
                    output_path=output_path,
                    progress_callback=progress_callback
                )
        
        return audio_data.tobytes(), generation_time

    def get_voice_options(self) -> Dict[str, Any]:
        """Get available voice options with multilingual support"""
        from ..core.model_config import MODEL_LANGUAGES, MODEL_ENGLISH_ACCENTS
        
        return {
            "voice_options": {
                "language": {
                    "options": MODEL_LANGUAGES,
                    "description": "Language selection",
                    "default": "vietnamese"
                },
                "gender": {
                    "options": MODEL_GENDER,
                    "description": "Voice gender",
                    "default": "female"
                },
                "group": {
                    "options": MODEL_GROUP,
                    "description": "Voice style/group",
                    "default": "story"
                },
                "area_or_accent": {
                    "vietnamese_areas": MODEL_AREA,
                    "english_accents": MODEL_ENGLISH_ACCENTS,
                    "description": "Voice accent/area (dynamic based on language)",
                    "default": "northern"
                },
                "emotion": {
                    "options": MODEL_EMOTION,
                    "description": "Voice emotion",
                    "default": "neutral"
                }
            },
            "advanced_options": {
                "speed": {
                    "min": 0.5,
                    "max": 2.0,
                    "default": 1.0,
                    "description": "Speech speed multiplier"
                },
                "random_seed": {
                    "min": 1,
                    "max": 99999,
                    "default": 9527,
                    "description": "Random seed for consistency"
                }
            },
            "supported_languages": MODEL_LANGUAGES
        }
    
    def get_reference_samples(self) -> Dict[str, Any]:
        """Get available default reference samples for voice cloning"""
        try:
            samples = []
            for sample_id, sample_data in Constants.DEFAULT_SAMPLES.items():
                sample = ReferenceSample(
                    id=sample_data["id"],
                    name=sample_data["name"],
                    description=sample_data["description"],
                    audio_path=sample_data["audio_path"],
                    text=sample_data["text"]
                )
                samples.append(sample.to_dict())
            
            return {
                "reference_samples": samples,
                "total_count": len(samples),
                "upload_info": {
                    "max_file_size": "16MB",
                    "supported_formats": Constants.SUPPORTED_FORMATS,
                    "recommended_duration": "5-30 seconds",
                    "recommended_quality": "High quality, no noise"
                }
            }
        except Exception as e:
            raise TTSError(f"Failed to get reference samples: {str(e)}")
    
    def _prepare_reference_audio(self, reference_audio_base64: str) -> str:
        """Convert base64 audio to file for processing"""
        logger = logging.getLogger(__name__)
        
        try:
            # Decode the base64 audio data
            audio_data = base64.b64decode(reference_audio_base64)
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            logger.info(f"Reference audio saved to temporary file: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to prepare reference audio: {str(e)}")
            raise TTSError(f"Failed to process reference audio: {str(e)}")
    
    def _audio_to_base64(self, audio_data) -> str:
        """Convert audio data to base64 encoding"""
        logger = logging.getLogger(__name__)
        try:
            # Handle numpy array
            if hasattr(audio_data, 'dtype'):
                # Convert numpy array to WAV bytes in memory
                import io
                import soundfile as sf
                
                # Ensure audio is 1D and float32
                if len(audio_data.shape) > 1:
                    audio_data = audio_data.reshape(-1)
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                # Create in-memory WAV file
                buffer = io.BytesIO()
                sf.write(buffer, audio_data, 24000, format='WAV')
                audio_bytes = buffer.getvalue()
                
                return base64.b64encode(audio_bytes).decode('utf-8')
            else:
                # Handle bytes directly
                return base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to convert audio to base64: {str(e)}")
            raise TTSError(f"Failed to encode audio: {str(e)}")
    
    def _create_progress_callback(self, enable_progress: bool = True):
        """Create a progress callback function for tracking processing"""
        if not enable_progress:
            return None
            
        def progress_callback(update: Dict[str, Any]):
            """Handle progress updates"""
            stage = update.get('stage', 'unknown')
            progress = update.get('progress', 0)
            message = update.get('message', '')
            
            print(f"[{stage.upper()}] {progress:.1f}% - {message}")
            
            # Handle errors
            if 'errors' in update and update['errors']:
                print(f"⚠️  Processing errors: {update['errors']}")
            
            # Handle chunk info
            if 'chunk_info' in update:
                chunk_info = update['chunk_info']
                print(f"   └─ Chunk {chunk_info.get('index', 0)+1}: {chunk_info.get('text_preview', '')}")
        
        return progress_callback
    
    def _validate_text_input(self, text: str, max_length: int, context: str = "text") -> str:
        """Enhanced text validation with detailed error messages"""
        # Basic validation
        if not text:
            raise ValidationError(f"{context.capitalize()} cannot be empty")
        
        text = text.strip()
        if not text:
            raise ValidationError(f"{context.capitalize()} cannot be empty after trimming")
        
        # Length validation
        if len(text) > max_length:
            raise ValidationError(
                f"{context.capitalize()} too long. Maximum {max_length:,} characters. "
                f"Current length: {len(text):,} characters."
            )
        
        return text
    
    def _handle_processing_error(self, error: Exception, context: str = "processing") -> str:
        """Enhanced error handling with user-friendly messages"""
        error_msg = str(error)
        
        # ONNX Runtime errors
        if "ONNXRuntimeError" in error_msg or "cannot broadcast" in error_msg:
            return (
                f"Model processing error during {context}. This usually happens when "
                "the text and reference audio are incompatible in length or content. "
                "Try using shorter text or a different reference audio."
            )
        
        # Memory errors
        if "memory" in error_msg.lower() or "allocation" in error_msg.lower():
            return (
                f"Insufficient memory during {context}. Try processing shorter text "
                "or enable chunking for long text."
            )
        
        # Tensor shape errors
        if "shape" in error_msg.lower() or "dimension" in error_msg.lower():
            return (
                f"Model input shape error during {context}. This typically occurs "
                "with very long text. Enable chunking or use shorter text."
            )
        
        # File I/O errors
        if "file" in error_msg.lower() or "path" in error_msg.lower():
            return f"File processing error during {context}: {error_msg}"
        
        # Default error
        return f"Processing error during {context}: {error_msg}"

    def _estimate_processing_time(self, text: str, enable_chunking: bool = True) -> float:
        """Estimate processing time for user feedback"""
        try:
            analysis = self.analyze_text_for_processing(text)
            base_time = analysis.get('estimated_processing_time', 10.0)
            
            # Add safety margin
            estimated_time = base_time * 1.2
            
            # Cap estimates for very long text
            max_reasonable_time = 300  # 5 minutes
            return min(estimated_time, max_reasonable_time)
            
        except Exception:
            # Fallback estimation
            chars_per_second = 50
            return len(text) / chars_per_second * 1.5
    
    def cleanup(self):
        """Cleanup resources"""
        if self._tts_engine:
            self._tts_engine.cleanup()
            self._tts_engine = None
    
    # Async processing methods
    async def submit_async_job(
        self, 
        job_type: str, 
        request_data: Dict[str, Any], 
        priority = None
    ) -> Dict[str, Any]:
        """Submit an async TTS processing job"""
        from ..core.request_queue import get_queue_manager, JobPriority
        from .schemas import AsyncJobResponse
        
        try:
            # Get queue manager
            queue_manager = get_queue_manager()
            
            # Create job
            job = await queue_manager.create_job(
                job_type=job_type,
                request_data=request_data,
                priority=priority or JobPriority.NORMAL
            )
            
            # Estimate completion time
            text = request_data.get('text', '')
            estimated_time = self._estimate_processing_time(text)
            
            # Get queue position
            queue_position = await queue_manager.get_queue_position(job.job_id)
            
            return AsyncJobResponse(
                job_id=job.job_id,
                status=job.status.value,
                message=f"Job submitted successfully for {job_type}",
                estimated_completion_time=estimated_time,
                queue_position=queue_position
            )
            
        except Exception as e:
            raise TTSError(f"Failed to submit async job: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of an async job"""
        from ..core.request_queue import get_queue_manager
        from .schemas import JobStatusResponse
        
        try:
            queue_manager = get_queue_manager()
            job = await queue_manager.get_job(job_id)
            
            if not job:
                raise ValidationError(f"Job {job_id} not found")
            
            return JobStatusResponse(
                job_id=job.job_id,
                status=job.status.value,
                progress=job.progress.__dict__ if job.progress else {},
                result=job.result.__dict__ if job.result else None,
                error=job.result.error_message if job.result and not job.result.success else None,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                estimated_remaining_time=job.estimated_remaining_time
            )
            
        except Exception as e:
            raise TTSError(f"Failed to get job status: {str(e)}")
    
    async def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel an async job"""
        from ..core.request_queue import get_queue_manager
        
        try:
            queue_manager = get_queue_manager()
            result = await queue_manager.cancel_job(job_id)
            return {"cancelled": result, "job_id": job_id}
            
        except Exception as e:
            raise TTSError(f"Failed to cancel job: {str(e)}")

    def _synthesize_with_cached_model(self, text: str, output_path: str, 
                                    model_session_manager, config: ModelConfig,
                                    gender: str = "female", group: str = "story", 
                                    area: Optional[str] = None, emotion: str = "neutral") -> Tuple[bytes, float]:
        """Synthesize text using cached model to avoid reloading"""
        start_time = time.time()
        
        try:
            if config.language == "english":
                # Use English TTS engine with cached model
                from ..core.english_tts_engine import EnglishTTSEngine
                engine = EnglishTTSEngine(config)
                engine.model_session_manager = model_session_manager
                
                # English synthesis
                audio_data, sample_rate = engine.synthesize(
                    text=text,
                    voice_id=gender,  # Use gender as voice_id for English
                    speed=config.speed,
                    seed=config.random_seed
                )
            else:
                # Vietnamese synthesis - use TTSEngine properly
                from ..core.tts_engine import TTSEngine
                
                # Create TTS engine with cached model session manager
                engine = TTSEngine(config)
                engine.model_session_manager = model_session_manager
                
                # Synthesize using TTS engine
                audio_data, generation_time = engine.synthesize(
                    text=text,
                    gender=gender,
                    group=group,
                    area=area,
                    emotion=emotion,
                    output_path=output_path
                )
            
            generation_time = time.time() - start_time
            
            # Convert to bytes if needed
            if isinstance(audio_data, np.ndarray):
                audio_bytes = audio_data.tobytes()
            else:
                audio_bytes = audio_data
                
            return audio_bytes, generation_time
            
        except Exception as e:
            raise TTSError(f"Synthesis with cached model failed: {str(e)}")
    
    def _synthesize_long_text_cached(self, text: str, output_path: str, config: ModelConfig,
                                   gender: str = "female", group: str = "story", 
                                   area: Optional[str] = None, emotion: str = "neutral",
                                   chunk_overlap: int = 50, prosody_consistency: float = 1.0,
                                   progress_callback: Optional[callable] = None) -> Tuple[bytes, float]:
        """Synthesize long text using cached model and optimized chunking"""
        start_time = time.time()
        
        try:
            # Get cached model
            model_session_manager = self.model_cache.get_model(config)
            
            # Use advanced text processor for chunking
            text_analysis = self.advanced_text_processor.analyze_text_structure(text)
            
            if not text_analysis.requires_chunking:
                # Use direct synthesis for short text
                return self._synthesize_with_cached_model(
                    text, output_path, model_session_manager, config,
                    gender, group, area, emotion
                )
            
            # Process in chunks for long text
            chunks = self.advanced_text_processor.chunk_text_advanced(text)
            audio_segments = []
            
            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks):
                if progress_callback:
                    progress_callback(f"Processing chunk {i+1}/{total_chunks}", (i+1)/total_chunks * 100)
                
                # Generate unique output path for this chunk
                chunk_output = output_path.replace('.wav', f'_chunk_{i}.wav')
                
                # Synthesize chunk
                chunk_audio, _ = self._synthesize_with_cached_model(
                    chunk.text, chunk_output, model_session_manager, config,
                    gender, group, area, emotion
                )
                
                audio_segments.append(chunk_audio)
            
            # Combine audio segments
            from ..core.audio_processor import AudioProcessor
            audio_processor = AudioProcessor()
            combined_audio = audio_processor.combine_audio_segments(
                audio_segments, 
                overlap_duration=chunk_overlap/1000.0,  # Convert ms to seconds
                sample_rate=config.sample_rate
            )
            
            # Save final audio
            audio_processor.save_audio(combined_audio, output_path, config.sample_rate)
            
            generation_time = time.time() - start_time
            
            # Read back as bytes
            if isinstance(combined_audio, np.ndarray):
                audio_bytes = combined_audio.tobytes()
            else:
                audio_bytes = combined_audio
                
            return audio_bytes, generation_time
            
        except Exception as e:
            raise TTSError(f"Long text synthesis with cached model failed: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache and performance statistics"""
        base_stats = self.model_cache.get_cache_stats()
        optimized_stats = self.optimized_manager.get_stats()
        performance_stats = self.performance_monitor.get_metrics()
        
        return {
            "model_cache": base_stats,
            "optimized_cache": optimized_stats,
            "performance": performance_stats,
            "system_status": {
                "warm_up_complete": optimized_stats.get("warm_up_complete", False),
                "total_models_ready": (
                    base_stats.get("total_entries", 0) + 
                    optimized_stats.get("total_cached_models", 0)
                )
            }
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear all caches and return cleanup results"""
        try:
            # Clear both caches
            self.model_cache.clear_cache()
            self.optimized_manager.clear_cache()
            
            # Reset engine
            self._tts_engine = None
            
            return {
                "success": True,
                "message": "All caches cleared successfully",
                "models_cleared": True,
                "optimized_cache_cleared": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clear some caches"
            }
