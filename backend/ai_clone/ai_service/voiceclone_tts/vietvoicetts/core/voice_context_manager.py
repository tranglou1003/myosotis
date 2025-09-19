"""
Voice Context System for maintaining consistency across chunks
"""

import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class VoiceContext:
    """Voice context information for maintaining consistency"""
    voice_embedding: Optional[Any] = None  # Voice characteristic embedding
    prosody_state: Dict[str, float] = None  # Prosody parameters
    speaker_id: str = ""  # Unique speaker identifier
    reference_audio_hash: str = ""  # Hash of reference audio
    reference_text: str = ""  # Reference text
    voice_characteristics: Dict[str, Any] = None  # Extracted voice features
    chunk_index: int = 0  # Current chunk index for context
    
    def __post_init__(self):
        if self.prosody_state is None:
            self.prosody_state = {
                'pitch_mean': 0.0,
                'pitch_std': 0.0,
                'energy_mean': 0.0,
                'energy_std': 0.0,
                'speaking_rate': 1.0,
                'pause_duration': 0.1
            }
        
        if self.voice_characteristics is None:
            self.voice_characteristics = {
                'timbre': 'neutral',
                'accent': 'northern',
                'age_group': 'adult',
                'emotion': 'neutral',
                'formality': 'normal'
            }


@dataclass
class ChunkVoiceState:
    """Voice state for a specific chunk"""
    chunk_index: int
    voice_context: VoiceContext
    transition_parameters: Dict[str, float]
    crossfade_config: Dict[str, Any]


class VoiceContextManager:
    """Manages voice context across chunks for consistency"""
    
    def __init__(self, cache_dir: str = "~/.cache/vietvoicetts/voice_contexts"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_context: Optional[VoiceContext] = None
        self.chunk_states: List[ChunkVoiceState] = []
        
    def create_voice_context(self, reference_audio_data: bytes, 
                           reference_text: str,
                           voice_params: Dict[str, Any] = None) -> VoiceContext:
        """Create or retrieve voice context from reference audio"""
        
        # Generate unique identifier for this voice
        audio_hash = hashlib.md5(reference_audio_data).hexdigest()
        text_hash = hashlib.md5(reference_text.encode('utf-8')).hexdigest()
        speaker_id = f"{audio_hash[:8]}_{text_hash[:8]}"
        
        # Check if we have cached context
        cached_context = self._load_cached_context(speaker_id)
        if cached_context:
            self.current_context = cached_context
            return cached_context
        
        # Extract voice characteristics from reference audio
        voice_characteristics = self._extract_voice_characteristics(
            reference_audio_data, reference_text, voice_params
        )
        
        # Create new context
        context = VoiceContext(
            speaker_id=speaker_id,
            reference_audio_hash=audio_hash,
            reference_text=reference_text,
            voice_characteristics=voice_characteristics
        )
        
        # Cache the context
        self._cache_voice_context(context)
        
        self.current_context = context
        return context
    
    def prepare_chunk_voice_state(self, chunk_index: int, 
                                chunk_text: str,
                                chunk_type: str,
                                prosody_type: str) -> ChunkVoiceState:
        """Prepare voice state for a specific chunk"""
        if not self.current_context:
            raise ValueError("No voice context available. Call create_voice_context first.")
        
        # Calculate transition parameters based on chunk characteristics
        transition_params = self._calculate_transition_parameters(
            chunk_index, chunk_text, chunk_type, prosody_type
        )
        
        # Configure crossfade for this chunk
        crossfade_config = self._configure_crossfade(
            chunk_index, chunk_type, prosody_type
        )
        
        # Create chunk-specific voice state
        chunk_state = ChunkVoiceState(
            chunk_index=chunk_index,
            voice_context=self._adapt_context_for_chunk(chunk_index, chunk_text, prosody_type),
            transition_parameters=transition_params,
            crossfade_config=crossfade_config
        )
        
        self.chunk_states.append(chunk_state)
        return chunk_state
    
    def get_voice_continuity_parameters(self, chunk_index: int) -> Dict[str, Any]:
        """Get parameters to maintain voice continuity"""
        if not self.current_context:
            return {}
        
        base_params = {
            'speaker_id': self.current_context.speaker_id,
            'voice_characteristics': self.current_context.voice_characteristics.copy(),
            'prosody_state': self.current_context.prosody_state.copy()
        }
        
        # Adjust parameters based on chunk position
        if chunk_index > 0:
            # Inherit some characteristics from previous chunk
            prev_state = self._get_previous_chunk_state(chunk_index)
            if prev_state:
                base_params['prosody_state'].update(prev_state.transition_parameters)
        
        return base_params
    
    def enhance_voice_continuity(self, chunk_states=None):
        """Enhance voice continuity between chunks by adjusting transition parameters
        
        This method should be called after all chunks have been processed but before synthesis
        to improve the overall voice consistency across chunks.
        """
        if not chunk_states:
            chunk_states = self.chunk_states
            
        if not chunk_states or len(chunk_states) <= 1:
            return
            
        # Calculate average prosody values across all chunks
        avg_prosody = {
            'pitch_mean': 0.0,
            'pitch_std': 0.0,
            'energy_mean': 0.0,
            'energy_std': 0.0,
            'speaking_rate': 0.0,
            'pause_duration': 0.0
        }
        
        # Gather and average values
        for state in chunk_states:
            for key in avg_prosody.keys():
                if key in state.voice_context.prosody_state:
                    avg_prosody[key] += state.voice_context.prosody_state[key]
        
        # Calculate averages
        for key in avg_prosody.keys():
            avg_prosody[key] /= len(chunk_states)
        
        # Apply smoothing - adjust each chunk's prosody state to be closer to the average
        smoothing_factor = 0.7  # How much to move toward the average (0.0 = no change, 1.0 = full average)
        for state in chunk_states:
            for key in avg_prosody.keys():
                if key in state.voice_context.prosody_state:
                    # Blend current value with average value
                    current = state.voice_context.prosody_state[key]
                    state.voice_context.prosody_state[key] = current * (1 - smoothing_factor) + avg_prosody[key] * smoothing_factor
                    
        return chunk_states
    
    def _extract_voice_characteristics(self, audio_data: bytes, 
                                     reference_text: str,
                                     voice_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract voice characteristics from reference audio"""
        # This is a simplified implementation
        # In a full implementation, this would use audio analysis
        
        characteristics = {
            'timbre': 'neutral',
            'accent': 'northern',
            'age_group': 'adult',
            'emotion': 'neutral',
            'formality': 'normal'
        }
        
        # Override with provided parameters
        if voice_params:
            characteristics.update(voice_params)
        
        # Simple text-based analysis for emotion/formality
        text_lower = reference_text.lower()
        
        # Detect formality
        formal_indicators = ['xin', 'kính', 'thưa', 'dạ', 'ạ']
        if any(indicator in text_lower for indicator in formal_indicators):
            characteristics['formality'] = 'formal'
        
        # Detect emotion from text (basic)
        if '!' in reference_text:
            characteristics['emotion'] = 'excited'
        elif '?' in reference_text:
            characteristics['emotion'] = 'questioning'
        
        return characteristics
    
    def _calculate_transition_parameters(self, chunk_index: int,
                                       chunk_text: str,
                                       chunk_type: str,
                                       prosody_type: str) -> Dict[str, float]:
        """Calculate transition parameters for smooth chunk connections"""
        base_params = {
            'pitch_continuity': 1.0,
            'energy_continuity': 1.0,
            'tempo_continuity': 1.0,
            'timbre_consistency': 1.0
        }
        
        # Adjust based on chunk type - increase continuity values for more consistent voice
        if chunk_type == 'dialogue':
            base_params['pitch_continuity'] = 0.95  # Reduced variation for more consistency
            base_params['energy_continuity'] = 0.97
        elif chunk_type == 'enumeration':
            base_params['tempo_continuity'] = 0.97  # More consistent tempo
        elif chunk_type == 'transition':
            base_params['pitch_continuity'] = 0.98  # Very smooth transitions
            base_params['energy_continuity'] = 0.98
        
        # Adjust based on prosody type - maintain higher consistency values
        if prosody_type == 'news':
            base_params['tempo_continuity'] = 1.05  # Slightly more consistent news pace
            base_params['timbre_consistency'] = 1.0
        elif prosody_type == 'dialogue':
            base_params['pitch_continuity'] = 0.95  # Less expressive, more consistent
        
        return base_params
    
    def _configure_crossfade(self, chunk_index: int,
                           chunk_type: str,
                           prosody_type: str) -> Dict[str, Any]:
        """Configure crossfade parameters for chunk transitions"""
        base_config = {
            'fade_in_duration': 0.05,
            'fade_out_duration': 0.05,
            'overlap_duration': 0.1,
            'curve_type': 'cosine',  # cosine, linear, exponential
            'volume_adjustment': 1.0
        }
        
        # Adjust for different chunk types - increase overlap and fade durations for smoother transitions
        if chunk_type == 'dialogue':
            base_config['fade_in_duration'] = 0.1
            base_config['fade_out_duration'] = 0.1
            base_config['curve_type'] = 'cosine'  # Smoother curve type
            base_config['overlap_duration'] = 0.15
        elif chunk_type == 'enumeration':
            base_config['fade_in_duration'] = 0.08
            base_config['fade_out_duration'] = 0.08
            base_config['overlap_duration'] = 0.12
        
        # Adjust for prosody types - standardize for consistency
        if prosody_type == 'news':
            base_config['curve_type'] = 'cosine'  # Consistent curve type
            base_config['overlap_duration'] = 0.12
        
        return base_config
    
    def _adapt_context_for_chunk(self, chunk_index: int,
                                chunk_text: str,
                                prosody_type: str) -> VoiceContext:
        """Adapt voice context for specific chunk characteristics"""
        if not self.current_context:
            raise ValueError("No current context available")
        
        # Create a copy of the current context
        adapted_context = VoiceContext(
            voice_embedding=self.current_context.voice_embedding,
            prosody_state=self.current_context.prosody_state.copy(),
            speaker_id=self.current_context.speaker_id,
            reference_audio_hash=self.current_context.reference_audio_hash,
            reference_text=self.current_context.reference_text,
            voice_characteristics=self.current_context.voice_characteristics.copy(),
            chunk_index=chunk_index
        )
        
        # Adapt prosody based on chunk characteristics with minimal changes
        # Reduce variation to maintain voice consistency between chunks
        if prosody_type == 'enumeration':
            adapted_context.prosody_state['speaking_rate'] *= 0.98
            adapted_context.prosody_state['pause_duration'] *= 1.05
        elif prosody_type == 'dialogue':
            adapted_context.prosody_state['pitch_std'] *= 1.03
            adapted_context.prosody_state['energy_std'] *= 1.03
        elif prosody_type == 'news':
            adapted_context.prosody_state['speaking_rate'] *= 1.02
            adapted_context.prosody_state['pause_duration'] *= 0.95
        
        return adapted_context
    
    def _get_previous_chunk_state(self, chunk_index: int) -> Optional[ChunkVoiceState]:
        """Get the voice state of the previous chunk"""
        for state in self.chunk_states:
            if state.chunk_index == chunk_index - 1:
                return state
        return None
    
    def _load_cached_context(self, speaker_id: str) -> Optional[VoiceContext]:
        """Load cached voice context"""
        cache_file = self.cache_dir / f"{speaker_id}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return VoiceContext(
                speaker_id=data['speaker_id'],
                reference_audio_hash=data['reference_audio_hash'],
                reference_text=data['reference_text'],
                voice_characteristics=data['voice_characteristics'],
                prosody_state=data.get('prosody_state', {})
            )
        except Exception:
            return None
    
    def _cache_voice_context(self, context: VoiceContext):
        """Cache voice context for future use"""
        cache_file = self.cache_dir / f"{context.speaker_id}.json"
        
        try:
            # Convert to serializable format
            data = {
                'speaker_id': context.speaker_id,
                'reference_audio_hash': context.reference_audio_hash,
                'reference_text': context.reference_text,
                'voice_characteristics': context.voice_characteristics,
                'prosody_state': context.prosody_state
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Ignore cache errors
    
    def cleanup(self):
        """Clean up resources"""
        self.current_context = None
        self.chunk_states.clear()
    
    def get_chunk_continuity_score(self, chunk_index: int) -> float:
        """Get a score indicating how well this chunk maintains voice continuity"""
        if chunk_index == 0 or not self.chunk_states:
            return 1.0
        
        current_state = None
        previous_state = None
        
        for state in self.chunk_states:
            if state.chunk_index == chunk_index:
                current_state = state
            elif state.chunk_index == chunk_index - 1:
                previous_state = state
        
        if not current_state or not previous_state:
            return 0.5
        
        # Calculate continuity based on transition parameters
        continuity_factors = []
        
        for param, value in current_state.transition_parameters.items():
            continuity_factors.append(value)
        
        return sum(continuity_factors) / len(continuity_factors) if continuity_factors else 0.5
