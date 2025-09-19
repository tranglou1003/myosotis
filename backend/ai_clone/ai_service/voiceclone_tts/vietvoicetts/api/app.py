"""
Application factory for VietVoice TTS FastAPI application
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import traceback
from pathlib import Path

from .routers import health_router, voice_router, synthesis_router, async_router
from .exceptions import TTSError, ValidationError, ConfigurationError
from .models import AppConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with GPU and queue initialization"""
    # Startup
    logger.info("Starting VietVoice TTS API server with multilingual support")
    
    try:
        # Initialize GPU manager for dual RTX 5090 support
        from ..core.gpu_manager import initialize_gpu_manager
        gpu_manager = initialize_gpu_manager(max_concurrent_per_gpu=5)
        logger.info(f"GPU Manager initialized with {len(gpu_manager.gpus)} GPUs")
        
        # Initialize request queue manager
        from ..core.request_queue import initialize_queue_manager
        queue_manager = await initialize_queue_manager(
            max_concurrent_jobs=10
        )
        logger.info("Request Queue Manager initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize managers: {e}")
        # Continue startup even if GPU/queue initialization fails
    
    yield
    
    # Shutdown
    logger.info("Shutting down VietVoice TTS API server")
    
    try:
        # Shutdown managers
        from ..core.gpu_manager import shutdown_gpu_manager
        from ..core.request_queue import shutdown_queue_manager
        
        await shutdown_queue_manager()
        shutdown_gpu_manager()
        logger.info("Managers shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app(config: AppConfig = None) -> FastAPI:
    """
    Application factory to create FastAPI application
    
    Args:
        config: Application configuration
        
    Returns:
        Configured FastAPI application
    """
    if config is None:
        config = AppConfig()
    
    # Create FastAPI application
    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        docs_url="/docs" if config.enable_docs else None,
        redoc_url="/redoc" if config.enable_docs else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware - MUST be added before other middlewares and routers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=False,  # Explicitly set to False
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],  # Allow all headers
        max_age=3600
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(voice_router)
    app.include_router(synthesis_router)
    app.include_router(async_router)  # Add async processing router
    
    # Setup results directory
    results_dir = Path(__file__).parent.parent.parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Add endpoint to serve demo HTML page
    @app.get("/demo", response_class=HTMLResponse)
    async def demo_page():
        """Serve the demo HTML page"""
        demo_path = Path(__file__).parent.parent.parent / "demo_web_interface.html"
        print(f"Looking for demo at: {demo_path}")
        print(f"Demo path exists: {demo_path.exists()}")
        if demo_path.exists():
            return HTMLResponse(content=demo_path.read_text(encoding='utf-8'))
        else:
            # Try alternative path
            alt_demo_path = Path.cwd() / "demo_web_interface.html"
            print(f"Alternative demo path: {alt_demo_path}")
            print(f"Alternative demo exists: {alt_demo_path.exists()}")
            if alt_demo_path.exists():
                return HTMLResponse(content=alt_demo_path.read_text(encoding='utf-8'))
            raise HTTPException(status_code=404, detail=f"Demo page not found at {demo_path} or {alt_demo_path}")

    # Add endpoint to serve result files without streaming support
    @app.get("/results/{filename}")
    @app.head("/results/{filename}")
    async def get_result_file(filename: str, request: Request):        
        """Serve result audio files without streaming support"""
        import time
        import os
        from fastapi.responses import Response
        
        file_path = results_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Wait for file to be completely written (check file stability)
        max_wait = 5  # Maximum 5 seconds wait
        wait_count = 0
        previous_size = 0
        
        while wait_count < max_wait:
            try:
                current_size = file_path.stat().st_size
                if current_size > 0 and current_size == previous_size:
                    # File size hasn't changed for 0.1 seconds, likely complete
                    break
                previous_size = current_size
                time.sleep(0.1)
                wait_count += 0.1
            except OSError:
                # File might be locked, wait a bit more
                time.sleep(0.1)
                wait_count += 0.1
        
        # Get final file size
        file_size = file_path.stat().st_size
        
        if file_size == 0:
            raise HTTPException(status_code=404, detail="File is empty or still being written")
        
        # For HEAD requests, return headers only
        headers = {
            "Content-Length": str(file_size),
            "Accept-Ranges": "none",  # Disable range requests
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache", 
            "Expires": "0",
            "Content-Disposition": f"inline; filename={filename}",
            "Content-Type": "audio/wav"
        }
        
        if request.method == "HEAD":
            return Response(headers=headers)
        
        # Read the entire file and return as Response to avoid range requests
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            return Response(
                content=file_content,
                media_type='audio/wav',
                headers=headers
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Also handle full path requests (fallback)
    @app.get("/home/hieu/ai_giasu/voiceclone_tts/results/{filename}")
    async def get_result_file_fullpath(filename: str, request: Request):
        """Handle requests with full path (fallback)"""
        return await get_result_file(filename, request)
    
    # Model cache management endpoints
    @app.get("/api/cache/stats")
    async def get_cache_stats():
        """Get model cache statistics"""
        try:
            from .services import TTSService
            service = TTSService()
            stats = service.get_cache_stats()
            return {"success": True, "cache_stats": stats}
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"success": False, "error": str(e)}
    
    @app.post("/api/cache/clear")
    async def clear_cache():
        """Clear model cache"""
        try:
            from .services import TTSService
            service = TTSService()
            result = service.clear_cache()
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"success": False, "error": str(e)}
        
    # Enhanced global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation Error",
                "detail": str(exc),
                "errors": exc.errors()
            }
        )
    
    @app.exception_handler(ValidationError)
    async def custom_validation_exception_handler(request: Request, exc: ValidationError):
        logger.error(f"Custom validation error: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Validation Error", 
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(ConfigurationError)
    async def configuration_exception_handler(request: Request, exc: ConfigurationError):
        logger.error(f"Configuration error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Configuration Error", 
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(TTSError)
    async def tts_exception_handler(request: Request, exc: TTSError):
        logger.error(f"TTS error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "TTS Error", 
                "detail": str(exc)
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP exception: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": f"HTTP {exc.status_code}",
                "detail": exc.detail
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error", 
                "detail": "An unexpected error occurred"
            }
        )
    
    # Add catch-all route last to avoid conflicts with specific endpoints
    @app.get("/{path:path}")
    async def get_audio_fallback(path: str):
        # Check if this is a request for a result file with full path
        if "results/" in path:
            # Extract just the filename from the path
            filename = path.split("results/")[-1]
            file_path = results_dir / filename
            if file_path.exists():
                file_size = file_path.stat().st_size
                return FileResponse(
                    path=str(file_path),
                    media_type='audio/wav',
                    filename=filename,
                    headers={
                        "Content-Length": str(file_size),
                        "Cache-Control": "public, max-age=3600",
                        # Explicitly disable range requests
                        "Accept-Ranges": "none"
                    }
                )
        
        # If it doesn't match our pattern or file doesn't exist, raise 404
        raise HTTPException(status_code=404, detail="Resource not found")
    
    return app


def get_app() -> FastAPI:
    """Get application instance with default configuration"""
    return create_app()