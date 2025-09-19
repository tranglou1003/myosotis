import os
import time
import shutil
from sqlalchemy.orm import Session
from app.models.model_media import Media, MediaTypeEnum
from app.schemas.sche_media import MediaCreate

folder_map = {
    "image": "static/images",
    "audio": "static/audios",
    "video": "static/videos"
}

def save_file(file, media_type: MediaTypeEnum) -> str:
    save_dir = folder_map[media_type.value]
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{int(time.time())}_{file.filename}"
    file_location = os.path.join(save_dir, filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_location

def create_favorite_media(db: Session, media_in: MediaCreate, file) -> Media:
    file_path = save_file(file, media_in.media_type)

    media = Media(
        user_id=media_in.user_id,
        media_type=media_in.media_type,
        title=media_in.title,
        artist=media_in.artist,
        file_path=file_path,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media
