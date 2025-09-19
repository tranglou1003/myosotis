"""
Global Model Cache Manager for TTS Performance Optimization
Keeps models loaded in memory to avoid reloading on each API call
"""

import threading
import time
import weakref
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
import logging

from .model_config import ModelConfig
from .model import ModelSessionManager

logger = logging.getLogger(__name__)


class ModelCacheEntry:
    """Cache entry for a loaded model"""
    
    def __init__(self, model_session_manager: ModelSessionManager, config: ModelConfig):
        self.model_session_manager = model_session_manager
        self.config = config
        self.last_accessed = time.time()
        self.access_count = 0
        self.creation_time = time.time()
    
    def access(self):
        """Mark this entry as accessed"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def is_stale(self, max_idle_time: int = 1800) -> bool:
        """Check if this entry is stale (unused for too long)"""
        return time.time() - self.last_accessed > max_idle_time
    
    def cleanup(self):
        """Clean up the model resources"""
        if self.model_session_manager:
            self.model_session_manager.cleanup()


class GlobalModelCache:
    """Global cache for TTS models to avoid reloading"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._cache: Dict[str, ModelCacheEntry] = {}
        self._cache_lock = threading.RLock()
        self._cleanup_thread = None
        self._running = True
        self._max_cache_size = 5  # Maximum number of models to keep in memory
        self._max_idle_time = 1800  # 30 minutes idle time before cleanup
        self._initialized = True
        
        # Start cleanup thread
        self._start_cleanup_thread()
        logger.info("Global model cache initialized")
    
    def _generate_cache_key(self, config: ModelConfig) -> str:
        """Generate a unique cache key for the model configuration"""
        key_parts = [
            config.language,
            str(config.use_gpu),
            str(config.gpu_id) if config.gpu_id is not None else "auto",
            config.model_path or "default"
        ]
        return "|".join(key_parts)
    
    def get_model(self, config: ModelConfig) -> ModelSessionManager:
        """Get a model from cache or create a new one"""
        cache_key = self._generate_cache_key(config)
        
        with self._cache_lock:
            # Check if model exists in cache
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                entry.access()
                logger.info(f"Retrieved cached model: {cache_key} (accessed {entry.access_count} times)")
                return entry.model_session_manager
            
            # Create new model if not in cache
            logger.info(f"Creating new model for cache key: {cache_key}")
            start_time = time.time()
            
            model_session_manager = ModelSessionManager(config)
            model_session_manager.load_models()
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")
            
            # Add to cache
            entry = ModelCacheEntry(model_session_manager, config)
            self._cache[cache_key] = entry
            
            # Cleanup old entries if cache is full
            self._cleanup_if_needed()
            
            return model_session_manager
    
    def _cleanup_if_needed(self):
        """Clean up cache if it's getting too full"""
        if len(self._cache) <= self._max_cache_size:
            return
        
        # Sort by last accessed time (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest entries
        entries_to_remove = len(self._cache) - self._max_cache_size
        for i in range(entries_to_remove):
            cache_key, entry = sorted_entries[i]
            logger.info(f"Removing old cache entry: {cache_key}")
            entry.cleanup()
            del self._cache[cache_key]
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while self._running:
                try:
                    with self._cache_lock:
                        stale_keys = []
                        for cache_key, entry in self._cache.items():
                            if entry.is_stale(self._max_idle_time):
                                stale_keys.append(cache_key)
                        
                        for cache_key in stale_keys:
                            entry = self._cache[cache_key]
                            logger.info(f"Cleaning up stale cache entry: {cache_key}")
                            entry.cleanup()
                            del self._cache[cache_key]
                    
                    # Sleep for 5 minutes before next cleanup
                    time.sleep(300)
                except Exception as e:
                    logger.error(f"Error in cache cleanup thread: {e}")
                    time.sleep(60)  # Sleep for 1 minute on error
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def clear_cache(self):
        """Clear all cached models"""
        with self._cache_lock:
            for entry in self._cache.values():
                entry.cleanup()
            self._cache.clear()
            logger.info("Model cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._cache_lock:
            stats = {
                "total_entries": len(self._cache),
                "max_cache_size": self._max_cache_size,
                "max_idle_time": self._max_idle_time,
                "entries": {}
            }
            
            for cache_key, entry in self._cache.items():
                stats["entries"][cache_key] = {
                    "language": entry.config.language,
                    "last_accessed": entry.last_accessed,
                    "access_count": entry.access_count,
                    "creation_time": entry.creation_time,
                    "age_seconds": time.time() - entry.creation_time
                }
            
            return stats
    
    def shutdown(self):
        """Shutdown the cache and cleanup resources"""
        self._running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        self.clear_cache()
        logger.info("Global model cache shutdown")


# Global cache instance
_global_cache = None
_cache_lock = threading.Lock()


def get_global_cache() -> GlobalModelCache:
    """Get the global model cache instance"""
    global _global_cache
    with _cache_lock:
        if _global_cache is None:
            _global_cache = GlobalModelCache()
        return _global_cache


def clear_global_cache():
    """Clear the global model cache"""
    global _global_cache
    with _cache_lock:
        if _global_cache is not None:
            _global_cache.clear_cache()


def shutdown_global_cache():
    """Shutdown the global model cache"""
    global _global_cache
    with _cache_lock:
        if _global_cache is not None:
            _global_cache.shutdown()
            _global_cache = None
