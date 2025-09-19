from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from typing import List, Optional

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.model_media import Media
from app.schemas.sche_media import MediaTypeEnum, MediaCreate, MediaResponse
from app.services.srv_media import create_favorite_media

router = APIRouter()

@router.get("/user/{user_id}/media", response_model=List[MediaResponse])
def get_user_media(
    user_id: int,
    media_type: Optional[MediaTypeEnum] = Query(None, description="Filter by media type"),
    db: Session = Depends(get_db)
):
    query = db.query(Media).filter(Media.user_id == user_id)
    if media_type:
        query = query.filter(Media.media_type == media_type)
    media_list = query.all()
    if not media_list:
        raise HTTPException(status_code=404, detail="No media found for this user")
    return media_list


@router.post("/upload_media", response_model=MediaResponse)
async def upload_media(
    user_id: int = Form(...),
    media_type: MediaTypeEnum = Form(...),
    title: str = Form(...),
    artist: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        media_in = MediaCreate(
            user_id=user_id,
            media_type=media_type,
            title=title,
            artist=artist,
        )
        media = create_favorite_media(db, media_in, file)
        return media
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
