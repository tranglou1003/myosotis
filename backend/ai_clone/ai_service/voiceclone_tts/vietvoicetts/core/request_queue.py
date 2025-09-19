"""
Request Queue Manager for concurrent TTS processing with job tracking
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class JobProgress:
    """Job progress information"""
    stage: str = "initialized"
    progress_percent: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    estimated_remaining_time: Optional[float] = None


@dataclass
class JobResult:
    """Job execution result"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    audio_base64: Optional[str] = None
    audio_file_path: Optional[str] = None
    processing_stats: Optional[Dict[str, Any]] = None


@dataclass
class TTSJob:
    """TTS processing job"""
    job_id: str
    job_type: str  # "interactive_voice" | "voice_cloning"
    request_data: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    
    # Timing information
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Progress and result
    progress: JobProgress = field(default_factory=JobProgress)
    result: Optional[JobResult] = None
    
    # Processing metadata
    estimated_duration: float = 30.0
    gpu_id: Optional[int] = None
    worker_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
    
    # Client information
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    def update_progress(self, stage: str, progress: float, message: str = "", 
                       details: Optional[Dict[str, Any]] = None,
                       estimated_remaining: Optional[float] = None):
        """Update job progress"""
        self.progress.stage = stage
        self.progress.progress_percent = min(100.0, max(0.0, progress))
        self.progress.message = message
        if details:
            self.progress.details.update(details)
        if estimated_remaining is not None:
            self.progress.estimated_remaining_time = estimated_remaining
    
    def set_result(self, result: JobResult):
        """Set job result and mark as completed or failed"""
        self.result = result
        self.completed_at = time.time()
        self.status = JobStatus.COMPLETED if result.success else JobStatus.FAILED
    
    def get_duration(self) -> Optional[float]:
        """Get job processing duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API response"""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.get_duration(),
            "progress": {
                "stage": self.progress.stage,
                "progress_percent": self.progress.progress_percent,
                "message": self.progress.message,
                "details": self.progress.details,
                "estimated_remaining_time": self.progress.estimated_remaining_time
            },
            "result": {
                "success": self.result.success if self.result else None,
                "audio_base64": self.result.audio_base64 if self.result else None,
                "error_message": self.result.error_message if self.result else None,
                "processing_stats": self.result.processing_stats if self.result else None
            } if self.result else None,
            "gpu_id": self.gpu_id,
            "retry_count": self.retry_count
        }


class RequestQueueManager:
    """
    Advanced request queue manager for concurrent TTS processing
    
    Features:
    - Async job processing with priority queues
    - Real-time progress tracking
    - GPU resource allocation coordination
    - Rate limiting and timeout management
    - Job persistence and recovery
    - Performance monitoring and statistics
    """
    
    def __init__(self, max_concurrent_jobs: int = 10, 
                 max_queue_size: int = 100,
                 default_timeout: float = 300.0):
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_concurrent_jobs = max_concurrent_jobs
        self.max_queue_size = max_queue_size
        self.default_timeout = default_timeout
        
        # Job storage and queues
        self.jobs: Dict[str, TTSJob] = {}
        self.pending_queue = asyncio.PriorityQueue()
        self.processing_jobs: Dict[str, TTSJob] = {}
        
        # Worker management
        self.workers: Dict[str, asyncio.Task] = {}
        self.worker_semaphore = asyncio.Semaphore(max_concurrent_jobs)
        
        # Performance tracking
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "cancelled_jobs": 0,
            "average_processing_time": 0.0,
            "queue_size": 0,
            "active_workers": 0,
            "total_processing_time": 0.0
        }
        
        # Rate limiting (requests per minute per IP)
        self.rate_limits: Dict[str, List[float]] = {}
        self.max_requests_per_minute = 10
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the queue manager"""
        if self._running:
            return
        
        self._running = True
        self.logger.info("Starting Request Queue Manager")
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._stats_task = asyncio.create_task(self._stats_loop())
        
        # Start worker pool
        for i in range(self.max_concurrent_jobs):
            worker_id = f"worker_{i}"
            self.workers[worker_id] = asyncio.create_task(
                self._worker_loop(worker_id)
            )
    
    async def stop(self):
        """Stop the queue manager and clean up"""
        if not self._running:
            return
        
        self.logger.info("Stopping Request Queue Manager")
        self._running = False
        
        # Cancel all pending jobs
        pending_jobs = [job for job in self.jobs.values() 
                       if job.status in [JobStatus.PENDING, JobStatus.QUEUED]]
        for job in pending_jobs:
            await self.cancel_job(job.job_id)
        
        # Stop background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._stats_task:
            self._stats_task.cancel()
        
        # Stop workers
        for worker_task in self.workers.values():
            worker_task.cancel()
        
        # Wait for graceful shutdown
        await asyncio.gather(*self.workers.values(), return_exceptions=True)
        
        self.logger.info("Request Queue Manager stopped")
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        if not client_ip:
            return True
        
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip] = [
                req_time for req_time in self.rate_limits[client_ip]
                if req_time > minute_ago
            ]
        else:
            self.rate_limits[client_ip] = []
        
        # Check rate limit
        if len(self.rate_limits[client_ip]) >= self.max_requests_per_minute:
            return False
        
        # Record new request
        self.rate_limits[client_ip].append(current_time)
        return True
    
    async def submit_job(self, job_type: str, request_data: Dict[str, Any],
                        priority: JobPriority = JobPriority.NORMAL,
                        client_ip: Optional[str] = None,
                        user_agent: Optional[str] = None) -> str:
        """
        Submit a new TTS job to the queue
        
        Args:
            job_type: Type of TTS job ("interactive_voice" | "voice_cloning")
            request_data: Job request parameters
            priority: Job priority level
            client_ip: Client IP address for rate limiting
            user_agent: Client user agent
            
        Returns:
            Job ID for tracking
            
        Raises:
            ValueError: If queue is full or rate limit exceeded
        """
        # Check rate limit
        if not self.check_rate_limit(client_ip):
            raise ValueError(f"Rate limit exceeded for IP {client_ip}")
        
        # Check queue capacity
        if len(self.jobs) >= self.max_queue_size:
            raise ValueError("Queue is full, please try again later")
        
        # Create job
        job_id = str(uuid.uuid4())
        job = TTSJob(
            job_id=job_id,
            job_type=job_type,
            request_data=request_data,
            priority=priority,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        # Estimate processing duration based on text length
        text = request_data.get("text", "")
        text_length = len(text)
        
        if text_length < 500:
            job.estimated_duration = 15.0
        elif text_length < 2000:
            job.estimated_duration = 30.0
        elif text_length < 5000:
            job.estimated_duration = 60.0
        else:
            job.estimated_duration = 120.0
        
        # Store job
        self.jobs[job_id] = job
        job.status = JobStatus.QUEUED
        
        # Add to priority queue (negative priority for max-heap behavior)
        await self.pending_queue.put((-priority.value, time.time(), job_id))
        
        # Update stats
        self.stats["total_jobs"] += 1
        self.stats["queue_size"] = len(self.jobs)
        
        self.logger.info(f"Submitted job {job_id} ({job_type}) with priority {priority.name}")
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and progress information"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        return job.to_dict()
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if it's still pending or queued"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
            job.status = JobStatus.CANCELLED
            job.completed_at = time.time()
            self.stats["cancelled_jobs"] += 1
            self.logger.info(f"Cancelled job {job_id}")
            return True
        
        return False
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop for processing jobs"""
        self.logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Wait for semaphore (rate limiting)
                async with self.worker_semaphore:
                    # Get next job from queue
                    try:
                        priority, timestamp, job_id = await asyncio.wait_for(
                            self.pending_queue.get(), timeout=1.0
                        )
                    except asyncio.TimeoutError:
                        continue
                    
                    if job_id not in self.jobs:
                        continue
                    
                    job = self.jobs[job_id]
                    
                    # Skip cancelled jobs
                    if job.status == JobStatus.CANCELLED:
                        continue
                    
                    # Process the job
                    await self._process_job(job, worker_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        self.logger.info(f"Worker {worker_id} stopped")
    
    async def _process_job(self, job: TTSJob, worker_id: str):
        """Process a single TTS job"""
        job.status = JobStatus.PROCESSING
        job.started_at = time.time()
        job.worker_id = worker_id
        job.update_progress("starting", 0, "Initializing TTS processing")
        
        self.processing_jobs[job.job_id] = job
        self.stats["active_workers"] = len(self.processing_jobs)
        
        self.logger.info(f"Worker {worker_id} processing job {job.job_id}")
        
        try:
            # Import TTS service here to avoid circular imports
            from ..api.services import TTSService
            
            tts_service = TTSService()
            
            # Update progress
            job.update_progress("processing", 10, "TTS service initialized")
            
            # Process based on job type
            if job.job_type == "interactive_voice":
                result = await self._process_interactive_voice(job, tts_service)
            elif job.job_type == "voice_cloning":
                result = await self._process_voice_cloning(job, tts_service)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")
            
            # Set result
            job.set_result(result)
            
            # Update stats
            if result.success:
                self.stats["completed_jobs"] += 1
            else:
                self.stats["failed_jobs"] += 1
            
            # Calculate average processing time
            duration = job.get_duration()
            if duration:
                self.stats["total_processing_time"] += duration
                self.stats["average_processing_time"] = (
                    self.stats["total_processing_time"] / 
                    (self.stats["completed_jobs"] + self.stats["failed_jobs"])
                )
            
            self.logger.info(f"Job {job.job_id} completed in {duration:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Job {job.job_id} failed: {e}")
            
            # Handle retry logic
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.QUEUED
                job.started_at = None
                job.update_progress("retrying", 0, f"Retrying (attempt {job.retry_count})")
                
                # Re-queue job with delay
                await asyncio.sleep(5)
                await self.pending_queue.put((-job.priority.value, time.time(), job.job_id))
                
                self.logger.info(f"Retrying job {job.job_id} (attempt {job.retry_count})")
            else:
                # Mark as failed
                result = JobResult(
                    success=False,
                    error_message=str(e)
                )
                job.set_result(result)
                self.stats["failed_jobs"] += 1
        
        finally:
            # Clean up
            if job.job_id in self.processing_jobs:
                del self.processing_jobs[job.job_id]
            self.stats["active_workers"] = len(self.processing_jobs)
    
    async def _process_interactive_voice(self, job: TTSJob, tts_service) -> JobResult:
        """Process interactive voice synthesis job"""
        data = job.request_data
        
        # Progress callback
        def progress_callback(info):
            stage = info.get("stage", "processing")
            progress = info.get("progress", 50)
            message = info.get("message", "Processing...")
            job.update_progress(stage, progress, message)
        
        job.update_progress("synthesis", 20, "Starting voice synthesis")
        
        # Call TTS service
        response = tts_service.synthesize_interactive_voice(
            text=data["text"],
            gender=data.get("gender", "female"),
            group=data.get("group", "story"),
            area=data.get("area", "northern"),
            emotion=data.get("emotion", "neutral"),
            speed=data.get("speed", 1.0),
            random_seed=data.get("random_seed", 9527),
            enable_chunking=data.get("enable_chunking", True),
            chunk_overlap=data.get("chunk_overlap", 50),
            prosody_consistency=data.get("prosody_consistency", 1.0),
            progress_callback=progress_callback
        )
        
        job.update_progress("finalizing", 90, "Finalizing results")
        
        return JobResult(
            success=True,
            data=response.__dict__ if hasattr(response, '__dict__') else {},
            audio_base64=response.audio_data if hasattr(response, 'audio_data') else None,
            audio_file_path=response.audio_file_path if hasattr(response, 'audio_file_path') else None,
            processing_stats={
                "generation_time": response.generation_time if hasattr(response, 'generation_time') else 0,
                "total_time": response.total_time if hasattr(response, 'total_time') else 0,
                "chunking_used": response.chunking_used if hasattr(response, 'chunking_used') else False
            }
        )
    
    async def _process_voice_cloning(self, job: TTSJob, tts_service) -> JobResult:
        """Process voice cloning synthesis job"""
        data = job.request_data
        
        # Progress callback
        def progress_callback(info):
            stage = info.get("stage", "processing")
            progress = info.get("progress", 50)
            message = info.get("message", "Processing...")
            job.update_progress(stage, progress, message)
        
        job.update_progress("cloning", 20, "Starting voice cloning")
        
        # Call TTS service
        response = tts_service.synthesize_voice_cloning(
            text=data["text"],
            use_default_sample=data.get("use_default_sample", True),
            default_sample_id=data.get("default_sample_id"),
            reference_text=data.get("reference_text"),
            reference_audio_base64=data.get("reference_audio_base64"),
            speed=data.get("speed", 1.0),
            random_seed=data.get("random_seed", 9527),
            enable_chunking=data.get("enable_chunking", True),
            chunk_overlap=data.get("chunk_overlap", 50),
            voice_consistency=data.get("voice_consistency", 1.0),
            progress_callback=progress_callback
        )
        
        job.update_progress("finalizing", 90, "Finalizing results")
        
        return JobResult(
            success=True,
            data=response.__dict__ if hasattr(response, '__dict__') else {},
            audio_base64=response.audio_data if hasattr(response, 'audio_data') else None,
            audio_file_path=response.audio_file_path if hasattr(response, 'audio_file_path') else None,
            processing_stats={
                "generation_time": response.generation_time if hasattr(response, 'generation_time') else 0,
                "total_time": response.total_time if hasattr(response, 'total_time') else 0,
                "chunking_used": response.chunking_used if hasattr(response, 'chunking_used') else False
            }
        )
    
    async def _cleanup_loop(self):
        """Background task to clean up old completed jobs"""
        while self._running:
            try:
                current_time = time.time()
                cleanup_threshold = 3600  # 1 hour
                
                # Find jobs to clean up
                jobs_to_cleanup = []
                for job_id, job in self.jobs.items():
                    if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                        job.completed_at and 
                        current_time - job.completed_at > cleanup_threshold):
                        jobs_to_cleanup.append(job_id)
                
                # Clean up old jobs
                for job_id in jobs_to_cleanup:
                    del self.jobs[job_id]
                    self.logger.debug(f"Cleaned up old job {job_id}")
                
                if jobs_to_cleanup:
                    self.stats["queue_size"] = len(self.jobs)
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def _stats_loop(self):
        """Background task to update statistics"""
        while self._running:
            try:
                self.stats["queue_size"] = len(self.jobs)
                self.stats["active_workers"] = len(self.processing_jobs)
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Stats loop error: {e}")
                await asyncio.sleep(30)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive queue status"""
        return {
            "queue_status": {
                "total_jobs": len(self.jobs),
                "pending_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.PENDING]),
                "queued_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.QUEUED]),
                "processing_jobs": len(self.processing_jobs),
                "completed_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED]),
                "failed_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.FAILED]),
                "cancelled_jobs": len([j for j in self.jobs.values() if j.status == JobStatus.CANCELLED]),
            },
            "performance_stats": self.stats,
            "configuration": {
                "max_concurrent_jobs": self.max_concurrent_jobs,
                "max_queue_size": self.max_queue_size,
                "default_timeout": self.default_timeout,
                "max_requests_per_minute": self.max_requests_per_minute
            }
        }


# Global queue manager instance
_queue_manager: Optional[RequestQueueManager] = None


async def get_queue_manager() -> RequestQueueManager:
    """Get the global queue manager instance"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = RequestQueueManager()
        await _queue_manager.start()
    return _queue_manager


async def initialize_queue_manager(max_concurrent_jobs: int = 10) -> RequestQueueManager:
    """Initialize the global queue manager with custom settings"""
    global _queue_manager
    if _queue_manager is not None:
        await _queue_manager.stop()
    
    _queue_manager = RequestQueueManager(max_concurrent_jobs=max_concurrent_jobs)
    await _queue_manager.start()
    return _queue_manager


async def shutdown_queue_manager():
    """Shutdown the global queue manager"""
    global _queue_manager
    if _queue_manager is not None:
        await _queue_manager.stop()
        _queue_manager = None
