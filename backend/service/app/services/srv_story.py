from fastapi_sqlalchemy import db
from sqlalchemy import func
from typing import List, Tuple, Optional
from fastapi import UploadFile
from app.models.model_story import Story, StoryType
from app.schemas.sche_story import StoryLifeCreateRequest, StoryLifeUpdateRequest
from app.utils.exception_handler import CustomException, ExceptionType
from app.utils.file_handler import FileHandler
import logging

logger = logging.getLogger(__name__)

class StoryService:
    @staticmethod
    def get_all(
        skip: int = 0, 
        limit: int = 10, 
        story_type: Optional[StoryType] = None,
        user_id: Optional[int] = None
    ) -> Tuple[List[Story], int]:
        """Get all stories with pagination and filtering"""
        try:
            query = db.session.query(Story)
            
            if story_type:
                query = query.filter(Story.type == story_type)
            if user_id:
                query = query.filter(Story.user_id == user_id)
            
            total = query.count()
            stories = query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
            return stories, total
        except Exception as e:
            logger.error(f"Error getting all stories: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to retrieve stories")

    @staticmethod
    def get_by_id(story_id: int) -> Story:
        """Get story by ID"""
        try:
            story = db.session.query(Story).filter(Story.id == story_id).first()
            if not story:
                raise CustomException(ExceptionType.NOT_FOUND, f"Story with ID {story_id} not found")
            return story
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting story by ID {story_id}: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to retrieve story")

    @staticmethod
    def get_by_user_id(
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        story_type: Optional[StoryType] = None
    ) -> Tuple[List[Story], int]:
        """Get stories by user ID with pagination"""
        try:
            query = db.session.query(Story).filter(Story.user_id == user_id)
            
            if story_type:
                query = query.filter(Story.type == story_type)
            
            total = query.count()
            stories = query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
            return stories, total
        except Exception as e:
            logger.error(f"Error getting stories for user {user_id}: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to retrieve user stories")

    @staticmethod
    async def create_with_file(
        req: StoryLifeCreateRequest, 
        file: Optional[UploadFile] = None
    ) -> Story:
        """Create a new story (file required for all types)"""
        try:
            if not file:
                raise CustomException(
                    ExceptionType.BAD_REQUEST, 
                    f"File is required for story type: {req.type.value}"
                )

            story_data = req.dict()
            file_path = await FileHandler.save_file(file, req.type.value)
            story_data['file_path'] = file_path

            story = Story(**story_data)
            db.session.add(story)
            db.session.commit()
            db.session.refresh(story)
            
            logger.info(f"Created story with ID {story.id}")
            return story
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating story: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to create story")

    @staticmethod
    def update(story_id: int, req: StoryLifeUpdateRequest) -> Story:
        """Update a story (file updates handled separately)"""
        try:
            story = StoryService.get_by_id(story_id)
            update_data = req.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(story, key, value)
            
            db.session.commit()
            logger.info(f"Updated story with ID {story_id}")
            return story
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating story {story_id}: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to update story")

    @staticmethod
    async def update_file(story_id: int, file: UploadFile) -> Story:
        """Update story file"""
        try:
            story = StoryService.get_by_id(story_id)
            
            if not file:
                raise CustomException(
                    ExceptionType.BAD_REQUEST, 
                    "File is required for updating"
                )
            
            if story.file_path:
                FileHandler.delete_file(story.file_path)
            
            new_file_path = await FileHandler.save_file(file, story.type.value)
            story.file_path = new_file_path
            
            db.session.commit()
            logger.info(f"Updated file for story with ID {story_id}")
            return story
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating file for story {story_id}: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to update story file")

    @staticmethod
    def delete(story_id: int) -> bool:
        """Delete a story and its associated file"""
        try:
            story = StoryService.get_by_id(story_id)
            
            if story.file_path:
                FileHandler.delete_file(story.file_path)
            
            db.session.delete(story)
            db.session.commit()
            
            logger.info(f"Deleted story with ID {story_id}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error deleting story {story_id}: {str(e)}")
            db.session.rollback()
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to delete story")

    @staticmethod
    def get_stats(user_id: Optional[int] = None) -> dict:
        """Get story statistics"""
        try:
            query = db.session.query(Story)
            if user_id:
                query = query.filter(Story.user_id == user_id)
            
            total_stories = query.count()
            stories_by_type = (
                query.with_entities(Story.type, func.count(Story.id))
                .group_by(Story.type)
                .all()
            )
            
            return {
                "total_stories": total_stories,
                "stories_by_type": {story_type: count for story_type, count in stories_by_type}
            }
        except Exception as e:
            logger.error(f"Error getting story stats: {str(e)}")
            raise CustomException(ExceptionType.INTERNAL_ERROR, "Failed to get story statistics")
