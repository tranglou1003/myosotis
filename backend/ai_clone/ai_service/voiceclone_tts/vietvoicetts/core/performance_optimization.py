"""
Performance optimization improvements for VietVoice TTS
This file implements advanced caching and preloading strategies
"""

import asyncio
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from ..core.model_config import ModelConfig
from ..core.model import ModelSessionManager
from ..core.english_tts_engine import EnglishTTSEngine

logger = logging.getLogger(__name__)

class OptimizedModelManager:
    """Advanced model manager with preloading and optimized caching"""
    
    _instance = None
    _lock = threading.RLock()
    _initialized = False
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._models: Dict[str, ModelSessionManager] = {}
        self._english_engines: Dict[str, EnglishTTSEngine] = {}
        self._preload_tasks: Dict[str, asyncio.Task] = {}
        self._warm_up_complete = False
        self._preload_lock = threading.RLock()
        self._preload_started = False
        
        self._initialized = True
        
        logger.info("OptimizedModelManager initialized (preloading will start on first request)")
    
    def ensure_preloading_started(self):
        """Ensure background preloading has started (safe to call from sync context)"""
        if not self._preload_started:
            with self._preload_lock:
                if not self._preload_started:
                    self._preload_started = True
                    try:
                        # Try to start preloading if we have an event loop
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(self._background_preload())
                            logger.info("Background preloading started")
                        except RuntimeError:
                            # No event loop running - that's okay, we'll preload on demand
                            logger.info("No event loop available - models will be loaded on demand")
                    except Exception as e:
                        logger.warning(f"Could not start background preloading: {e}")

    async def _background_preload(self):
        """Preload common models in background"""
        logger.info("Starting background model preloading...")
        
        # Common configurations to preload
        preload_configs = [
            # Vietnamese models
            {
                "language": "vietnamese",
                "config_name": "vietnamese_default",
                "config": ModelConfig(language="vietnamese")
            },
            # English model  
            {
                "language": "english",
                "config_name": "english_default", 
                "config": ModelConfig(language="english")
            }
        ]
        
        tasks = []
        for config_info in preload_configs:
            task = asyncio.create_task(self._preload_single_model(config_info))
            tasks.append(task)
        
        # Wait for all preloading to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        self._warm_up_complete = True
        logger.info("Background model preloading completed")
    
    async def _preload_single_model(self, config_info: Dict[str, Any]):
        """Preload a single model configuration"""
        try:
            config_name = config_info["config_name"]
            config = config_info["config"]
            language = config_info["language"]
            
            logger.info(f"Preloading {config_name} model...")
            start_time = time.time()
            
            if language == "english":
                # Preload English engine
                engine = EnglishTTSEngine()
                await asyncio.get_event_loop().run_in_executor(None, engine._load_model)
                
                with self._preload_lock:
                    self._english_engines[config_name] = engine
                    
            else:
                # Preload Vietnamese model
                model_manager = ModelSessionManager(config)
                await asyncio.get_event_loop().run_in_executor(None, model_manager.load_models)
                
                with self._preload_lock:
                    self._models[config_name] = model_manager
            
            load_time = time.time() - start_time
            logger.info(f"Successfully preloaded {config_name} in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to preload {config_name}: {e}")
    
    def get_model(self, config: ModelConfig) -> ModelSessionManager:
        """Get model with optimized lookup"""
        # Ensure preloading has started
        self.ensure_preloading_started()
        
        config_key = self._generate_config_key(config)
        
        # First check preloaded models
        with self._preload_lock:
            if config.language == "english":
                if "english_default" in self._english_engines:
                    # For English, we need to wrap the engine in a compatible interface
                    return self._get_english_model_wrapper(self._english_engines["english_default"])
            else:
                if "vietnamese_default" in self._models:
                    return self._models["vietnamese_default"]
            
            # Check if we have exact match in cache
            if config_key in self._models:
                return self._models[config_key]
        
        # If not preloaded, create on demand
        logger.info(f"Creating model on demand for: {config_key}")
        start_time = time.time()
        
        model_manager = ModelSessionManager(config)
        model_manager.load_models()
        
        with self._preload_lock:
            self._models[config_key] = model_manager
        
        load_time = time.time() - start_time
        logger.info(f"Model created on demand in {load_time:.2f}s")
        
        return model_manager
    
    def _generate_config_key(self, config: ModelConfig) -> str:
        """Generate cache key for configuration"""
        key_parts = [
            config.language,
            str(config.use_gpu),
            str(config.gpu_id) if config.gpu_id is not None else "auto",
            config.model_path or "default"
        ]
        return "|".join(key_parts)
    
    def _get_english_model_wrapper(self, engine: EnglishTTSEngine) -> ModelSessionManager:
        """Create a wrapper to make English engine compatible with ModelSessionManager interface"""
        # This is a simplified approach - in production you might want to create a proper adapter
        class EnglishModelWrapper:
            def __init__(self, engine):
                self.engine = engine
                self.config = ModelConfig(language="english")
            
            def select_sample(self, voice_id: Optional[str] = None, **kwargs):
                # Delegate to the engine's voice selection logic
                return self.engine.get_voice_sample(voice_id)
            
            def cleanup(self):
                pass
        
        return EnglishModelWrapper(engine)
    
    def is_warm(self) -> bool:
        """Check if models are preloaded and ready"""
        return self._warm_up_complete
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self._preload_lock:
            return {
                "preloaded_models": len(self._models),
                "preloaded_english_engines": len(self._english_engines),
                "warm_up_complete": self._warm_up_complete,
                "total_cached_models": len(self._models) + len(self._english_engines)
            }
    
    def clear_cache(self):
        """Clear all cached models"""
        with self._preload_lock:
            # Cleanup models
            for model in self._models.values():
                try:
                    model.cleanup()
                except:
                    pass
            self._models.clear()
            
            # Clear English engines
            self._english_engines.clear()
            
            self._warm_up_complete = False
            
        logger.info("Model cache cleared")


# Global instance
_optimized_manager = None
_manager_lock = threading.Lock()

def get_optimized_manager() -> OptimizedModelManager:
    """Get the optimized model manager instance"""
    global _optimized_manager
    with _manager_lock:
        if _optimized_manager is None:
            _optimized_manager = OptimizedModelManager()
        return _optimized_manager


class RequestBatcher:
    """Batch similar requests for optimal processing"""
    
    def __init__(self, batch_size: int = 3, batch_timeout: float = 0.1):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._pending_requests = []
        self._batch_lock = threading.RLock()
        
    async def add_request(self, request_data: Dict[str, Any], callback: callable):
        """Add request to batch processing queue"""
        with self._batch_lock:
            self._pending_requests.append({
                "data": request_data,
                "callback": callback,
                "timestamp": time.time()
            })
            
            # Process batch if it's full or timeout reached
            if (len(self._pending_requests) >= self.batch_size or 
                self._should_process_batch()):
                await self._process_batch()
    
    def _should_process_batch(self) -> bool:
        """Check if batch should be processed based on timeout"""
        if not self._pending_requests:
            return False
        
        oldest_request = min(req["timestamp"] for req in self._pending_requests)
        return (time.time() - oldest_request) >= self.batch_timeout
    
    async def _process_batch(self):
        """Process pending requests in batch"""
        if not self._pending_requests:
            return
        
        current_batch = self._pending_requests.copy()
        self._pending_requests.clear()
        
        # Group by similar configurations
        batches_by_config = {}
        for request in current_batch:
            config_key = self._get_config_key(request["data"])
            if config_key not in batches_by_config:
                batches_by_config[config_key] = []
            batches_by_config[config_key].append(request)
        
        # Process each group
        tasks = []
        for config_key, batch in batches_by_config.items():
            task = asyncio.create_task(self._process_config_batch(batch))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def _get_config_key(self, request_data: Dict[str, Any]) -> str:
        """Generate key for request configuration"""
        return f"{request_data.get('language', 'vietnamese')}_{request_data.get('voice_id', 'default')}"
    
    async def _process_config_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of requests with same configuration"""
        # This is where you could implement actual batching logic
        # For now, process individually but with shared model instance
        for request in batch:
            try:
                # Process individual request
                result = await self._process_single_request(request["data"])
                request["callback"]({"success": True, "result": result})
            except Exception as e:
                request["callback"]({"success": False, "error": str(e)})
    
    async def _process_single_request(self, request_data: Dict[str, Any]):
        """Process a single request (placeholder)"""
        # This would be replaced with actual TTS processing
        await asyncio.sleep(0.1)  # Simulate processing
        return {"processed": True, "data": request_data}


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self._metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0,
            "total_processing_time": 0
        }
        self._metrics_lock = threading.RLock()
    
    def record_request(self, processing_time: float, cache_hit: bool):
        """Record request metrics"""
        with self._metrics_lock:
            self._metrics["total_requests"] += 1
            self._metrics["total_processing_time"] += processing_time
            
            if cache_hit:
                self._metrics["cache_hits"] += 1
            else:
                self._metrics["cache_misses"] += 1
            
            # Update average
            self._metrics["average_response_time"] = (
                self._metrics["total_processing_time"] / self._metrics["total_requests"]
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        with self._metrics_lock:
            total_requests = self._metrics["total_requests"]
            if total_requests > 0:
                cache_hit_rate = (self._metrics["cache_hits"] / total_requests) * 100
            else:
                cache_hit_rate = 0
            
            return {
                **self._metrics,
                "cache_hit_rate": cache_hit_rate
            }


class SimplePerformanceMonitor:
    """Simple performance monitor without async dependencies"""
    
    def __init__(self):
        self._requests = 0
        self._total_time = 0
        self._cache_hits = 0
    
    def record_request(self, duration: float, cache_hit: bool = False):
        """Record a request"""
        self._requests += 1
        self._total_time += duration
        if cache_hit:
            self._cache_hits += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        avg_time = self._total_time / max(self._requests, 1)
        cache_hit_rate = (self._cache_hits / max(self._requests, 1)) * 100
        
        return {
            "total_requests": self._requests,
            "average_response_time": avg_time,
            "cache_hit_rate": cache_hit_rate,
            "total_time": self._total_time
        }


# Global instances
_request_batcher = RequestBatcher()
_performance_monitor = PerformanceMonitor()

def get_request_batcher() -> RequestBatcher:
    return _request_batcher

def get_performance_monitor() -> PerformanceMonitor:
    return _performance_monitor
