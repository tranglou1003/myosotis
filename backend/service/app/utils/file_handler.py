import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.schemas.sche_story import StoryType

class FileHandler:
    folder_map = {
        "image": "static/images",
        "audio": "static/audios", 
        "video": "static/videos"
    }
    
    allowed_extensions = {
        "image": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"},
        "audio": {".mp3", ".wav", ".m4a", ".aac", ".ogg"},
        "video": {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}
    }
    
    max_file_sizes = {
        "image": 10 * 1024 * 1024,  
        "audio": 50 * 1024 * 1024,  
        "video": 100 * 1024 * 1024  }

    @staticmethod
    def validate_file(file: UploadFile, story_type: str) -> bool:
        """Validate file type and size"""
        if story_type not in FileHandler.folder_map:
            raise HTTPException(status_code=400, detail=f"Invalid story type: {story_type}")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in FileHandler.allowed_extensions[story_type]:
            allowed = ", ".join(FileHandler.allowed_extensions[story_type])
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type for {story_type}. Allowed: {allowed}"
            )
        
        if file.size and file.size > FileHandler.max_file_sizes[story_type]:
            max_size_mb = FileHandler.max_file_sizes[story_type] / (1024 * 1024)
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size for {story_type}: {max_size_mb}MB"
            )
        
        return True

    @staticmethod
    async def save_file(file: UploadFile, story_type: str) -> str:
        """Save uploaded file and return file path"""
        FileHandler.validate_file(file, story_type)
        
        folder_path = FileHandler.folder_map[story_type]
        os.makedirs(folder_path, exist_ok=True)
        
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(folder_path, unique_filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
