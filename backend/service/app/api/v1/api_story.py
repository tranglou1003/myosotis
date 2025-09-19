# Updated Router (routes/route_story.py)
from fastapi import APIRouter, HTTPException, status, Query, Form, File, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from typing import Optional
import os
from app.services.srv_story import StoryService
from app.schemas.sche_story import (
    StoryLifeCreateRequest, 
    StoryLifeUpdateRequest, 
    StoryLifeResponse,
    StoryType
)
from app.utils.response_formatter import format_response

router = APIRouter(prefix="/stories")

@router.get("/", response_model=dict)
def get_all_stories(
    skip: int = Query(0, ge=0, description="Number of stories to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of stories to return"),
    story_type: Optional[StoryType] = Query(None, description="Filter by story type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID")
):
    """Get all stories with pagination and filtering"""
    data, total = StoryService.get_all(skip=skip, limit=limit, story_type=story_type, user_id=user_id)
    stories = [StoryLifeResponse.from_orm(story) for story in data]
    return format_response(
        data=stories,
        metadata={
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    )

@router.get("/{story_id}", response_model=dict)
def get_story(story_id: int):
    """Get a specific story by ID"""
    try:
        data = StoryService.get_by_id(story_id)
        return format_response(data=StoryLifeResponse.from_orm(data).dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_story(
    user_id: int = Form(..., description="User ID who creates the story"),
    title: str = Form(..., description="Story title"),
    type: StoryType = Form(..., description="Story type"),
    description: Optional[str] = Form(None, description="Story description"),
    start_time: Optional[str] = Form(None, description="Start time (YYYY-MM-DD)"),
    end_time: Optional[str] = Form(None, description="End time (YYYY-MM-DD)"),
    file: Optional[UploadFile] = File(None, description="File upload for image/audio/video stories")
):
    """Create a new story with optional file upload"""
    try:
        # Convert form data to request model
        from datetime import datetime
        
        story_data = {
            "user_id": user_id,
            "title": title,
            "type": type,
            "description": description
        }
        
        # Handle date conversion
        if start_time:
            story_data["start_time"] = datetime.strptime(start_time, "%Y-%m-%d").date()
        if end_time:
            story_data["end_time"] = datetime.strptime(end_time, "%Y-%m-%d").date()
            
        req = StoryLifeCreateRequest(**story_data)
        
        data = await StoryService.create_with_file(req, file)
        response_data = StoryLifeResponse.from_orm(data)
        return format_response(
            data=jsonable_encoder(response_data),
            message="Story created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{story_id}", response_model=dict)
def update_story(story_id: int, req: StoryLifeUpdateRequest):
    """Update story metadata (title, description, etc.)"""
    try:
        data = StoryService.update(story_id, req)
        return format_response(
            data=StoryLifeResponse.from_orm(data).dict(),
            message="Story updated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{story_id}/file", response_model=dict)
async def update_story_file(
    story_id: int,
    file: UploadFile = File(..., description="New file to upload")
):
    """Update story file"""
    try:
        data = await StoryService.update_file(story_id, file)
        return format_response(
            data=StoryLifeResponse.from_orm(data).dict(),
            message="Story file updated successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{story_id}", response_model=dict)
def delete_story(story_id: int):
    """Delete a story and its associated file"""
    try:
        StoryService.delete(story_id)
        return format_response(message="Story deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/user/{user_id}", response_model=dict)
def get_user_stories(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    story_type: Optional[StoryType] = Query(None)
):
    """Get all stories by a specific user"""
    data, total = StoryService.get_by_user_id(
        user_id=user_id, 
        skip=skip, 
        limit=limit, 
        story_type=story_type
    )
    return format_response(
        data=[StoryLifeResponse.from_orm(story).dict() for story in data],
        metadata={
            "total": total,
            "skip": skip,
            "limit": limit,
            "user_id": user_id
        }
    )

@router.get("/{story_id}/file")
def get_story_file(story_id: int):
    """Download/view story file"""
    try:
        story = StoryService.get_by_id(story_id)
        
        if not story.file_path or not os.path.exists(story.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        media_type_map = {
            StoryType.image: "image/*",
            StoryType.audio: "audio/*", 
            StoryType.video: "video/*"
        }
        
        media_type = media_type_map.get(story.type, "application/octet-stream")
        filename = os.path.basename(story.file_path)
        
        return FileResponse(
            path=story.file_path,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

