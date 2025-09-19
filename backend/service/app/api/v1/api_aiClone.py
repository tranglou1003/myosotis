def process_service_result(result: dict) -> dict:
    """
    Normalize service result to match CreateVideoResponse schema
    """
    if not result.get("success", False):
        # Error case: map error to message, set video_id=None
        return {
            "success": False,
            "video_id": None,
            "message": result.get("error", "Unknown error occurred"),
            "error": result.get("error"),
            "total_processing_time": result.get("total_processing_time"),
            "status": "failed"
        }
    else:
        # Success case: preserve all fields
        return {
            "success": True,
            "video_id": result.get("video_id"),
            "session_id": result.get("session_id"),
            "video_url": result.get("video_url"),
            "video_filename": result.get("video_filename"),
            "status": result.get("status", "pending"),
            "message": result.get("message", "Video creation initiated successfully"),
            "generated_target_text": result.get("generated_target_text"),
            "text_generation_time": result.get("text_generation_time"),
            "video_generation_time": result.get("video_generation_time"),
            "total_processing_time": result.get("total_processing_time")
        }
        
    
# app/api/v1/api_aiClone.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import base64
import logging
import requests
import os
from datetime import datetime

from app.core.database import get_db
from app.schemas.sche_ai_clone import (
    CreateVideoResponse,
    GetUserVideosResponse,
    VideoListItem
)
from app.services.srv_ai_clone import AICloneService
from app.models.model_user import User
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-clone")


def get_ai_clone_service(db: Session = Depends(get_db)):
    """Get AI Clone service instance"""
    return AICloneService(db_session=db)


@router.get("/user-videos/{user_id}", response_model=GetUserVideosResponse)
async def get_user_videos(
    user_id: int,
    db: Session = Depends(get_db),
    service: AICloneService = Depends(get_ai_clone_service)
):
    """
    API 3: Get danh sách video đã tạo của user
    
    Response bao gồm:
    - Thông tin video (URL, filename, status)
    - Input data (reference text, target text)  
    - Generation info (AI generated hay không, topic/description/keywords)
    - Timing info (processing time, created date, completed date)
    - Error info (nếu có)
    """
    try:
        result = service.get_user_videos(user_id)
        
        if not result["success"]:
            if "User not found" in result.get("error", ""):
                raise HTTPException(status_code=404, detail="User not found")
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
        
        # Convert video data to VideoListItem objects
        videos = []
        for video_data in result["videos"]:
            video_item = VideoListItem(**video_data)
            videos.append(video_item)
        
        return GetUserVideosResponse(
            success=True,
            user_id=user_id,
            total_videos=result["total_videos"],
            videos=videos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting videos for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Form-based alternatives for easier frontend integration
@router.post("/create-video-full-text-form", response_model=CreateVideoResponse)
async def create_video_with_full_text_form(
    reference_audio: UploadFile = File(...),
    image: UploadFile = File(...),
    user_id: int = Form(...),
    reference_text: str = Form(...),
    target_text: str = Form(...),
    language: str = Form(default="vietnamese"),
    dynamic_scale: float = Form(default=1.0),
    db: Session = Depends(get_db),
    service: AICloneService = Depends(get_ai_clone_service)
):
    """
    Alternative form-based endpoint cho API 
    """
    try:
        # Validate inputs
        if not reference_text.strip():
            raise HTTPException(status_code=400, detail="Reference text cannot be empty")
        if not target_text.strip():
            raise HTTPException(status_code=400, detail="Target text cannot be empty")
        if len(reference_text) > 500:
            raise HTTPException(status_code=400, detail="Reference text too long (max 500 chars)")
        if len(target_text) > 2000:
            raise HTTPException(status_code=400, detail="Target text too long (max 2000 chars)")
        
        # Same processing as above
        if not reference_audio.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
            raise HTTPException(status_code=400, detail="Audio file must be WAV, MP3, or M4A")
        
        if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Image file must be JPG or PNG")
        
        audio_content = await reference_audio.read()
        image_content = await image.read()
        
        audio_base64 = base64.b64encode(audio_content).decode()
        image_base64 = base64.b64encode(image_content).decode()
        
        result = service.create_video_with_full_text(
            user_id=user_id,
            reference_text=reference_text.strip(),
            target_text=target_text.strip(),
            audio_base64=audio_base64,
            image_base64=image_base64,
            language=language,
            dynamic_scale=dynamic_scale
        )
        processed_result = process_service_result(result)
        if not processed_result["success"]:
            # Map lỗi phổ biến sang mã lỗi phù hợp
            msg = processed_result["message"] or "Unknown error"
            if "not found" in msg.lower():
                raise HTTPException(status_code=404, detail=msg)
            elif "auth" in msg.lower() or "401" in msg:
                raise HTTPException(status_code=401, detail=msg)
            elif "timeout" in msg.lower():
                raise HTTPException(status_code=504, detail=msg)
            else:
                raise HTTPException(status_code=500, detail=msg)
        return CreateVideoResponse(**processed_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in create_video_with_full_text_form")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-video-from-topic-form", response_model=CreateVideoResponse)
async def create_video_from_topic_form(
    reference_audio: UploadFile = File(...),
    image: UploadFile = File(...),
    user_id: int = Form(...),
    reference_text: str = Form(...),
    topic: str = Form(...),
    description: str = Form(default=""),
    keywords: str = Form(default=""),
    language: str = Form(default="vietnamese"),
    dynamic_scale: float = Form(default=1.0),
    db: Session = Depends(get_db),
    service: AICloneService = Depends(get_ai_clone_service)
):
    """
    Alternative form-based endpoint cho API 2
    """
    try:
        # Validate inputs
        if not reference_text.strip():
            raise HTTPException(status_code=400, detail="Reference text cannot be empty")
        if not topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        if len(reference_text) > 500:
            raise HTTPException(status_code=400, detail="Reference text too long (max 500 chars)")
        if len(topic) > 200:
            raise HTTPException(status_code=400, detail="Topic too long (max 200 chars)")
        
        # Same processing as above
        if not reference_audio.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
            raise HTTPException(status_code=400, detail="Audio file must be WAV, MP3, or M4A")
        
        if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Image file must be JPG or PNG")
        
        audio_content = await reference_audio.read()
        image_content = await image.read()
        
        audio_base64 = base64.b64encode(audio_content).decode()
        image_base64 = base64.b64encode(image_content).decode()
        
        result = service.create_video_with_topic(
            user_id=user_id,
            reference_text=reference_text.strip(),
            topic=topic.strip(),
            description=description.strip(),
            keywords=keywords.strip(),
            audio_base64=audio_base64,
            image_base64=image_base64,
            language=language,
            dynamic_scale=dynamic_scale
        )
        processed_result = process_service_result(result)
        if not processed_result["success"]:
            msg = processed_result["message"] or "Unknown error"
            if "not found" in msg.lower():
                raise HTTPException(status_code=404, detail=msg)
            elif "auth" in msg.lower() or "401" in msg:
                raise HTTPException(status_code=401, detail=msg)
            elif "timeout" in msg.lower():
                raise HTTPException(status_code=504, detail=msg)
            else:
                raise HTTPException(status_code=500, detail=msg)
        return CreateVideoResponse(**processed_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in create_video_from_topic_form")
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "service": "AI Clone API", "timestamp": datetime.now()}


@router.get("/video-status/{video_id}")
async def get_video_status(
    video_id: int,
    db: Session = Depends(get_db)
):
    """
    Get status của một video  từ database
    """

    try:
        from app.models.model_ai_clone import AICloneVideo
        
        video = db.query(AICloneVideo).filter(AICloneVideo.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "video_id": video.id,
            "status": video.status,
            "video_url": video.video_url,
            "video_filename": video.video_filename,
            "processing_time": video.processing_time,
            "created_at": video.created_at,
            "completed_at": video.completed_at,
            "error_message": video.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting status for video {video_id}")
        raise HTTPException(status_code=500, detail=str(e))


# Human Clone Proxy Endpoints
@router.get("/human-clone/download/{filename}")
async def download_video_file(filename: str):
    """
    API Download Video
    URL: /api/v1/ai-clone/human-clone/download/{filename}
    
    """
    try:
        # Validate filename format (should be session_id.mp4)
        if not filename.endswith('.mp4'):
            raise HTTPException(status_code=400, detail="Invalid file format. Only MP4 files are supported.")
        
        # Extract session_id from filename (remove .mp4 extension)
        session_id = filename.replace('.mp4', '')
        
        # Try to download from Human Clone service first
        human_clone_url = settings.HUMAN_CLONE_SERVICE_URL
        download_url = f"{human_clone_url}/api/v1/videos/download/{session_id}"
        
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Stream video file từ Human Clone service về client
                def generate():
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                
                headers = {
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'video/mp4',
                    'Content-Length': response.headers.get('Content-Length', '')
                }
                
                return StreamingResponse(
                    generate(),
                    media_type="video/mp4",
                    headers=headers
                )
            elif response.status_code == 404:
                # Fallback: tìm file trong local directories
                local_paths = [
                    f"/home/quangnm/seadev_backend_backup/app/public/human_clone/{filename}",
                    f"/home/quangnm/seadev_backend_backup/public/human_clone/{filename}",
                    f"/home/quangnm/seadev_backend/app_clone/Sonic/res_path/{filename}",
                ]
                
                video_path = None
                for path in local_paths:
                    if os.path.exists(path):
                        video_path = path
                        break
                
                if video_path:
                    # Stream file từ local
                    def generate():
                        with open(video_path, "rb") as video_file:
                            while chunk := video_file.read(8192):
                                yield chunk
                    
                    headers = {
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'video/mp4',
                        'Content-Length': str(os.path.getsize(video_path))
                    }
                    
                    return StreamingResponse(
                        generate(),
                        media_type="video/mp4",
                        headers=headers
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"Video file not found: {filename}")
            else:
                raise HTTPException(status_code=502, detail="Error downloading video from Human Clone service")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Human Clone service: {e}")
            # Fallback to local file if service is down
            local_paths = [
                f"/home/quangnm/seadev_backend/public/app/human_clone/{filename}",
                f"/home/quangnm/seadev_backend_backup/app/public/human_clone/{filename}"
            ]
            
            for path in local_paths:
                if os.path.exists(path):
                    def generate():
                        with open(path, "rb") as video_file:
                            while chunk := video_file.read(8192):
                                yield chunk
                    
                    headers = {
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Content-Type': 'video/mp4',
                        'Content-Length': str(os.path.getsize(path))
                    }
                    
                    return StreamingResponse(
                        generate(),
                        media_type="video/mp4",
                        headers=headers
                    )
            
            raise HTTPException(status_code=503, detail="Human Clone service unavailable and video not found locally")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error downloading video file {filename}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/human-clone/view/{filename}")
async def view_video_file(filename: str):
    """
    API View Video: Stream video 
    URL: /api/v1/ai-clone/human-clone/view/{filename}
    Ví dụ: /api/v1/ai-clone/human-clone/view/36d96955-3f5f-4648-acdd-c06b62579e12.mp4
    
 
    """
    try:
        # Validate filename format
        if not filename.endswith('.mp4'):
            raise HTTPException(status_code=400, detail="Invalid file format. Only MP4 files are supported.")
        
        # Extract session_id from filename
        session_id = filename.replace('.mp4', '')
        
        # Try Human Clone service first
        human_clone_url = settings.HUMAN_CLONE_SERVICE_URL
        view_url = f"{human_clone_url}/api/v1/videos/download/{session_id}"
        
        try:
            response = requests.get(view_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Stream video for viewing (không có attachment header)
                def generate():
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                
                headers = {
                    'Content-Type': 'video/mp4',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': response.headers.get('Content-Length', ''),
                    'Cache-Control': 'public, max-age=3600'  # Cache cho performance
                }
                
                return StreamingResponse(
                    generate(),
                    media_type="video/mp4",
                    headers=headers
                )
            elif response.status_code == 404:
                # Fallback to local files
                local_paths = [
                    f"/home/quangnm/seadev_backend/public/human_clone/{filename}",
                    f"/home/quangnm/seadev_backend_backup/public/human_clone/{filename}",
                    f"/home/quangnm/seadev_backend/app_clone/Sonic/res_path/{filename}",
                    f"/home/quangnm/seadev_backend/static/videos/{filename}"
                ]
                
                video_path = None
                for path in local_paths:
                    if os.path.exists(path):
                        video_path = path
                        break
                
                if video_path:
                    # Stream for viewing
                    def generate():
                        with open(video_path, "rb") as video_file:
                            while chunk := video_file.read(8192):
                                yield chunk
                    
                    headers = {
                        'Content-Type': 'video/mp4',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(os.path.getsize(video_path)),
                        'Cache-Control': 'public, max-age=3600'
                    }
                    
                    return StreamingResponse(
                        generate(),
                        media_type="video/mp4",
                        headers=headers
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"Video file not found: {filename}")
            else:
                raise HTTPException(status_code=502, detail="Error accessing video from Human Clone service")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Human Clone service: {e}")
            # Fallback to local files
            local_paths = [
                f"/home/quangnm/seadev_backend/public/human_clone/{filename}",
                f"/home/quangnm/seadev_backend_backup/public/human_clone/{filename}"
            ]
            
            for path in local_paths:
                if os.path.exists(path):
                    def generate():
                        with open(path, "rb") as video_file:
                            while chunk := video_file.read(8192):
                                yield chunk
                    
                    headers = {
                        'Content-Type': 'video/mp4',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(os.path.getsize(path)),
                        'Cache-Control': 'public, max-age=3600'
                    }
                    
                    return StreamingResponse(
                        generate(),
                        media_type="video/mp4",
                        headers=headers
                    )
            
            raise HTTPException(status_code=503, detail="Human Clone service unavailable and video not found locally")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error viewing video file {filename}")
        raise HTTPException(status_code=500, detail=str(e))
