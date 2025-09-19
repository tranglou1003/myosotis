#!/usr/bin/env python
import asyncio
import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add app directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir))

# Ensure required directories exist
base_path = Path(__file__).parent.parent.absolute()
required_dirs = [
    base_path / "temp_clone",
    base_path / "public" / "human_clone",
    base_path / "static" / "audio",
    base_path / "static" / "images"
]

for directory in required_dirs:
    directory.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import schemas after logger is configured
try:
    from schemas.sche_human_clone import HumanCloneRequest
    logger.info("Successfully imported ")
except ImportError as e:
    logger.warning(f"Could not import : {e}")
    
    # Define a basic request model if import fails
    class HumanCloneRequest(BaseModel):
        reference_audio_base64: str
        reference_text: str
        target_text: str
        image_base64: str
        language: str = "vietnamese"
        dynamic_scale: float = 1.0

# Global variables
AI_SERVICE_INITIALIZED = False


async def init_ai_services():
    """Initialize AI services and check GPU availability"""
    global AI_SERVICE_INITIALIZED
    try:
        logger.info("Initializing AI services...")
        
        # Import AI services
        from app.services.srv_ai_manager import AIManager
        
        ai_manager = AIManager()
        
        # Check environment
        env_status = await ai_manager.check_environment()
        logger.info(f"Environment status: {env_status}")
        
        if env_status.get("ai_features_enabled", False):
            AI_SERVICE_INITIALIZED = True
            logger.info("AI services initialized successfully")
        else:
            logger.warning("AI services not fully available, but worker will still run")
            AI_SERVICE_INITIALIZED = False
            
    except Exception as e:
        logger.error(f"Failed to initialize AI services: {e}")
        AI_SERVICE_INITIALIZED = False


async def cleanup_ai_services():
    """Cleanup AI services on shutdown"""
    logger.info("Cleaning up AI services...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await init_ai_services()
    yield
    # Shutdown
    await cleanup_ai_services()


# Create FastAPI app
app = FastAPI(
    title="Human Clone AI Service",
    description="AI service for generating human clone videos",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint with GPU status"""
    try:
        # Import here to avoid issues if services not available
        from app.services.srv_ai_manager import AIManager
        
        ai_manager = AIManager()
        env_status = await ai_manager.check_environment()
        gpu_status = await ai_manager.check_gpu_memory()
        
        return {
            "status": "healthy" if AI_SERVICE_INITIALIZED else "degraded",
            "service": "ai_worker",
            "initialized": AI_SERVICE_INITIALIZED,
            "environment": env_status,
            "gpu": gpu_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai_worker",
            "initialized": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/ai/human-clone/generate")
async def generate_human_clone(request: HumanCloneRequest):
    """
    Generate human clone video and return result immediately
    
    Input: image_base64, audio_base64, reference_text, target_text, language
    Output: video_url, session_id, processing_time
    
    This endpoint generates the video and returns the result directly
    """
    import time
    
    start_time = time.time()
    
    try:
        logger.info("Starting human clone generation...")
        
        # Import AI service
        from app.services.srv_human_clone import HumanCloneService
        
        # Create AI service
        ai_service = HumanCloneService()
        
        # Process immediately (synchronous)
        result = await ai_service.clone_human(request)
        
        processing_time = round(time.time() - start_time, 2)
        
        if result.status.value == "completed":
            logger.info(f" Generation completed in {processing_time}s")
            
            return {
                "success": True,
                "session_id": result.session_id,
                "video_url": result.video_url,
                "video_filename": result.video_filename,
                "processing_time": processing_time,
                "message": "Video generated successfully"
            }
        else:
            logger.error(f"Generation failed: {result.message}")
            return {
                "success": False,
                "error": result.message,
                "processing_time": processing_time
            }
            
    except Exception as e:
        processing_time = round(time.time() - start_time, 2)
        logger.error(f"Generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "processing_time": processing_time
        }


@app.get("/api/v1/videos/download/{session_id}")
async def download_video(session_id: str):
    """Download video file by session ID"""
    try:
        video_path = Path(f"/app/public/human_clone/{session_id}.mp4")
        logger.info(f"Looking for video at: {video_path}")
        logger.info(f"File exists: {video_path.exists()}")
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=f"{session_id}.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("Starting Service...")
    logger.info("Available endpoints:")
    logger.info("   GET  /health")
    logger.info("   POST /ai/human-clone/generate")
    logger.info("   GET  /ai/videos/download/{session_id}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8779,  
        log_level="info",
        access_log=True
    )
