"""
Advanced Text Processing for Long Text TTS
Handles semantic chunking, prosody analysis, and Vietnamese language specifics
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path


@dataclass
class ChunkInfo:
    """Information about a text chunk"""
    text: str
    index: int
    chunk_type: str  # 'normal', 'transition', 'enumeration', 'dialogue'
    prosody_type: str  # 'narrative', 'news', 'dialogue', 'enumeration'
    semantic_weight: float  # 0.0 to 1.0
    expected_duration: float  # in seconds
    context_before: str = ""
    context_after: str = ""
    crossfade_duration: float = 0.1
    voice_context: Optional[Dict] = None


@dataclass
class TextAnalysis:
    """Analysis of text structure and characteristics"""
    total_length: int
    estimated_speaking_time: float
    language_complexity: float
    prosody_patterns: List[str]
    transition_points: List[int]
    optimal_chunk_size: int
    requires_chunking: bool


class AdvancedTextProcessor:
    """Advanced text processor with semantic chunking and prosody analysis"""
    
    def __init__(self, max_chunk_duration: float = 45.0, sample_rate: int = 24000):
        self.max_chunk_duration = max_chunk_duration
        self.sample_rate = sample_rate
        
        # Vietnamese language patterns
        self.sentence_endings = r'[.!?]'
        self.pause_markers = r'[,;:]'
        self.transition_words = [
            'tuy nhiên', 'nhưng', 'mặt khác', 'bên cạnh đó', 'ngoài ra',
            'do đó', 'vì vậy', 'kết quả là', 'từ đó', 'theo đó',
            'đầu tiên', 'thứ hai', 'thứ ba', 'cuối cùng', 'sau cùng',
            'trước hết', 'tiếp theo', 'sau đó', 'bên cạnh đó'
        ]
        self.enumeration_markers = [
            'đầu tiên', 'thứ nhất', 'thứ hai', 'thứ ba', 'thứ tư', 'thứ năm',
            'một là', 'hai là', 'ba là', 'bốn là', 'năm là',
            'trước hết', 'tiếp theo', 'sau đó', 'cuối cùng'
        ]
        self.dialogue_markers = ['"', "'", '«', '»', '-', '–', '—']
        
        # Speaking rate estimation (chars per second)
        self.avg_speaking_rate = 12.0  # Vietnamese average
        self.optimal_chunk_chars = int(self.max_chunk_duration * self.avg_speaking_rate * 0.8)
        
    def analyze_text_structure(self, text: str) -> TextAnalysis:
        """Analyze text structure and characteristics"""
        clean_text = self._clean_text_for_analysis(text)
        text_length = len(clean_text)
        
        # Estimate speaking time
        estimated_time = self._estimate_speaking_time(clean_text)
        
        # Calculate language complexity
        complexity = self._calculate_language_complexity(clean_text)
        
        # Detect prosody patterns
        prosody_patterns = self._detect_prosody_patterns(clean_text)
        
        # Find transition points
        transition_points = self._find_transition_points(clean_text)
        
        # Determine optimal chunk size
        optimal_chunk_size = self._calculate_optimal_chunk_size(clean_text, complexity)
        
        # Check if chunking is required
        requires_chunking = estimated_time > self.max_chunk_duration or text_length > self.optimal_chunk_chars
        
        return TextAnalysis(
            total_length=text_length,
            estimated_speaking_time=estimated_time,
            language_complexity=complexity,
            prosody_patterns=prosody_patterns,
            transition_points=transition_points,
            optimal_chunk_size=optimal_chunk_size,
            requires_chunking=requires_chunking
        )
    
    def smart_chunking(self, text: str, speaking_rate: float = None) -> List[ChunkInfo]:
        """Perform semantic-aware chunking of text"""
        if speaking_rate is None:
            speaking_rate = self.avg_speaking_rate
            
        clean_text = self._clean_text_for_analysis(text)
        analysis = self.analyze_text_structure(clean_text)
        
        if not analysis.requires_chunking:
            return [ChunkInfo(
                text=clean_text,
                index=0,
                chunk_type='normal',
                prosody_type=self._detect_prosody_type(clean_text),
                semantic_weight=1.0,
                expected_duration=analysis.estimated_speaking_time,
                crossfade_duration=0.0
            )]
        
        # Split into sentences first
        sentences = self._split_into_sentences(clean_text)
        
        # Group sentences into semantic chunks
        chunks = self._group_sentences_into_chunks(sentences, analysis.optimal_chunk_size)
        
        # Create ChunkInfo objects
        chunk_infos = []
        for i, chunk_text in enumerate(chunks):
            chunk_type = self._classify_chunk_type(chunk_text)
            prosody_type = self._detect_prosody_type(chunk_text)
            semantic_weight = self._calculate_semantic_weight(chunk_text)
            expected_duration = self._estimate_speaking_time(chunk_text)
            
            # Calculate crossfade duration based on context
            crossfade_duration = self._calculate_crossfade_duration(
                chunk_text, 
                chunks[i-1] if i > 0 else "", 
                chunks[i+1] if i < len(chunks)-1 else ""
            )
            
            chunk_info = ChunkInfo(
                text=chunk_text,
                index=i,
                chunk_type=chunk_type,
                prosody_type=prosody_type,
                semantic_weight=semantic_weight,
                expected_duration=expected_duration,
                context_before=chunks[i-1] if i > 0 else "",
                context_after=chunks[i+1] if i < len(chunks)-1 else "",
                crossfade_duration=crossfade_duration
            )
            
            chunk_infos.append(chunk_info)
        
        return chunk_infos
    
    def _clean_text_for_analysis(self, text: str) -> str:
        """Clean text while preserving structure for analysis"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure proper sentence endings
        if not re.search(r'[.!?]$', text):
            text += '.'
            
        return text
    
    def _estimate_speaking_time(self, text: str) -> float:
        """Estimate speaking time in seconds"""
        # Count characters, giving extra weight to punctuation
        char_count = len(text)
        pause_count = len(re.findall(r'[.!?]', text)) * 0.5  # Major pauses
        pause_count += len(re.findall(r'[,;:]', text)) * 0.2  # Minor pauses
        
        adjusted_length = char_count + pause_count * self.avg_speaking_rate
        return adjusted_length / self.avg_speaking_rate
    
    def _calculate_language_complexity(self, text: str) -> float:
        """Calculate language complexity (0.0 to 1.0)"""
        factors = []
        
        # Sentence length variance
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]
        if sentence_lengths:
            length_variance = np.var(sentence_lengths) / (np.mean(sentence_lengths) ** 2)
            factors.append(min(length_variance, 1.0))
        
        # Vietnamese diacritics density
        vietnamese_chars = len(re.findall(r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳỵỷỹý]', text))
        diacritic_density = vietnamese_chars / len(text) if text else 0
        factors.append(min(diacritic_density * 2, 1.0))
        
        # Technical terms and numbers
        tech_density = len(re.findall(r'[0-9%]+', text)) / len(text.split()) if text.split() else 0
        factors.append(min(tech_density * 3, 1.0))
        
        return np.mean(factors) if factors else 0.5
    
    def _detect_prosody_patterns(self, text: str) -> List[str]:
        """Detect prosody patterns in text"""
        patterns = []
        
        # Check for enumeration
        if any(marker in text.lower() for marker in self.enumeration_markers):
            patterns.append('enumeration')
        
        # Check for dialogue
        if any(marker in text for marker in self.dialogue_markers):
            patterns.append('dialogue')
        
        # Check for questions
        if '?' in text:
            patterns.append('interrogative')
        
        # Check for exclamations
        if '!' in text:
            patterns.append('exclamatory')
        
        # Check for formal tone
        formal_indicators = ['theo đó', 'căn cứ', 'quy định', 'nghị định']
        if any(indicator in text.lower() for indicator in formal_indicators):
            patterns.append('formal')
        
        # Default to narrative if no specific patterns
        if not patterns:
            patterns.append('narrative')
            
        return patterns
    
    def _find_transition_points(self, text: str) -> List[int]:
        """Find optimal transition points for chunking"""
        transition_points = []
        
        # Sentence boundaries
        for match in re.finditer(r'[.!?]\s+', text):
            transition_points.append(match.end())
        
        # Transition words
        for word in self.transition_words:
            for match in re.finditer(rf'\b{re.escape(word)}\b', text, re.IGNORECASE):
                transition_points.append(match.start())
        
        # Paragraph breaks (double spaces or newlines)
        for match in re.finditer(r'\s{2,}', text):
            transition_points.append(match.start())
        
        return sorted(list(set(transition_points)))
    
    def _calculate_optimal_chunk_size(self, text: str, complexity: float) -> int:
        """Calculate optimal chunk size based on text characteristics"""
        base_chunk_size = self.optimal_chunk_chars
        
        # Adjust based on complexity - more aggressive reduction for complex text
        if complexity > 0.7:
            complexity_factor = 0.5  # Very complex text: reduce to 50%
        elif complexity > 0.5:
            complexity_factor = 0.7  # High complexity: reduce to 70%
        elif complexity > 0.3:
            complexity_factor = 0.85  # Medium complexity: reduce to 85%
        else:
            complexity_factor = 1.0  # Low complexity: keep original size
        
        # Adjust based on text length
        text_length = len(text)
        if text_length < 500:
            length_factor = 1.1  # Slightly larger chunks for short text
        elif text_length > 5000:
            length_factor = 0.8  # Smaller chunks for very long text
        elif text_length > 2000:
            length_factor = 0.9  # Moderately smaller chunks for long text
        else:
            length_factor = 1.0
        
        optimal_size = int(base_chunk_size * complexity_factor * length_factor)
        
        # Ensure reasonable bounds with stricter upper limit to prevent memory issues
        return max(200, min(optimal_size, 800))  # Reduced max from 1200 to 800
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences with Vietnamese language considerations"""
        # Split by sentence endings but keep the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:  # Minimum sentence length
                # Ensure sentence ends with punctuation
                if not re.search(r'[.!?]$', sentence):
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _group_sentences_into_chunks(self, sentences: List[str], target_chunk_size: int) -> List[str]:
        """Group sentences into optimal chunks with strict size control"""
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Handle extremely long sentences by splitting them first
            if len(sentence) > target_chunk_size:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # Split the long sentence and add chunks
                split_chunks = self._split_long_sentence(sentence, target_chunk_size)
                chunks.extend(split_chunks)
                continue
            
            # Check if adding this sentence would exceed the target size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= target_chunk_size:
                current_chunk = potential_chunk
            else:
                # Start a new chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Final safety check: ensure no chunk exceeds the target size
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= target_chunk_size:
                final_chunks.append(chunk)
            else:
                # Emergency split for chunks that are still too long
                print(f"Emergency splitting chunk of {len(chunk)} chars (target: {target_chunk_size})")
                split_chunks = self._split_long_sentence(chunk, target_chunk_size)
                final_chunks.extend(split_chunks)
        
        return final_chunks
    
    def _split_long_sentence(self, sentence: str, max_size: int) -> List[str]:
        """Split a long sentence into smaller chunks"""
        if len(sentence) <= max_size:
            return [sentence]
        
        # Try to split by commas first
        if ',' in sentence:
            parts = sentence.split(',')
            chunks = []
            current = ""
            
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                    
                potential = current + "," + part if current else part
                if len(potential) <= max_size:
                    current = potential
                else:
                    if current:
                        chunks.append(current.strip())
                    current = part
            
            if current:
                chunks.append(current.strip())
            
            # If we successfully split and all chunks are reasonable size
            if all(len(chunk) <= max_size for chunk in chunks) and len(chunks) > 1:
                return chunks
        
        # Fallback: split by words
        words = sentence.split()
        chunks = []
        current = ""
        
        for word in words:
            potential = current + " " + word if current else word
            if len(potential) <= max_size:
                current = potential
            else:
                if current:
                    chunks.append(current.strip())
                current = word
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def _classify_chunk_type(self, chunk_text: str) -> str:
        """Classify the type of chunk"""
        chunk_lower = chunk_text.lower()
        
        # Check for enumeration
        if any(marker in chunk_lower for marker in self.enumeration_markers):
            return 'enumeration'
        
        # Check for dialogue
        if any(marker in chunk_text for marker in self.dialogue_markers):
            return 'dialogue'
        
        # Check for transition
        if any(word in chunk_lower for word in self.transition_words):
            return 'transition'
        
        return 'normal'
    
    def _detect_prosody_type(self, text: str) -> str:
        """Detect the primary prosody type for a text chunk"""
        text_lower = text.lower()
        
        # Check for enumeration
        if any(marker in text_lower for marker in self.enumeration_markers):
            return 'enumeration'
        
        # Check for dialogue
        if any(marker in text for marker in self.dialogue_markers):
            return 'dialogue'
        
        # Check for news-like content
        news_indicators = ['theo báo cáo', 'thông tin', 'tin tức', 'phóng viên']
        if any(indicator in text_lower for indicator in news_indicators):
            return 'news'
        
        # Default to narrative
        return 'narrative'
    
    def _calculate_semantic_weight(self, text: str) -> float:
        """Calculate semantic weight (importance) of a chunk"""
        weight_factors = []
        
        # Length factor (longer chunks might be more important)
        length_factor = min(len(text) / 500, 1.0)
        weight_factors.append(length_factor)
        
        # Keyword density
        important_words = ['quan trọng', 'chính', 'cơ bản', 'chủ yếu', 'đặc biệt']
        keyword_count = sum(1 for word in important_words if word in text.lower())
        keyword_factor = min(keyword_count / 3, 1.0)
        weight_factors.append(keyword_factor)
        
        # Punctuation density (more punctuation might indicate complexity)
        punct_density = len(re.findall(r'[.!?]', text)) / len(text) if text else 0
        punct_factor = min(punct_density * 100, 1.0)
        weight_factors.append(punct_factor)
        
        return np.mean(weight_factors) if weight_factors else 0.5
    
    def _calculate_crossfade_duration(self, current_chunk: str, 
                                    previous_chunk: str, 
                                    next_chunk: str) -> float:
        """Calculate optimal crossfade duration based on context and sentence structure"""
        base_duration = 0.1
        
        # Analyze sentence endings and beginnings for better transitions
        current_type = self._classify_chunk_type(current_chunk)
        prev_type = self._classify_chunk_type(previous_chunk) if previous_chunk else 'normal'
        
        # Check for sentence boundaries at chunk borders
        current_ends_sentence = self._ends_with_sentence_boundary(current_chunk)
        current_starts_sentence = self._starts_with_sentence_boundary(current_chunk)
        
        # Adjust duration based on sentence structure
        if current_ends_sentence and current_starts_sentence:
            # Clean sentence boundaries - shorter crossfade
            base_duration *= 0.6
        elif not current_ends_sentence and not current_starts_sentence:
            # Mid-sentence break - longer, smoother crossfade
            base_duration *= 1.4
        
        # Increase crossfade for dialogue transitions
        if current_type == 'dialogue' or prev_type == 'dialogue':
            base_duration *= 1.3
        
        # Increase crossfade for enumeration transitions  
        if current_type == 'enumeration' or prev_type == 'enumeration':
            base_duration *= 1.2
        
        # Reduce crossfade for smooth narrative flow
        if current_type == 'normal' and prev_type == 'normal':
            base_duration *= 0.9
        
        # Cap the duration within reasonable bounds
        return max(0.05, min(base_duration, 0.25))
    
    def _ends_with_sentence_boundary(self, text: str) -> bool:
        """Check if text ends with a clear sentence boundary"""
        text = text.strip()
        if not text:
            return False
        return text[-1] in '.!?'
    
    def _starts_with_sentence_boundary(self, text: str) -> bool:
        """Check if text starts with a new sentence (capitalized word)"""
        text = text.strip()
        if not text:
            return False
        
        # Check if first word is capitalized (indicating sentence start)
        words = text.split()
        if not words:
            return False
            
        first_word = words[0]
        # Remove leading punctuation/quotes
        first_word = first_word.lstrip('"\'«-–—')
        
        return first_word and first_word[0].isupper()
    
    def _detect_prosody_break_points(self, text: str) -> List[int]:
        """Detect natural prosody break points for better chunking"""
        break_points = []
        
        # Strong break points (sentence boundaries)
        for match in re.finditer(r'[.!?]\s+', text):
            break_points.append(match.end())
        
        # Medium break points (clause boundaries)
        for match in re.finditer(r'[,;:]\s+', text):
            break_points.append(match.end())
        
        # Weak break points (conjunctions and transitions)
        transition_pattern = r'\b(' + '|'.join(self.transition_words) + r')\b'
        for match in re.finditer(transition_pattern, text, re.IGNORECASE):
            break_points.append(match.start())
        
        # Remove duplicates and sort
        break_points = sorted(list(set(break_points)))
        
        return break_points
