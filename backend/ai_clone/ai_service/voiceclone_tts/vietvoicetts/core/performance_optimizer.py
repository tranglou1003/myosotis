"""
Performance optimization utilities for long text TTS processing
"""

import time
import psutil
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Performance metrics for TTS processing"""
    estimated_processing_time: float
    memory_requirement: float  # MB
    optimal_chunk_count: int
    processing_complexity: float
    recommended_batch_size: int


@dataclass
class ProcessingStats:
    """Real-time processing statistics"""
    chunks_processed: int
    total_chunks: int
    current_chunk_time: float
    average_chunk_time: float
    estimated_remaining_time: float
    memory_usage: float
    cpu_usage: float


class PerformanceOptimizer:
    """Performance optimizer for TTS processing"""
    
    def __init__(self):
        self.processing_history = []
        self.baseline_metrics = self._establish_baseline()
        
    def _establish_baseline(self) -> Dict[str, float]:
        """Establish baseline performance metrics"""
        return {
            'chars_per_second': 50.0,  # Characters processed per second
            'memory_per_char': 0.1,    # MB per character
            'overhead_factor': 1.3,    # Processing overhead
            'chunking_overhead': 0.05   # Overhead per chunk
        }
    
    def estimate_processing_time(self, text_length: int, 
                               use_chunking: bool = False,
                               chunk_count: int = 1) -> float:
        """Estimate total processing time for text"""
        base_time = text_length / self.baseline_metrics['chars_per_second']
        
        # Apply overhead
        base_time *= self.baseline_metrics['overhead_factor']
        
        # Add chunking overhead
        if use_chunking:
            chunking_overhead = chunk_count * self.baseline_metrics['chunking_overhead']
            base_time += chunking_overhead
        
        # Add I/O overhead for file operations
        io_overhead = 2.0  # Base I/O time
        if use_chunking:
            io_overhead += chunk_count * 0.5  # Per chunk I/O
        
        return base_time + io_overhead
    
    def estimate_memory_usage(self, text_length: int, 
                            chunk_count: int = 1) -> float:
        """Estimate memory usage in MB"""
        base_memory = text_length * self.baseline_metrics['memory_per_char']
        
        # Add model memory (estimated)
        model_memory = 500.0  # MB for ONNX model
        
        # Add chunk processing memory
        chunk_memory = chunk_count * 50.0  # MB per chunk buffer
        
        return base_memory + model_memory + chunk_memory
    
    def should_use_chunking(self, text: str, 
                          max_memory_mb: float = 2048,
                          max_processing_time: float = 300) -> Tuple[bool, str]:
        """Determine if chunking should be used"""
        text_length = len(text)
        
        # Check memory constraints
        estimated_memory = self.estimate_memory_usage(text_length, 1)
        if estimated_memory > max_memory_mb:
            return True, f"Memory constraint: {estimated_memory:.1f}MB > {max_memory_mb}MB"
        
        # Check processing time constraints
        estimated_time = self.estimate_processing_time(text_length, False)
        if estimated_time > max_processing_time:
            return True, f"Time constraint: {estimated_time:.1f}s > {max_processing_time}s"
        
        # Check text length constraints (ONNX model limits)
        if text_length > 2000:
            return True, f"Text length constraint: {text_length} chars > 2000 chars"
        
        return False, "No chunking needed"
    
    def optimize_chunk_size(self, text: str, 
                          target_chunk_time: float = 30.0) -> int:
        """Calculate optimal chunk size based on performance constraints"""
        text_length = len(text)
        
        # Calculate chunk size for target processing time
        target_chars_per_chunk = int(target_chunk_time * self.baseline_metrics['chars_per_second'])
        
        # Adjust based on system capabilities
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        memory_based_chunk_size = int(available_memory / self.baseline_metrics['memory_per_char'] * 0.3)
        
        # Take the minimum to ensure we don't exceed constraints
        optimal_chunk_size = min(target_chars_per_chunk, memory_based_chunk_size)
        
        # Ensure reasonable bounds
        optimal_chunk_size = max(300, min(optimal_chunk_size, 1200))
        
        return optimal_chunk_size
    
    def calculate_performance_metrics(self, text: str) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        text_length = len(text)
        
        # Determine if chunking is needed
        use_chunking, reason = self.should_use_chunking(text)
        
        if use_chunking:
            optimal_chunk_size = self.optimize_chunk_size(text)
            chunk_count = max(1, (text_length + optimal_chunk_size - 1) // optimal_chunk_size)
        else:
            chunk_count = 1
            optimal_chunk_size = text_length
        
        # Calculate metrics
        estimated_time = self.estimate_processing_time(text_length, use_chunking, chunk_count)
        memory_requirement = self.estimate_memory_usage(text_length, chunk_count)
        
        # Calculate processing complexity
        complexity = self._calculate_processing_complexity(text)
        
        # Determine recommended batch size
        batch_size = self._calculate_batch_size(chunk_count, memory_requirement)
        
        return PerformanceMetrics(
            estimated_processing_time=estimated_time,
            memory_requirement=memory_requirement,
            optimal_chunk_count=chunk_count,
            processing_complexity=complexity,
            recommended_batch_size=batch_size
        )
    
    def _calculate_processing_complexity(self, text: str) -> float:
        """Calculate processing complexity score (0.0 to 1.0)"""
        factors = []
        
        # Text length factor
        length_factor = min(len(text) / 5000, 1.0)
        factors.append(length_factor)
        
        # Vietnamese character density
        vietnamese_chars = len([c for c in text if ord(c) > 127])
        viet_factor = min(vietnamese_chars / len(text) * 2, 1.0) if text else 0
        factors.append(viet_factor)
        
        # Punctuation density (affects prosody processing)
        punct_count = len([c for c in text if c in '.!?,:;'])
        punct_factor = min(punct_count / len(text) * 50, 1.0) if text else 0
        factors.append(punct_factor)
        
        return np.mean(factors) if factors else 0.5
    
    def _calculate_batch_size(self, chunk_count: int, memory_requirement: float) -> int:
        """Calculate optimal batch size for chunk processing"""
        available_memory = psutil.virtual_memory().available / (1024 * 1024)  # MB
        
        # Conservative memory usage (use 50% of available)
        usable_memory = available_memory * 0.5
        
        if memory_requirement > 0:
            max_concurrent_chunks = int(usable_memory / (memory_requirement / chunk_count))
        else:
            max_concurrent_chunks = chunk_count
        
        # Ensure reasonable bounds
        batch_size = max(1, min(max_concurrent_chunks, chunk_count))
        
        # Don't exceed system CPU count for parallel processing
        cpu_count = psutil.cpu_count()
        batch_size = min(batch_size, cpu_count)
        
        return batch_size
    
    def start_processing_monitor(self, total_chunks: int) -> 'ProcessingMonitor':
        """Start a processing monitor for real-time statistics"""
        return ProcessingMonitor(total_chunks, self)
    
    def record_chunk_processing_time(self, chunk_size: int, processing_time: float):
        """Record processing time for future optimization"""
        chars_per_second = chunk_size / processing_time if processing_time > 0 else 0
        
        self.processing_history.append({
            'chunk_size': chunk_size,
            'processing_time': processing_time,
            'chars_per_second': chars_per_second,
            'timestamp': time.time()
        })
        
        # Keep only recent history (last 100 records)
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
        
        # Update baseline metrics based on recent performance
        self._update_baseline_metrics()
    
    def _update_baseline_metrics(self):
        """Update baseline metrics based on recent performance data"""
        if len(self.processing_history) < 5:
            return
        
        recent_history = self.processing_history[-20:]  # Last 20 records
        
        # Calculate average chars per second
        avg_chars_per_second = np.mean([h['chars_per_second'] for h in recent_history])
        
        # Update baseline with exponential smoothing
        alpha = 0.1  # Smoothing factor
        self.baseline_metrics['chars_per_second'] = (
            alpha * avg_chars_per_second + 
            (1 - alpha) * self.baseline_metrics['chars_per_second']
        )


class ProcessingMonitor:
    """Real-time processing monitor"""
    
    def __init__(self, total_chunks: int, optimizer: PerformanceOptimizer):
        self.total_chunks = total_chunks
        self.optimizer = optimizer
        self.chunks_processed = 0
        self.start_time = time.time()
        self.chunk_times = []
        self.current_chunk_start = None
        
    def start_chunk(self):
        """Start timing a chunk"""
        self.current_chunk_start = time.time()
    
    def finish_chunk(self, chunk_size: int):
        """Finish timing a chunk"""
        if self.current_chunk_start is None:
            return
        
        chunk_time = time.time() - self.current_chunk_start
        self.chunk_times.append(chunk_time)
        self.chunks_processed += 1
        
        # Record in optimizer for learning
        self.optimizer.record_chunk_processing_time(chunk_size, chunk_time)
        
        self.current_chunk_start = None
    
    def get_current_stats(self) -> ProcessingStats:
        """Get current processing statistics"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        # Calculate average chunk time
        avg_chunk_time = np.mean(self.chunk_times) if self.chunk_times else 0
        
        # Estimate remaining time
        remaining_chunks = self.total_chunks - self.chunks_processed
        estimated_remaining = remaining_chunks * avg_chunk_time if avg_chunk_time > 0 else 0
        
        # Get system stats
        memory_usage = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        
        # Current chunk time
        current_chunk_time = (current_time - self.current_chunk_start) if self.current_chunk_start else 0
        
        return ProcessingStats(
            chunks_processed=self.chunks_processed,
            total_chunks=self.total_chunks,
            current_chunk_time=current_chunk_time,
            average_chunk_time=avg_chunk_time,
            estimated_remaining_time=estimated_remaining,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage
        )
    
    def get_progress_percentage(self) -> float:
        """Get processing progress as percentage"""
        if self.total_chunks == 0:
            return 100.0
        return (self.chunks_processed / self.total_chunks) * 100.0
