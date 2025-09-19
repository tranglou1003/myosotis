"""
TTS Engine - Main speech synthesis engine with long text support
"""

import time
import numpy as np
import torch
import re
from typing import List, Tuple, Optional, Generator, Dict, Any
from tqdm import tqdm

from .model_config import ModelConfig
from .model import ModelSessionManager
from .text_processor import TextProcessor
from .audio_processor import AudioProcessor
from .advanced_text_processor import AdvancedTextProcessor, ChunkInfo
from .performance_optimizer import PerformanceOptimizer, ProcessingMonitor
from .voice_context_manager import VoiceContextManager, VoiceContext


class TTSEngine:
    """Main TTS engine for inference with long text support"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig(language="english")
        
        # Initialize English TTS engine if needed
        if self.config.language == "english":
            self._init_english_engine()
        else:
            self._init_vietnamese_engine()
    
    def _init_english_engine(self):
        """Initialize English TTS engine"""
        try:
            from .english_tts_engine import EnglishTTSEngine
            self.english_engine = EnglishTTSEngine(self.config)
            # Expose the model session manager from the English engine
            self.model_session_manager = self.english_engine.model_session_manager
            self.text_processor = None
            print("Initialized English TTS engine with F5-TTS")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize English TTS engine: {e}")
        
        # Initialize common components
        self.audio_processor = AudioProcessor()
        self.advanced_text_processor = AdvancedTextProcessor(
            max_chunk_duration=self.config.max_chunk_duration,
            sample_rate=self.config.sample_rate
        )
        self.performance_optimizer = PerformanceOptimizer()
        self.voice_context_manager = VoiceContextManager()
        self.sample_cache = {}
    
    def _init_vietnamese_engine(self):
        """Initialize Vietnamese TTS engine"""
        self.model_session_manager = ModelSessionManager(self.config)
        self.model_session_manager.load_models()
        
        if not self.model_session_manager.vocab_path:
            raise RuntimeError("Vocabulary file not found in model tar archive")
        
        self.text_processor = TextProcessor(self.model_session_manager.vocab_path)
        self.audio_processor = AudioProcessor()
        self.advanced_text_processor = AdvancedTextProcessor(
            max_chunk_duration=self.config.max_chunk_duration,
            sample_rate=self.config.sample_rate
        )
        self.performance_optimizer = PerformanceOptimizer()
        self.voice_context_manager = VoiceContextManager()
        self.sample_cache = {}
        self.english_engine = None
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'model_session_manager') and self.model_session_manager:
            self.model_session_manager.cleanup()
        if hasattr(self, 'voice_context_manager') and self.voice_context_manager:
            self.voice_context_manager.cleanup()
        if hasattr(self, 'english_engine') and self.english_engine:
            self.english_engine.cleanup()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def synthesize_long_text_optimized(self, text: str,
                                     gender: Optional[str] = None,
                                     group: Optional[str] = None,
                                     area: Optional[str] = None,
                                     emotion: Optional[str] = None,
                                     output_path: Optional[str] = None,
                                     reference_audio: Optional[str] = None,
                                     reference_text: Optional[str] = None,
                                     progress_callback: Optional[callable] = None) -> Tuple[np.ndarray, float]:
        """
        Synthesize long text with optimized chunking and voice consistency
        
        Args:
            text: Input text to synthesize
            gender, group, area, emotion: Voice parameters for interactive voice
            output_path: Optional output file path
            reference_audio: Path or bytes for voice cloning
            reference_text: Reference text for voice cloning
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (audio_array, processing_time)
        """
        start_time = time.time()
        
        # Handle English synthesis
        if self.config.language == "english":
            return self._synthesize_english(text, gender, group, area, emotion, 
                                          reference_audio, reference_text, output_path)
        
        # Vietnamese synthesis
        # Reset sample cache to ensure consistent sample selection across chunks
        self.model_session_manager.reset_sample_cache()
        
        try:
            # Analyze text and determine processing strategy
            analysis = self.advanced_text_processor.analyze_text_structure(text)
            performance_metrics = self.performance_optimizer.calculate_performance_metrics(text)
            
            print(f"Kết quả phân tích:")
            print(f"  - độ dài: {analysis.total_length} từ")
            print(f"  - Time ước tính: {analysis.estimated_speaking_time:.1f}s")
            print(f"  - Complexity: {analysis.language_complexity:.2f}")
            print(f"  - Chunking: {analysis.requires_chunking}")
            print(f"  - Optimal chunk size: {analysis.optimal_chunk_size}")
            print(f"  - Estimated processing time: {performance_metrics.estimated_processing_time:.1f}s")
            
            if progress_callback:
                progress_callback({"stage": "analysis", "progress": 10, "message": "Text analyzed"})
            
            # Determine processing mode
            if not analysis.requires_chunking:
                # Use standard synthesis for short text
                return self.synthesize(
                    text, gender, group, area, emotion, output_path, 
                    reference_audio, reference_text
                )
            
            # Use chunked synthesis for long text
            return self._synthesize_chunked_text(
                text, analysis, performance_metrics,
                gender, group, area, emotion, output_path,
                reference_audio, reference_text, progress_callback
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f" Error in long text synthesis: {str(e)}")
            raise e
    
    def _synthesize_chunked_text(self, text: str,
                               analysis,
                               performance_metrics,
                               gender: Optional[str] = None,
                               group: Optional[str] = None,
                               area: Optional[str] = None,
                               emotion: Optional[str] = None,
                               output_path: Optional[str] = None,
                               reference_audio: Optional[str] = None,
                               reference_text: Optional[str] = None,
                               progress_callback: Optional[callable] = None) -> Tuple[np.ndarray, float]:
        """Synthesize text using intelligent chunking with Reference-Length Matching Strategy"""
        start_time = time.time()
        
        # Check for Reference-Length Matching Strategy activation
        if reference_audio and reference_text:
            chunking_info = self._calculate_reference_based_chunking(reference_text, text)
            
            if chunking_info['needs_ref_chunking']:
                print(f"🎯 Activating Reference-Length Matching Strategy")
                print(f"   Ratio: {chunking_info['word_ratio']:.1f}x ≥ 2.0 threshold")
                
                # Use reference-based chunking
                voice_params = {
                    'gender': gender,
                    'group': group, 
                    'area': area,
                    'emotion': emotion
                }
                
                final_audio, processing_time = self._synthesize_with_reference_chunking(
                    text, reference_audio, reference_text, chunking_info, voice_params, progress_callback
                )
                
                # Save output if requested
                if output_path:
                    self.audio_processor.save_audio(final_audio, output_path, self.config.sample_rate)
                
                return final_audio, processing_time
            else:
                print(f"📊 Reference-Length Matching not activated (ratio: {chunking_info['word_ratio']:.1f}x < 2.0)")
                print(f"🔄 Falling back to smart chunking")
        
        # Fall back to standard smart chunking
        chunks = self.advanced_text_processor.smart_chunking(text)
        
        print(f" Đang xlý {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {len(chunk.text)} từ, type: {chunk.chunk_type}, prosody: {chunk.prosody_type}")
        
        if progress_callback:
            progress_callback({
                "stage": "chunking", 
                "progress": 20, 
                "message": f"Created {len(chunks)} chunks"
            })
        
        # Setup voice context for consistency
        voice_context = None
        if reference_audio and reference_text:
            print(f"🔊 Setting up voice context with reference audio: {reference_audio}")
            print(f"📝 Reference text: {reference_text[:100]}...")
            
            # Load reference audio
            try:
                if isinstance(reference_audio, str):
                    with open(reference_audio, 'rb') as f:
                        audio_data = f.read()
                    print(f"✅ Loaded reference audio file: {len(audio_data)} bytes")
                else:
                    audio_data = reference_audio
                    print(f"✅ Using provided reference audio data: {len(audio_data)} bytes")
                
                voice_context = self.voice_context_manager.create_voice_context(
                    audio_data, reference_text,
                    {"gender": gender, "group": group, "area": area, "emotion": emotion}
                )
                print(f"✅ Voice context created successfully for voice cloning")
            except Exception as e:
                print(f"❌ Failed to create voice context: {str(e)}")
                import traceback
                traceback.print_exc()
                voice_context = None
        else:
            print(f"⚠️  No reference audio provided - reference_audio: {reference_audio}, reference_text: {reference_text}")
            voice_context = None
        
        # Initialize processing monitor
        monitor = self.performance_optimizer.start_processing_monitor(len(chunks))
        
        # Process chunks
        generated_waves = []
        processing_errors = []
        
        for i, chunk_info in enumerate(chunks):
            try:
                monitor.start_chunk()
                
                if progress_callback:
                    progress_callback({
                        "stage": "synthesis",
                        "progress": 20 + (i / len(chunks)) * 70,
                        "message": f"Processing chunk {i+1}/{len(chunks)}",
                        "chunk_info": {
                            "index": i,
                            "text_preview": chunk_info.text[:50] + "..." if len(chunk_info.text) > 50 else chunk_info.text,
                            "type": chunk_info.chunk_type,
                            "prosody": chunk_info.prosody_type
                        }
                    })
                
                # Synthesize chunk with context
                chunk_audio = self._synthesize_chunk_with_context(
                    chunk_info, reference_audio, reference_text, voice_context,
                    gender, group, area, emotion
                )
                
                generated_waves.append(chunk_audio)
                monitor.finish_chunk(len(chunk_info.text))
                
                # Log progress
                stats = monitor.get_current_stats()
                print(f" Chunk {i+1}/{len(chunks)} completed in {stats.current_chunk_time:.1f}s "
                     f"(avg: {stats.average_chunk_time:.1f}s, remaining: {stats.estimated_remaining_time:.1f}s)")
                
            except Exception as e:
                error_msg = f"Error processing chunk {i+1}: {str(e)}"
                print(f" {error_msg}")
                processing_errors.append(error_msg)
                
                # Generate silence for failed chunk to maintain timing
                silence_duration = chunk_info.expected_duration
                silence_samples = int(silence_duration * self.config.sample_rate)
                silence = np.zeros(silence_samples, dtype=np.int16)
                generated_waves.append(silence)
        
        if progress_callback:
            progress_callback({
                "stage": "concatenation", 
                "progress": 90, 
                "message": "Concatenating audio chunks"
            })
        
        # Concatenate with prosody-aware crossfade
        final_audio = self._concatenate_with_prosody_aware_crossfade(
            generated_waves, chunks
        )
        
        # Save output if requested
        if output_path:
            self.audio_processor.save_audio(final_audio, output_path, self.config.sample_rate)
        
        processing_time = time.time() - start_time
        
        if progress_callback:
            progress_callback({
                "stage": "complete", 
                "progress": 100, 
                "message": f"Synthesis completed in {processing_time:.1f}s",
                "errors": processing_errors if processing_errors else None
            })
        
        print(f"🎉 Long text synthesis completed in {processing_time:.1f}s")
        if processing_errors:
            print(f"  {len(processing_errors)} chunks had errors")
        
        return final_audio, processing_time
    
    def _synthesize_chunk_with_context(self, chunk_info: ChunkInfo,
                                     reference_audio: Optional[str],
                                     reference_text: Optional[str],
                                     voice_context: Optional[VoiceContext],
                                     gender: Optional[str] = None,
                                     group: Optional[str] = None,
                                     area: Optional[str] = None,
                                     emotion: Optional[str] = None) -> np.ndarray:
        """Synthesize a single chunk with voice context and memory management"""
        
        # Prepare chunk voice state
        chunk_voice_state = None
        continuity_params = {}
        
        if voice_context and self.voice_context_manager.current_context:
            try:
                chunk_voice_state = self.voice_context_manager.prepare_chunk_voice_state(
                    chunk_info.index, chunk_info.text, chunk_info.chunk_type, chunk_info.prosody_type
                )
                
                # Get voice continuity parameters
                continuity_params = self.voice_context_manager.get_voice_continuity_parameters(
                    chunk_info.index
                )
            except Exception as context_error:
                print(f"Warning: Failed to prepare chunk voice state: {str(context_error)}")
                chunk_voice_state = None
                continuity_params = {}
        else:
            # If no voice context available, create basic continuity parameters
            continuity_params = {
                'speaker_id': f'default_{gender}_{group}_{area}_{emotion}',
                'voice_characteristics': {
                    'gender': gender,
                    'group': group,
                    'area': area,
                    'emotion': emotion
                },
                'prosody_state': {
                    'pitch_mean': 1.0,
                    'energy_mean': 1.0,
                    'speaking_rate': 1.0
                }
            }
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Use standard synthesis with enhanced parameters
                chunk_audio, _ = self.synthesize(
                    chunk_info.text,
                    gender=gender,
                    group=group,
                    area=area,
                    emotion=emotion,
                    reference_audio=reference_audio,
                    reference_text=reference_text
                )
                
                # Apply voice context adjustments if available
                if chunk_voice_state:
                    chunk_audio = self._apply_voice_context(chunk_audio, chunk_voice_state)
                
                return chunk_audio
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a memory allocation error
                if ("allocation" in error_msg.lower() or 
                    "memory" in error_msg.lower() or 
                    "onnxruntimeerror" in error_msg.lower()):
                    
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Memory error on chunk {chunk_info.index + 1}, attempt {retry_count}/{max_retries}. Retrying with smaller text...")
                        
                        # Try with shorter text
                        shortened_text = self._shorten_text_for_retry(chunk_info.text, retry_count)
                        if shortened_text != chunk_info.text:
                            # Create a temporary chunk info with shortened text
                            temp_chunk_info = ChunkInfo(
                                text=shortened_text,
                                index=chunk_info.index,
                                chunk_type=chunk_info.chunk_type,
                                prosody_type=chunk_info.prosody_type,
                                semantic_weight=chunk_info.semantic_weight,
                                expected_duration=chunk_info.expected_duration * 0.7,  # Reduce expected duration
                                crossfade_duration=chunk_info.crossfade_duration
                            )
                            
                            try:
                                chunk_audio, _ = self.synthesize(
                                    temp_chunk_info.text,
                                    gender=gender,
                                    group=group,
                                    area=area,
                                    emotion=emotion,
                                    reference_audio=reference_audio,
                                    reference_text=reference_text
                                )
                                
                                if chunk_voice_state:
                                    chunk_audio = self._apply_voice_context(chunk_audio, chunk_voice_state)
                                
                                print(f" Successfully synthesized shortened chunk {chunk_info.index + 1}")
                                return chunk_audio
                                
                            except Exception as retry_error:
                                print(f"Retry {retry_count} also failed: {str(retry_error)}")
                                continue
                        else:
                            print(f"Cannot shorten text further for chunk {chunk_info.index + 1}")
                            break
                    else:
                        print(f" All retries failed for chunk {chunk_info.index + 1}")
                        break
                else:
                    # Non-memory error, don't retry
                    raise e
        
        # If all retries failed, generate silence as fallback
        print(f"🔇 Generating silence for failed chunk {chunk_info.index + 1}")
        silence_duration = max(chunk_info.expected_duration, 2.0)  # At least 2 seconds
        silence_samples = int(silence_duration * self.config.sample_rate)
        return np.zeros(silence_samples, dtype=np.int16)
    
    def _shorten_text_for_retry(self, text: str, retry_count: int) -> str:
        """Shorten text for retry attempts"""
        if retry_count == 1:
            # First retry: cut to 70% of original length
            words = text.split()
            target_length = int(len(words) * 0.7)
            if target_length > 5:
                shortened = " ".join(words[:target_length])
                if not shortened.endswith(('.', '!', '?')):
                    shortened += '.'
                return shortened
        elif retry_count == 2:
            # Second retry: cut to 50% of original length
            words = text.split()
            target_length = int(len(words) * 0.5)
            if target_length > 3:
                shortened = " ".join(words[:target_length])
                if not shortened.endswith(('.', '!', '?')):
                    shortened += '.'
                return shortened
        
        return text  # Return original if cannot shorten further
    
    def _apply_voice_context(self, audio: np.ndarray, 
                           chunk_voice_state) -> np.ndarray:
        """Apply voice context adjustments to maintain consistency"""
        
        # Apply transition parameters for voice consistency
        transition_params = chunk_voice_state.transition_parameters
        
        # Simple amplitude adjustment for energy continuity
        if 'energy_continuity' in transition_params:
            energy_factor = transition_params['energy_continuity']
            audio = audio * energy_factor
        
        # Ensure audio doesn't clip
        audio = self.audio_processor.fix_clipped_audio(audio)
        
        return audio
    
    def _concatenate_with_prosody_aware_crossfade(self, 
                                                generated_waves: List[np.ndarray],
                                                chunks: List[ChunkInfo]) -> np.ndarray:
        """Concatenate audio with prosody-aware crossfading"""
        
        if not generated_waves:
            return np.array([], dtype=np.int16)
        
        if len(generated_waves) == 1:
            return generated_waves[0].flatten()
        
        # Use enhanced crossfade from audio processor
        crossfade_durations = [chunk.crossfade_duration for chunk in chunks[1:]]
        
        # Calculate average crossfade duration
        avg_crossfade = np.mean(crossfade_durations) if crossfade_durations else 0.1
        
        return self.audio_processor.concatenate_with_crossfade_improved(
            generated_waves, avg_crossfade, self.config.sample_rate
        )

    def synthesize(self, text: str,
                   gender: Optional[str] = None,
                   group: Optional[str] = None,
                   area: Optional[str] = None,
                   emotion: Optional[str] = None,
                   output_path: Optional[str] = None,
                   reference_audio: Optional[str] = None,
                   reference_text: Optional[str] = None) -> Tuple[np.ndarray, float]:
        """
        Synthesize speech from text
        
        Args:
            text: Target text to synthesize
            reference_audio: Path to reference audio file (optional, uses default if not provided)
            reference_text: Text that was spoken in the reference audio (optional, helps with voice cloning quality)
            output_path: Path to save the generated audio (optional)
            
        Returns:
            Tuple of (generated_audio, generation_time)
        """
        start_time = time.time()
        
        # Handle English synthesis
        if self.config.language == "english":
            return self._synthesize_english(text, gender, group, area, emotion, 
                                          reference_audio, reference_text, output_path)
        
        # Vietnamese synthesis
        # Reset sample cache to ensure fresh sample selection for new synthesis
        if not hasattr(self, '_synthesis_in_progress'):
            self.model_session_manager.reset_sample_cache()
            self._synthesis_in_progress = True
        
        try:
            ref_audio, ref_text = self.model_session_manager.select_sample(gender, group, area, emotion, reference_audio, reference_text)
            inputs_list = self._prepare_inputs(ref_audio, ref_text, text)
            
            generated_waves = []
            for i, (audio, text_ids, max_duration, time_step) in enumerate(inputs_list):
                print(f"Generating speech for chunk {i+1}/{len(inputs_list)}...")
                
                preprocess_outputs = self._run_preprocess(audio, text_ids, max_duration)
                (noise, rope_cos_q, rope_sin_q, rope_cos_k, rope_sin_k, 
                 cat_mel_text, cat_mel_text_drop, ref_signal_len) = preprocess_outputs
                
                noise, time_step = self._run_transformer_steps(
                    noise, rope_cos_q, rope_sin_q, rope_cos_k, rope_sin_k,
                    cat_mel_text, cat_mel_text_drop, time_step
                )
                
                generated_signal = self._run_decode(noise, ref_signal_len)
                generated_waves.append(generated_signal)
            
            # Concatenate all generated waves with cross-fading
            if len(generated_waves) > 1:
                print(f"Concatenating {len(generated_waves)} chunks with improved cross-fade (duration: {self.config.cross_fade_duration}s)...")
            
            final_wave = self.audio_processor.concatenate_with_crossfade_improved(
                generated_waves, self.config.cross_fade_duration, self.config.sample_rate
            )
            
            generation_time = time.time() - start_time
            
            if output_path:
                self.audio_processor.save_audio(final_wave, output_path, self.config.sample_rate)
                print(f"Audio saved to: {output_path}")
            
            return final_wave, generation_time
            
        except Exception as e:
            raise RuntimeError(f"Speech synthesis failed: {str(e)}")
        finally:
            # Clear synthesis in progress flag
            if hasattr(self, '_synthesis_in_progress'):
                delattr(self, '_synthesis_in_progress')
    
    def _synthesize_english(self, text: str,
                           gender: Optional[str] = None,
                           group: Optional[str] = None,
                           area: Optional[str] = None,  # accent for English
                           emotion: Optional[str] = None,
                           reference_audio: Optional[str] = None,
                           reference_text: Optional[str] = None,
                           output_path: Optional[str] = None) -> Tuple[np.ndarray, float]:
        """
        Synthesize English speech using the English TTS engine
        """
        try:
            # Generate speech using English engine with correct interface
            audio_data, generation_time = self.english_engine.synthesize(
                text=text,
                reference_audio=reference_audio,
                reference_text=reference_text,
                output_path=output_path,
                gender=gender or "female"  # Default to female if not specified
            )
            
            return audio_data, generation_time
            
        except Exception as e:
            raise RuntimeError(f"English speech synthesis failed: {str(e)}")
    
    def validate_configuration(self, reference_audio: Optional[str] = None) -> bool:
        """Validate configuration with reference audio"""
        if reference_audio is None:
            # If no reference audio is provided, configuration is valid
            # since the model will use built-in samples
            print("✅ Configuration valid: Using built-in voice samples")
            return True
        else:
            # Validate with the provided reference audio
            return self.config.validate_with_reference_audio(reference_audio)
    
    def _prepare_inputs(self, reference_audio_path_or_bytes: str, reference_text: str, 
                       target_text: str) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """Prepare all inputs for inference, handling text chunking if needed"""
        audio = self.audio_processor.load_audio(reference_audio_path_or_bytes, self.config.sample_rate)
        audio = audio.reshape(1, 1, -1)

        # Clean text
        reference_text = self.text_processor.clean_text(reference_text)
        target_text = self.text_processor.clean_text(target_text)
        
        # Calculate reference audio duration and text length
        ref_text_len = self.text_processor.calculate_text_length(reference_text, self.config.pause_punctuation)
        ref_audio_len = audio.shape[-1] // self.config.hop_length + 1
        ref_audio_duration = audio.shape[-1] / self.config.sample_rate
        
        # Estimate speaking rate (characters per second)
        speaking_rate = ref_text_len / ref_audio_duration if ref_audio_duration > 0 else 100
        
        # Calculate total duration including reference audio
        target_text_len = self.text_processor.calculate_text_length(target_text, self.config.pause_punctuation)
        target_audio_duration = max(target_text_len / speaking_rate / self.config.speed, self.config.min_target_duration)
        total_estimated_duration = ref_audio_duration + target_audio_duration
        
        # Determine if chunking is needed
        # Dynamic max_chunk_duration based on reference audio length
        effective_max_chunk_duration = max(
            self.config.max_chunk_duration,
            ref_audio_duration + 15.0  # At least 15s for target text
        )
        
        if total_estimated_duration <= effective_max_chunk_duration:
            # Single chunk processing
            chunks = [target_text]
            print(f"Single chunk: total estimated duration {total_estimated_duration:.1f}s (ref: {ref_audio_duration:.1f}s + target: {target_audio_duration:.1f}s)")
        else:
            # Multiple chunks needed
            # Calculate available duration for target text per chunk (excluding reference audio)
            # Add a small safety margin to ensure chunks don't exceed the limit
            safety_margin = 1.0  # seconds
            min_target_duration_per_chunk = 10.0  # Increased from 1.0 to 10.0 for better quality
            available_target_duration = effective_max_chunk_duration - ref_audio_duration - safety_margin
            
            if available_target_duration < min_target_duration_per_chunk:
                # If reference audio is very long, use a much larger effective duration
                min_effective_duration = ref_audio_duration + min_target_duration_per_chunk + safety_margin
                effective_max_chunk_duration = min_effective_duration
                available_target_duration = min_target_duration_per_chunk
                print(f"⚠️  Reference audio ({ref_audio_duration:.1f}s) is very long. Using extended max_chunk_duration: {effective_max_chunk_duration:.1f}s")
            
            # Calculate max characters per chunk based on available duration
            # Use a more conservative approach for character calculation
            base_chars_per_chunk = int(speaking_rate * available_target_duration * self.config.speed)
            
            # Ensure minimum chunk size for quality
            min_chars_per_chunk = 200  # Minimum characters per chunk
            max_chars_per_chunk = max(base_chars_per_chunk, min_chars_per_chunk)
            
            print(f"Chunking with: available_target_duration={available_target_duration:.1f}s, max_chars_per_chunk={max_chars_per_chunk}")
            
            chunks = self.text_processor.chunk_text(target_text, max_chars=max_chars_per_chunk)
            
            # Post-process: verify each chunk meets duration requirements
            final_chunks = []
            for chunk in chunks:
                chunk_text_len = self.text_processor.calculate_text_length(chunk, self.config.pause_punctuation)
                chunk_target_duration = max(chunk_text_len / speaking_rate / self.config.speed, self.config.min_target_duration)
                chunk_total_duration = ref_audio_duration + chunk_target_duration
                
                if chunk_total_duration <= effective_max_chunk_duration:
                    final_chunks.append(chunk)
                else:
                    # Split this chunk further
                    print(f"Warning: Chunk too long ({chunk_total_duration:.1f}s), splitting further...")
                    # Calculate a smaller max_chars for this specific chunk
                    smaller_max_chars = int(len(chunk) * available_target_duration / chunk_target_duration * 0.9)  # 90% safety
                    sub_chunks = self.text_processor.chunk_text(chunk, max_chars=smaller_max_chars)
                    final_chunks.extend(sub_chunks)
            
            chunks = final_chunks
            print(f"Long text detected (total estimated {total_estimated_duration:.1f}s), split into {len(chunks)} chunks")
            print(f"Reference audio: {ref_audio_duration:.1f}s, available per chunk: {available_target_duration:.1f}s (using max_chunk_duration: {effective_max_chunk_duration:.1f}s)")
        
        # Prepare inputs for each chunk
        inputs_list = []
        for i, chunk in enumerate(chunks):
            chunk_text_len = self.text_processor.calculate_text_length(chunk, self.config.pause_punctuation)
            
            # Calculate target duration with minimum enforcement
            chunk_target_duration = max(chunk_text_len / speaking_rate / self.config.speed, self.config.min_target_duration)
            
            # Calculate chunk_audio_len based on the enforced target duration
            # Convert target duration to audio length units
            target_audio_samples = int(chunk_target_duration * self.config.sample_rate)
            target_audio_len = target_audio_samples // self.config.hop_length + 1
            chunk_audio_len = ref_audio_len + target_audio_len
            
            max_duration = np.array([chunk_audio_len], dtype=np.int64)
            
            combined_text = [list(reference_text + chunk)]
            text_ids = self.text_processor.text_to_indices(combined_text)
            time_step = np.array([0], dtype=np.int32)
            
            inputs_list.append((audio, text_ids, max_duration, time_step))
            
            # Calculate and display total duration for this chunk
            chunk_total_duration = ref_audio_duration + chunk_target_duration
            print(f"Chunk {i+1}/{len(chunks)}: {len(chunk)} chars, total duration {chunk_total_duration:.1f}s (ref: {ref_audio_duration:.1f}s + target: {chunk_target_duration:.1f}s). Content: {chunk}")
        
        return inputs_list
    
    def _run_preprocess(self, audio: np.ndarray, text_ids: np.ndarray, 
                       max_duration: np.ndarray) -> Tuple[np.ndarray, ...]:
        """Run preprocessing model"""
        session = self.model_session_manager.sessions['preprocess']
        input_names = self.model_session_manager.input_names['preprocess']
        output_names = self.model_session_manager.output_names['preprocess']
        
        inputs = {
            input_names[0]: audio,
            input_names[1]: text_ids,
            input_names[2]: max_duration
        }
        
        return session.run(output_names, inputs)
    
    def _run_transformer_steps(self, noise: np.ndarray, rope_cos_q: np.ndarray,
                              rope_sin_q: np.ndarray, rope_cos_k: np.ndarray,
                              rope_sin_k: np.ndarray, cat_mel_text: np.ndarray,
                              cat_mel_text_drop: np.ndarray, time_step: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Run transformer model iteratively"""
        session = self.model_session_manager.sessions['transformer']
        input_names = self.model_session_manager.input_names['transformer']
        output_names = self.model_session_manager.output_names['transformer']
        
        for i in tqdm(range(0, self.config.nfe_step - 1, self.config.fuse_nfe), 
                      desc="Processing", 
                      total=self.config.nfe_step // self.config.fuse_nfe - 1):
            
            inputs = {
                input_names[0]: noise,
                input_names[1]: rope_cos_q,
                input_names[2]: rope_sin_q,
                input_names[3]: rope_cos_k,
                input_names[4]: rope_sin_k,
                input_names[5]: cat_mel_text,
                input_names[6]: cat_mel_text_drop,
                input_names[7]: time_step
            }
            
            noise, time_step = session.run(output_names, inputs)
        
        return noise, time_step
    
    def _run_decode(self, noise: np.ndarray, ref_signal_len: np.ndarray) -> np.ndarray:
        """Run decode model to generate final audio"""
        session = self.model_session_manager.sessions['decode']
        input_names = self.model_session_manager.input_names['decode']
        output_names = self.model_session_manager.output_names['decode']
        
        inputs = {
            input_names[0]: noise,
            input_names[1]: ref_signal_len
        }
        
        return session.run(output_names, inputs)[0]
    
    def _calculate_reference_based_chunking(self, reference_text: str, target_text: str) -> Dict[str, Any]:
        """Calculate reference-based chunking metrics and decision"""
        # Clean and count words
        ref_words = len(reference_text.strip().split())
        target_words = len(target_text.strip().split())
        
        # Calculate ratio
        word_ratio = target_words / ref_words if ref_words > 0 else 0
        
        # Decision threshold: activate if target is at least 2x longer than reference
        needs_ref_chunking = word_ratio >= 2.0 and ref_words >= 10  # Minimum ref length check
        
        chunking_info = {
            'reference_word_count': ref_words,
            'target_word_count': target_words,
            'word_ratio': word_ratio,
            'needs_ref_chunking': needs_ref_chunking,
            'target_chunk_size': ref_words,
            'estimated_chunks': int(target_words / ref_words) if ref_words > 0 else 1
        }
        
        return chunking_info
    
    def _create_reference_sized_chunks(self, text: str, target_word_count: int) -> List[str]:
        """Create chunks with sizes matching reference text length with improved boundary detection"""
        words = text.strip().split()
        chunks = []
        
        # Allow ±20% flexibility but minimum 10 words
        min_chunk_size = max(int(target_word_count * 0.8), 10)
        max_chunk_size = int(target_word_count * 1.2)
        
        # Detect prosody break points for better chunking
        break_points = self.advanced_text_processor._detect_prosody_break_points(text)
        
        # Convert break points from character positions to word positions
        word_break_points = []
        current_pos = 0
        for i, word in enumerate(words):
            word_start = text.find(word, current_pos)
            word_end = word_start + len(word)
            
            # Check if any break points fall within this word's range
            for bp in break_points:
                if word_start <= bp <= word_end:
                    word_break_points.append(i + 1)  # Break after this word
                    break
            
            current_pos = word_end
        
        # Remove duplicates and sort
        word_break_points = sorted(list(set(word_break_points)))
        
        i = 0
        while i < len(words):
            # Start with target chunk size
            chunk_end = min(i + target_word_count, len(words))
            
            # If we're near the end, take all remaining words
            if len(words) - chunk_end < min_chunk_size:
                chunk_end = len(words)
            else:
                # First priority: find prosody break points within range
                best_break = None
                for bp in word_break_points:
                    if i + min_chunk_size <= bp <= i + max_chunk_size:
                        best_break = bp
                        break
                
                if best_break:
                    chunk_end = best_break
                else:
                    # Fallback: find sentence boundaries within flexibility range
                    for j in range(min(i + max_chunk_size, len(words)), 
                                  max(i + min_chunk_size, chunk_end - 1), -1):
                        if j < len(words) and words[j-1].endswith(('.', '!', '?', ':')):
                            chunk_end = j
                            break
            
            # Create chunk with boundary analysis
            chunk_words = words[i:chunk_end]
            chunk_text = " ".join(chunk_words)
            
            # Add metadata about chunk boundaries for better crossfading
            chunk_text = self._annotate_chunk_boundaries(chunk_text, i == 0, chunk_end >= len(words))
            chunks.append(chunk_text)
            
            i = chunk_end
        
        # Merge very short final chunk if needed
        if len(chunks) > 1 and len(chunks[-1].split()) < min_chunk_size // 2:
            last_chunk = chunks.pop()
            chunks[-1] = chunks[-1] + " " + last_chunk
        
        return chunks

    def _annotate_chunk_boundaries(self, chunk_text: str, is_first: bool, is_last: bool) -> str:
        """Add metadata annotations to chunk for better processing (invisible to TTS)"""
        # This metadata will be stripped before synthesis but helps with crossfade decisions
        annotations = []
        
        if is_first:
            annotations.append("[CHUNK_START]")
        if is_last:
            annotations.append("[CHUNK_END]")
        
        # Check sentence boundaries
        if chunk_text.strip().endswith(('.', '!', '?')):
            annotations.append("[SENTENCE_END]")
        if chunk_text.strip() and chunk_text.strip()[0].isupper():
            annotations.append("[SENTENCE_START]")
        
        # Store annotations in chunk (will be removed before synthesis)
        if annotations:
            return f"{''.join(annotations)} {chunk_text}"
        return chunk_text
    
    def _setup_voice_context(self, reference_audio: str, reference_text: str, 
                           voice_params: Dict[str, Any]) -> Optional[VoiceContext]:
        """Setup enhanced voice context for reference-based synthesis"""
        try:
            print(f"🎯 Setting up enhanced voice context...")
            
            # Load reference audio
            if isinstance(reference_audio, str):
                with open(reference_audio, 'rb') as f:
                    audio_data = f.read()
            else:
                audio_data = reference_audio
            
            # Create enhanced voice context
            voice_context = self.voice_context_manager.create_voice_context(
                audio_data, reference_text, voice_params
            )
            
            print(f"✅ Enhanced voice context created successfully")
            return voice_context
            
        except Exception as e:
            print(f"❌ Failed to create enhanced voice context: {str(e)}")
            return None
    
    def _extract_voice_consistency_params(self, voice_context: Optional[VoiceContext]) -> Dict[str, Any]:
        """Extract parameters for maintaining voice consistency across chunks"""
        if not voice_context:
            return {
                'base_volume': 1.0,
                'pitch_factor': 1.0,
                'energy_factor': 1.0,
                'speaking_rate': 1.0
            }
        
        # Extract consistency parameters from voice context
        try:
            consistency_params = {
                'base_volume': getattr(voice_context, 'base_volume', 1.0),
                'pitch_factor': getattr(voice_context, 'pitch_factor', 1.0),
                'energy_factor': getattr(voice_context, 'energy_factor', 1.0),
                'speaking_rate': getattr(voice_context, 'speaking_rate', 1.0),
                'voice_embedding': getattr(voice_context, 'voice_embedding', None)
            }
            return consistency_params
        except Exception as e:
            print(f"Warning: Failed to extract voice consistency params: {str(e)}")
            return {
                'base_volume': 1.0,
                'pitch_factor': 1.0,
                'energy_factor': 1.0,
                'speaking_rate': 1.0
            }
    
    def _synthesize_chunk_with_consistency(self, chunk_text: str, chunk_index: int,
                                         reference_audio: str, reference_text: str,
                                         consistency_params: Dict[str, Any],
                                         voice_params: Dict[str, Any]) -> np.ndarray:
        """Synthesize a chunk with enhanced voice consistency"""
        max_retries = 3
        retry_count = 0
        
        # Clean chunk text by removing boundary annotations
        clean_text = self._clean_chunk_annotations(chunk_text)
        
        while retry_count < max_retries:
            try:
                print(f"Synthesizing với chunk {chunk_index + 1} (attempt {retry_count + 1})")
                
                # Use same reference for all chunks - this is key for consistency
                chunk_audio, _ = self.synthesize(
                    clean_text,
                    gender=voice_params.get('gender'),
                    group=voice_params.get('group'),
                    area=voice_params.get('area'),
                    emotion=voice_params.get('emotion'),
                    reference_audio=reference_audio,  # Same reference for all chunks
                    reference_text=reference_text     # Same reference text for all chunks
                )
                
                # Apply voice consistency adjustments with boundary information
                chunk_audio = self._apply_voice_consistency(
                    chunk_audio, chunk_index, consistency_params, chunk_text
                )
                
                return chunk_audio
                
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"   ⚠️ Chunk {chunk_index + 1} failed (attempt {retry_count}), retrying...")
                    # Try with shorter text
                    clean_text = self._shorten_text_for_retry(clean_text, retry_count)
                else:
                    print(f"   ❌ Chunk {chunk_index + 1} failed after all retries")

    def _clean_chunk_annotations(self, chunk_text: str) -> str:
        """Remove boundary annotations from chunk text before synthesis"""
        import re
        
        # Remove all annotation markers
        clean_text = re.sub(r'\[CHUNK_START\]|\[CHUNK_END\]|\[SENTENCE_START\]|\[SENTENCE_END\]', '', chunk_text)
        
        # Clean up extra spaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text

    def _extract_chunk_boundary_info(self, chunk_text: str) -> Dict[str, bool]:
        """Extract boundary information from annotated chunk text"""
        return {
            'is_chunk_start': '[CHUNK_START]' in chunk_text,
            'is_chunk_end': '[CHUNK_END]' in chunk_text,
            'is_sentence_start': '[SENTENCE_START]' in chunk_text,
            'is_sentence_end': '[SENTENCE_END]' in chunk_text
        }
        
        # Generate silence as fallback
        print(f"   🔇 Generating silence fallback for chunk {chunk_index + 1}")
        silence_samples = int(3.0 * self.config.sample_rate)  # 3 seconds of silence
        return np.zeros(silence_samples, dtype=np.int16)
    
    def _apply_voice_consistency(self, audio: np.ndarray, chunk_index: int,
                               consistency_params: Dict[str, Any], 
                               chunk_text: str = "") -> np.ndarray:
        """Apply voice consistency adjustments with boundary awareness"""
        try:
            # Extract boundary information
            boundary_info = self._extract_chunk_boundary_info(chunk_text) if chunk_text else {}
            
            # Preserve original volume level - this is crucial for preventing volume drop
            base_volume = consistency_params.get('base_volume', 1.0)
            
            # For the first chunk, calculate and store the base volume
            if chunk_index == 0:
                rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
                if rms > 0:
                    consistency_params['calculated_base_volume'] = rms
            
            # Apply gentle volume normalization to maintain consistency without reducing quality
            calculated_base = consistency_params.get('calculated_base_volume', None)
            if calculated_base and chunk_index > 0:
                current_rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
                if current_rms > 0:
                    # Apply gentle volume adjustment (limit to ±15% for sentence boundaries)
                    volume_ratio = calculated_base / current_rms
                    
                    # Be more conservative at sentence boundaries to avoid artifacts
                    if boundary_info.get('is_sentence_start') or boundary_info.get('is_sentence_end'):
                        volume_ratio = np.clip(volume_ratio, 0.85, 1.15)  # More conservative
                    else:
                        volume_ratio = np.clip(volume_ratio, 0.8, 1.2)    # Standard adjustment
                    
                    audio = (audio.astype(np.float32) * volume_ratio).astype(np.int16)
            
            # Apply energy factor if available with boundary awareness
            energy_factor = consistency_params.get('energy_factor', 1.0)
            
            # Adjust energy factor based on boundary context
            if boundary_info.get('is_sentence_end'):
                energy_factor *= 0.98  # Slightly lower energy for sentence endings
            elif boundary_info.get('is_sentence_start'):
                energy_factor *= 1.02  # Slightly higher energy for sentence starts
            
            if 0.85 <= energy_factor <= 1.15:  # Only apply if factor is reasonable
                audio = (audio.astype(np.float32) * energy_factor).astype(np.int16)
            
            # Ensure no clipping
            audio = self.audio_processor.fix_clipped_audio(audio)
            
            return audio
            
        except Exception as e:
            print(f"Warning: Failed to apply voice consistency: {str(e)}")
            return audio
    
    def _concatenate_with_voice_consistency(self, generated_waves: List[np.ndarray]) -> np.ndarray:
        """Enhanced concatenation with intelligent crossfade to prevent "vấp" between chunks"""
        if not generated_waves:
            return np.array([], dtype=np.int16)
        
        if len(generated_waves) == 1:
            return generated_waves[0].flatten()
        
        # Use intelligent crossfade with adaptive duration and smart transitions
        return self._concatenate_with_intelligent_crossfade(
            generated_waves, self.config.sample_rate
        )
    
    def _concatenate_with_intelligent_crossfade(self, generated_waves: List[np.ndarray], 
                                               sample_rate: int) -> np.ndarray:
        """Advanced concatenation with intelligent crossfade to eliminate chunk transitions"""
        if not generated_waves:
            return np.array([], dtype=np.int16)
        
        if len(generated_waves) == 1:
            return generated_waves[0].reshape(-1)
        
        # Flatten all waves and analyze each chunk
        flattened_waves = [wave.reshape(-1) for wave in generated_waves]
        
        # Calculate reference volume from the first chunk 
        reference_rms = np.sqrt(np.mean(flattened_waves[0].astype(np.float32) ** 2))
        
        # Pre-process waves with volume normalization and silence trimming
        processed_waves = []
        for i, wave in enumerate(flattened_waves):
            # Trim silence from edges but preserve natural pauses
            trimmed_wave = self._smart_trim_silence(wave, sample_rate)
            
            # Gentle volume normalization
            current_rms = np.sqrt(np.mean(trimmed_wave.astype(np.float32) ** 2))
            if current_rms > 0 and reference_rms > 0:
                volume_ratio = reference_rms / current_rms
                volume_ratio = np.clip(volume_ratio, 0.90, 1.10)  # Very conservative
                
                if i > 0:  # Don't adjust the reference chunk
                    adjusted_wave = (trimmed_wave.astype(np.float32) * volume_ratio).astype(np.int16)
                    processed_waves.append(self.audio_processor.fix_clipped_audio(adjusted_wave))
                else:
                    processed_waves.append(trimmed_wave)
            else:
                processed_waves.append(trimmed_wave)
        
        # Apply intelligent crossfading between chunks
        final_wave = processed_waves[0]
        
        for i in range(1, len(processed_waves)):
            prev_wave = final_wave
            next_wave = processed_waves[i]
            
            # Analyze transition context for optimal crossfade
            transition_info = self._analyze_transition_context(prev_wave, next_wave, sample_rate)
            
            # Apply context-aware crossfade
            final_wave = self._apply_context_aware_crossfade(
                prev_wave, next_wave, transition_info, sample_rate
            )
        
        # Final enhancement to ensure smooth overall result
        final_wave = self._apply_final_smoothing(final_wave, sample_rate)
        
        return final_wave

    def _smart_trim_silence(self, audio: np.ndarray, sample_rate: int, 
                           threshold_ratio: float = 0.02) -> np.ndarray:
        """Smart silence trimming that preserves natural speech pauses"""
        if len(audio) == 0:
            return audio
        
        # Calculate dynamic threshold based on audio content
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        threshold = rms * threshold_ratio
        
        # Find speech regions
        window_size = int(0.02 * sample_rate)  # 20ms windows
        energy = []
        
        for i in range(0, len(audio), window_size):
            window = audio[i:i + window_size]
            if len(window) > 0:
                window_energy = np.sqrt(np.mean(window.astype(np.float32) ** 2))
                energy.append(window_energy)
        
        # Find start and end of speech with more conservative trimming
        start_idx = 0
        end_idx = len(audio)
        
        # Find speech start (allow some leading silence for natural rhythm)
        for i, e in enumerate(energy):
            if e > threshold:
                start_idx = max(0, i * window_size - int(0.05 * sample_rate))  # Keep 50ms before
                break
        
        # Find speech end (allow some trailing silence)
        for i in reversed(range(len(energy))):
            if energy[i] > threshold:
                end_idx = min(len(audio), (i + 1) * window_size + int(0.05 * sample_rate))  # Keep 50ms after
                break
        
        return audio[start_idx:end_idx]

    def _analyze_transition_context(self, prev_wave: np.ndarray, next_wave: np.ndarray, 
                                   sample_rate: int) -> Dict[str, Any]:
        """Analyze the transition context between two audio chunks"""
        
        # Analyze ending of previous chunk (last 200ms)
        prev_tail_samples = min(int(0.2 * sample_rate), len(prev_wave))
        prev_tail = prev_wave[-prev_tail_samples:] if prev_tail_samples > 0 else prev_wave
        
        # Analyze beginning of next chunk (first 200ms)  
        next_head_samples = min(int(0.2 * sample_rate), len(next_wave))
        next_head = next_wave[:next_head_samples] if next_head_samples > 0 else next_wave
        
        # Calculate energy characteristics
        prev_energy = np.sqrt(np.mean(prev_tail.astype(np.float32) ** 2))
        next_energy = np.sqrt(np.mean(next_head.astype(np.float32) ** 2))
        
        # Detect if ending/beginning are low energy (likely sentence end/start)
        energy_threshold = max(prev_energy, next_energy) * 0.3
        prev_is_quiet = prev_energy < energy_threshold
        next_is_quiet = next_energy < energy_threshold
        
        # Calculate spectral characteristics (simplified)
        prev_high_freq = np.mean(np.abs(prev_tail[-int(0.01 * sample_rate):]))  # Last 10ms
        next_high_freq = np.mean(np.abs(next_head[:int(0.01 * sample_rate)]))   # First 10ms
        
        # Determine optimal crossfade duration and type
        if prev_is_quiet and next_is_quiet:
            # Both chunks end/start quietly - shorter crossfade
            crossfade_duration = 0.08
            fade_type = 'linear'
        elif abs(prev_energy - next_energy) > max(prev_energy, next_energy) * 0.5:
            # Large energy difference - longer, smoother crossfade
            crossfade_duration = 0.20
            fade_type = 'smooth_cosine'
        else:
            # Normal case - standard crossfade  
            crossfade_duration = 0.12
            fade_type = 'cosine'
        
        return {
            'crossfade_duration': crossfade_duration,
            'fade_type': fade_type,
            'prev_energy': prev_energy,
            'next_energy': next_energy,
            'energy_ratio': next_energy / prev_energy if prev_energy > 0 else 1.0,
            'prev_is_quiet': prev_is_quiet,
            'next_is_quiet': next_is_quiet
        }

    def _apply_context_aware_crossfade(self, prev_wave: np.ndarray, next_wave: np.ndarray,
                                      transition_info: Dict[str, Any], sample_rate: int) -> np.ndarray:
        """Apply intelligent crossfade based on transition context"""
        
        crossfade_duration = transition_info['crossfade_duration']
        fade_type = transition_info['fade_type']
        energy_ratio = transition_info['energy_ratio']
        
        crossfade_samples = int(crossfade_duration * sample_rate)
        crossfade_samples = min(crossfade_samples, len(prev_wave), len(next_wave))
        
        if crossfade_samples <= 0:
            return np.concatenate([prev_wave, next_wave])
        
        # Get overlapping regions
        prev_overlap = prev_wave[-crossfade_samples:]
        next_overlap = next_wave[:crossfade_samples]
        
        # Generate fade curves based on context
        if fade_type == 'linear':
            fade_out = np.linspace(1.0, 0.0, crossfade_samples)
            fade_in = np.linspace(0.0, 1.0, crossfade_samples)
        elif fade_type == 'smooth_cosine':
            # Extra smooth curve for difficult transitions
            t = np.linspace(0, np.pi/2, crossfade_samples)
            fade_out = (np.cos(t) ** 3)  # Extra smooth
            fade_in = (np.sin(t) ** 3)   # Extra smooth
        else:  # cosine
            t = np.linspace(0, np.pi/2, crossfade_samples) 
            fade_out = np.cos(t) ** 2
            fade_in = np.sin(t) ** 2
        
        # Apply energy-aware volume adjustment
        if abs(energy_ratio - 1.0) > 0.2:  # Significant energy difference
            # Gradually adjust energy across the crossfade
            energy_adjustment = np.linspace(1.0, energy_ratio, crossfade_samples)
            next_overlap_adjusted = next_overlap.astype(np.float32) * energy_adjustment
        else:
            next_overlap_adjusted = next_overlap.astype(np.float32)
        
        # Normalize fades to preserve energy
        fade_sum = fade_out + fade_in
        fade_out = fade_out / (fade_sum + 1e-8)
        fade_in = fade_in / (fade_sum + 1e-8)
        
        # Apply crossfade
        cross_faded_overlap = (prev_overlap.astype(np.float32) * fade_out + 
                              next_overlap_adjusted * fade_in).astype(np.int16)
        
        # Combine the result
        final_wave = np.concatenate([
            prev_wave[:-crossfade_samples],
            cross_faded_overlap,
            next_wave[crossfade_samples:]
        ])
        
        return final_wave

    def _apply_final_smoothing(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply final smoothing to eliminate any remaining artifacts"""
        if len(audio) == 0:
            return audio
        
        # Light smoothing filter to remove any remaining discontinuities
        # Use a very short moving average (1ms) to smooth micro-discontinuities
        window_size = max(1, int(0.001 * sample_rate))
        
        if window_size > 1 and len(audio) > window_size:
            # Apply very light smoothing
            smoothed = np.convolve(audio.astype(np.float32), 
                                 np.ones(window_size) / window_size, 
                                 mode='same')
            
            # Blend with original (90% original, 10% smoothed)
            final_audio = (0.9 * audio.astype(np.float32) + 0.1 * smoothed).astype(np.int16)
            return self.audio_processor.fix_clipped_audio(final_audio)
        
        return audio

    def _concatenate_with_enhanced_volume_preservation(self, generated_waves: List[np.ndarray], 
                                                      crossfade_duration: float, 
                                                      sample_rate: int) -> np.ndarray:
        """Legacy method - now redirects to intelligent crossfade"""
        return self._concatenate_with_intelligent_crossfade(generated_waves, sample_rate)
    
    def _synthesize_with_reference_chunking(self, text: str, reference_audio: str, reference_text: str,
                                          chunking_info: Dict[str, Any], voice_params: Dict[str, Any],
                                          progress_callback: Optional[callable] = None) -> Tuple[np.ndarray, float]:
        """Main synthesis pipeline using Reference-Length Matching Strategy"""
        start_time = time.time()
        
        print(f"🎯 Reference-Length Matching Strategy activated!")
        print(f"   📊 Word ratio: {chunking_info['word_ratio']:.1f}x")
        print(f"   📦 Target chunks: ~{chunking_info['estimated_chunks']}")
        print(f"   📏 Target chunk size: ~{chunking_info['target_chunk_size']} words")
        
        # Create reference-sized chunks
        chunks = self._create_reference_sized_chunks(text, chunking_info['target_chunk_size'])
        
        print(f"📦 Created {len(chunks)} chunks:")
        total_words = 0
        for i, chunk in enumerate(chunks):
            word_count = len(chunk.split())
            total_words += word_count
            print(f"   Chunk {i+1}: {word_count} words - {chunk[:60]}...")
        
        efficiency = (total_words / chunking_info['target_word_count'] * 100) if chunking_info['target_word_count'] > 0 else 100
        print(f"📊 Chunking efficiency: {efficiency:.1f}% words preserved")
        
        if progress_callback:
            progress_callback({
                "stage": "ref_chunking",
                "progress": 25,
                "message": f"{len(chunks)} reference-sized chunks",
                "chunking_info": chunking_info
            })
        
        # Setup enhanced voice context
        voice_context = self._setup_voice_context(reference_audio, reference_text, voice_params)
        consistency_params = self._extract_voice_consistency_params(voice_context)
        
        # Synthesize chunks with consistency
        generated_waves = []
        processing_errors = []
        
        for i, chunk_text in enumerate(chunks):
            try:
                if progress_callback:
                    progress_callback({
                        "stage": "ref_synthesis",
                        "progress": 25 + (i / len(chunks)) * 65,
                        "message": f"Synthesizing chunk {i+1}/{len(chunks)}",
                        "chunk_info": {
                            "index": i,
                            "text_preview": chunk_text[:50] + "..." if len(chunk_text) > 50 else chunk_text,
                            "word_count": len(chunk_text.split())
                        }
                    })
                
                # Synthesize chunk with consistency - using SAME reference for all chunks
                chunk_audio = self._synthesize_chunk_with_consistency(
                    chunk_text, i, reference_audio, reference_text, 
                    consistency_params, voice_params
                )
                
                generated_waves.append(chunk_audio)
                print(f" Chunk {i+1}/{len(chunks)} đone ({len(chunk_text.split())} words)")
                
            except Exception as e:
                error_msg = f"Error in chunk {i+1}: {str(e)}"
                print(f"   ❌ {error_msg}")
                processing_errors.append(error_msg)
                
                # Generate silence fallback
                silence_samples = int(3.0 * self.config.sample_rate)
                generated_waves.append(np.zeros(silence_samples, dtype=np.int16))
        
        if progress_callback:
            progress_callback({
                "stage": "ref_concatenation",
                "progress": 90,
                "message": "Concatenating with voice consistency"
            })
        
        # Enhanced concatenation with voice consistency
        print(f" Có  {len(generated_waves)} chunks đẫ được ghép")
        final_audio = self._concatenate_with_voice_consistency(generated_waves)
        
        processing_time = time.time() - start_time
        
        success_rate = ((len(chunks) - len(processing_errors)) / len(chunks) * 100) if len(chunks) > 0 else 0
        
        print(f"Matching done")
        print(f"  Time xly: {processing_time:.1f}s")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Chunks processed: {len(chunks)}")
        print(f"  Chunks failed: {len(processing_errors)}")
        
        if progress_callback:
            progress_callback({
                "stage": "ref_complete",
                "progress": 100,
                "message": f"Reference-Length Matching completed in {processing_time:.1f}s",
                "stats": {
                    "chunks_processed": len(chunks),
                    "chunks_failed": len(processing_errors),
                    "success_rate": success_rate,
                    "processing_time": processing_time
                }
            })
        
        return final_audio, processing_time