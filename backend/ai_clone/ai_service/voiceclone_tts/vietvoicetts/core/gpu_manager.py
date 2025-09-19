"""
GPU Manager for dual RTX 5090 load balancing and optimization
"""

import os
import time
import threading
import queue
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

try:
    import torch
    import psutil
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


class GPUStatus(Enum):
    """GPU status enumeration"""
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class GPUInfo:
    """GPU information and status"""
    gpu_id: int
    name: str
    status: GPUStatus
    memory_total: int
    memory_used: int
    memory_free: int
    utilization: float
    temperature: Optional[float] = None
    power_usage: Optional[float] = None
    active_sessions: int = 0
    last_updated: float = 0


@dataclass
class GPUAllocation:
    """GPU allocation for a specific task"""
    gpu_id: int
    session_id: str
    allocated_memory: int
    start_time: float
    estimated_duration: float


class GPUManager:
    """
    Advanced GPU Manager for dual RTX 5090 load balancing
    
    Features:
    - Automatic GPU detection and monitoring
    - Load balancing across multiple GPUs
    - Memory usage tracking and optimization
    - Session management and resource cleanup
    - Performance monitoring and statistics
    """
    
    def __init__(self, max_concurrent_per_gpu: int = 5):
        self.logger = logging.getLogger(__name__)
        self.max_concurrent_per_gpu = max_concurrent_per_gpu
        
        # GPU information and status
        self.gpus: Dict[int, GPUInfo] = {}
        self.allocations: Dict[str, GPUAllocation] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        self._allocation_queue = queue.Queue()
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "successful_allocations": 0,
            "failed_allocations": 0,
            "average_gpu_utilization": 0.0,
            "load_balance_efficiency": 0.0
        }
        
        # Initialize GPU detection
        self._detect_gpus()
        
        # Start monitoring thread
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_gpus, daemon=True)
        self._monitor_thread.start()
    
    def _detect_gpus(self) -> None:
        """Detect available GPUs and their capabilities"""
        self.logger.info("Detecting available GPUs...")
        
        if not TORCH_AVAILABLE:
            self.logger.warning("PyTorch not available for GPU detection")
            return
        
        if not torch.cuda.is_available():
            self.logger.warning("CUDA not available")
            return
        
        gpu_count = torch.cuda.device_count()
        self.logger.info(f"Found {gpu_count} CUDA devices")
        
        for gpu_id in range(gpu_count):
            try:
                device_props = torch.cuda.get_device_properties(gpu_id)
                
                # Get memory info
                torch.cuda.set_device(gpu_id)
                memory_total = torch.cuda.get_device_properties(gpu_id).total_memory
                memory_reserved = torch.cuda.memory_reserved(gpu_id)
                memory_free = memory_total - memory_reserved
                
                gpu_info = GPUInfo(
                    gpu_id=gpu_id,
                    name=device_props.name,
                    status=GPUStatus.AVAILABLE,
                    memory_total=memory_total,
                    memory_used=memory_reserved,
                    memory_free=memory_free,
                    utilization=0.0,
                    last_updated=time.time()
                )
                
                self.gpus[gpu_id] = gpu_info
                self.logger.info(f"GPU {gpu_id}: {device_props.name} - "
                               f"Memory: {memory_total // (1024**3):.1f}GB")
                
            except Exception as e:
                self.logger.error(f"Error detecting GPU {gpu_id}: {e}")
    
    def _monitor_gpus(self) -> None:
        """Background GPU monitoring thread"""
        while self._monitoring_active:
            try:
                self._update_gpu_stats()
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.logger.error(f"GPU monitoring error: {e}")
                time.sleep(10)
    
    def _update_gpu_stats(self) -> None:
        """Update GPU statistics and status"""
        if not TORCH_AVAILABLE:
            return
        
        with self._lock:
            for gpu_id, gpu_info in self.gpus.items():
                try:
                    torch.cuda.set_device(gpu_id)
                    
                    # Update memory usage
                    memory_total = torch.cuda.get_device_properties(gpu_id).total_memory
                    memory_reserved = torch.cuda.memory_reserved(gpu_id)
                    memory_free = memory_total - memory_reserved
                    
                    gpu_info.memory_total = memory_total
                    gpu_info.memory_used = memory_reserved
                    gpu_info.memory_free = memory_free
                    gpu_info.last_updated = time.time()
                    
                    # Calculate utilization based on active sessions
                    gpu_info.utilization = min(100.0, 
                        (gpu_info.active_sessions / self.max_concurrent_per_gpu) * 100)
                    
                    # Update status based on availability
                    if gpu_info.active_sessions >= self.max_concurrent_per_gpu:
                        gpu_info.status = GPUStatus.BUSY
                    else:
                        gpu_info.status = GPUStatus.AVAILABLE
                        
                except Exception as e:
                    self.logger.error(f"Error updating GPU {gpu_id} stats: {e}")
                    gpu_info.status = GPUStatus.ERROR
    
    def get_optimal_gpu(self, estimated_memory: int = 0, 
                       estimated_duration: float = 30.0) -> Optional[int]:
        """
        Select the optimal GPU for a new task
        
        Args:
            estimated_memory: Estimated memory usage in bytes
            estimated_duration: Estimated task duration in seconds
            
        Returns:
            GPU ID or None if no GPU available
        """
        with self._lock:
            available_gpus = [
                (gpu_id, gpu_info) for gpu_id, gpu_info in self.gpus.items()
                if gpu_info.status == GPUStatus.AVAILABLE and
                   gpu_info.active_sessions < self.max_concurrent_per_gpu and
                   gpu_info.memory_free >= estimated_memory
            ]
            
            if not available_gpus:
                self.logger.warning("No available GPUs for allocation")
                return None
            
            # Sort by utilization (lowest first) and memory availability
            available_gpus.sort(key=lambda x: (x[1].utilization, -x[1].memory_free))
            
            selected_gpu_id = available_gpus[0][0]
            self.logger.debug(f"Selected GPU {selected_gpu_id} for allocation")
            
            return selected_gpu_id
    
    def allocate_gpu(self, session_id: str, estimated_memory: int = 0,
                    estimated_duration: float = 30.0) -> Optional[int]:
        """
        Allocate a GPU for a specific session
        
        Args:
            session_id: Unique session identifier
            estimated_memory: Estimated memory usage in bytes
            estimated_duration: Estimated task duration in seconds
            
        Returns:
            Allocated GPU ID or None if allocation failed
        """
        gpu_id = self.get_optimal_gpu(estimated_memory, estimated_duration)
        
        if gpu_id is None:
            self.performance_stats["failed_allocations"] += 1
            return None
        
        with self._lock:
            # Create allocation record
            allocation = GPUAllocation(
                gpu_id=gpu_id,
                session_id=session_id,
                allocated_memory=estimated_memory,
                start_time=time.time(),
                estimated_duration=estimated_duration
            )
            
            self.allocations[session_id] = allocation
            self.gpus[gpu_id].active_sessions += 1
            
            self.performance_stats["successful_allocations"] += 1
            self.performance_stats["total_requests"] += 1
            
            self.logger.info(f"Allocated GPU {gpu_id} for session {session_id}")
            
            return gpu_id
    
    def release_gpu(self, session_id: str) -> bool:
        """
        Release GPU allocation for a session
        
        Args:
            session_id: Session identifier to release
            
        Returns:
            True if successfully released, False otherwise
        """
        with self._lock:
            if session_id not in self.allocations:
                self.logger.warning(f"Session {session_id} not found for release")
                return False
            
            allocation = self.allocations[session_id]
            gpu_id = allocation.gpu_id
            
            # Update GPU status
            if gpu_id in self.gpus:
                self.gpus[gpu_id].active_sessions = max(0, 
                    self.gpus[gpu_id].active_sessions - 1)
            
            # Remove allocation
            del self.allocations[session_id]
            
            self.logger.info(f"Released GPU {gpu_id} for session {session_id}")
            
            return True
    
    def get_onnx_providers(self, gpu_id: Optional[int] = None) -> List[str]:
        """
        Get optimized ONNX providers for the specified or optimal GPU
        
        Args:
            gpu_id: Specific GPU ID, or None for automatic selection
            
        Returns:
            List of ONNX execution providers
        """
        if not ONNX_AVAILABLE:
            return ['CPUExecutionProvider']
        
        providers = []
        
        # If specific GPU requested or GPUs available
        if gpu_id is not None or self.gpus:
            if gpu_id is None:
                gpu_id = self.get_optimal_gpu()
            
            if gpu_id is not None:
                providers.append(('CUDAExecutionProvider', {
                    'device_id': gpu_id,
                    'arena_extend_strategy': 'kNextPowerOfTwo',
                    'gpu_mem_limit': 4 * 1024 * 1024 * 1024,  # 4GB limit
                    'cudnn_conv_algo_search': 'EXHAUSTIVE',
                    'do_copy_in_default_stream': True,
                }))
        
        # Fallback providers
        providers.extend([
            'CPUExecutionProvider'
        ])
        
        return providers
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """Get comprehensive GPU status information"""
        with self._lock:
            status = {
                "total_gpus": len(self.gpus),
                "available_gpus": len([g for g in self.gpus.values() 
                                     if g.status == GPUStatus.AVAILABLE]),
                "busy_gpus": len([g for g in self.gpus.values() 
                                if g.status == GPUStatus.BUSY]),
                "active_sessions": len(self.allocations),
                "performance_stats": self.performance_stats.copy(),
                "gpu_details": {}
            }
            
            for gpu_id, gpu_info in self.gpus.items():
                status["gpu_details"][str(gpu_id)] = {
                    "name": gpu_info.name,
                    "status": gpu_info.status.value,
                    "memory_total_gb": gpu_info.memory_total / (1024**3),
                    "memory_used_gb": gpu_info.memory_used / (1024**3),
                    "memory_free_gb": gpu_info.memory_free / (1024**3),
                    "utilization_percent": gpu_info.utilization,
                    "active_sessions": gpu_info.active_sessions,
                    "last_updated": gpu_info.last_updated
                }
            
            # Calculate average utilization
            if self.gpus:
                avg_util = sum(g.utilization for g in self.gpus.values()) / len(self.gpus)
                self.performance_stats["average_gpu_utilization"] = avg_util
                
                # Calculate load balance efficiency
                max_util = max(g.utilization for g in self.gpus.values()) if self.gpus else 0
                min_util = min(g.utilization for g in self.gpus.values()) if self.gpus else 0
                balance_eff = 100.0 - (max_util - min_util) if max_util > 0 else 100.0
                self.performance_stats["load_balance_efficiency"] = balance_eff
            
            return status
    
    def cleanup_expired_sessions(self, max_duration: float = 600.0) -> int:
        """
        Clean up expired sessions that have exceeded max duration
        
        Args:
            max_duration: Maximum session duration in seconds
            
        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        expired_sessions = []
        
        with self._lock:
            for session_id, allocation in self.allocations.items():
                if current_time - allocation.start_time > max_duration:
                    expired_sessions.append(session_id)
        
        # Release expired sessions
        cleaned_count = 0
        for session_id in expired_sessions:
            if self.release_gpu(session_id):
                cleaned_count += 1
                self.logger.warning(f"Cleaned up expired session {session_id}")
        
        return cleaned_count
    
    def shutdown(self) -> None:
        """Shutdown the GPU manager and clean up resources"""
        self.logger.info("Shutting down GPU manager...")
        
        self._monitoring_active = False
        
        # Wait for monitor thread to finish
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=10)
        
        # Release all allocations
        with self._lock:
            session_ids = list(self.allocations.keys())
            for session_id in session_ids:
                self.release_gpu(session_id)
        
        self.logger.info("GPU manager shutdown complete")


# Global GPU manager instance
_gpu_manager: Optional[GPUManager] = None


def get_gpu_manager() -> GPUManager:
    """Get the global GPU manager instance"""
    global _gpu_manager
    if _gpu_manager is None:
        _gpu_manager = GPUManager()
    return _gpu_manager


def initialize_gpu_manager(max_concurrent_per_gpu: int = 5) -> GPUManager:
    """Initialize the global GPU manager with custom settings"""
    global _gpu_manager
    if _gpu_manager is not None:
        _gpu_manager.shutdown()
    
    _gpu_manager = GPUManager(max_concurrent_per_gpu=max_concurrent_per_gpu)
    return _gpu_manager


def shutdown_gpu_manager() -> None:
    """Shutdown the global GPU manager"""
    global _gpu_manager
    if _gpu_manager is not None:
        _gpu_manager.shutdown()
        _gpu_manager = None
