# app/services/srv_ai_clone.py
import os
import requests
from openai import OpenAI
import openai
import base64
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import json
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.config import settings

from app.models.model_ai_clone import AICloneVideo
from app.models.model_user import User

logger = logging.getLogger(__name__)


class AICloneService:
    """Service AI Clone với database integration"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.human_clone_url = settings.HUMAN_CLONE_SERVICE_URL
        self.llm_url = settings.LLM_API_PYTHON_URL
        self.llm_api_key = settings.SEA_LION_API_KEY
        self.llm_model_name = settings.LLM_MODEL_NAME
        self.request_timeout = settings.AI_REQUEST_TIMEOUT
        # Remove trailing slashes
        self.human_clone_url = self.human_clone_url.rstrip('/')
        self.llm_url = self.llm_url.rstrip('/')
    
    def create_video_with_full_text(self, user_id: int, reference_text: str, target_text: str,
                                   audio_base64: str, image_base64: str, 
                                   language: str = "vietnamese", dynamic_scale: float = 1.0) -> Dict[str, Any]:
        """
        Trường hợp 1: Tạo video với target text đầy đủ từ user
        """
        start_time = datetime.now()
        
        try:
            # Validate user exists
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Create database record
            video_record = AICloneVideo(
                user_id=user_id,
                reference_text=reference_text,
                target_text=target_text,
                language=language,
                dynamic_scale=dynamic_scale,
                is_ai_generated_text=False,
                status="pending"
            )
            
            self.db_session.add(video_record)
            self.db_session.commit()
            self.db_session.refresh(video_record)
            
            # Call AI service
            result = self._call_human_clone_service(
                audio_base64, image_base64, reference_text, target_text, language, dynamic_scale
            )
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Update database record
            if result["success"]:
                video_record.session_id = result.get("session_id")
                video_record.video_url = result.get("video_url")
                video_record.video_filename = result.get("video_filename")
                video_record.status = "completed"
                video_record.processing_time = result.get("processing_time")
                video_record.completed_at = datetime.now()
                video_record.updated_at = datetime.now()
            else:
                video_record.status = "failed"
                video_record.error_message = result.get("error")
                video_record.processing_time = total_time
                video_record.updated_at = datetime.now()
            
            self.db_session.commit()
            
            # Build response
            response = {
                "success": result["success"],
                "video_id": video_record.id,
                "session_id": result.get("session_id"),
                "video_url": result.get("video_url"),
                "video_filename": result.get("video_filename"),
                "status": video_record.status,
                "video_generation_time": result.get("processing_time"),
                "total_processing_time": total_time,
                "message": "Video created successfully" if result["success"] else "Video creation failed",
                "error": result.get("error")
            }
            
            logger.info(f"Video creation completed for user {user_id}, video_id: {video_record.id}, success: {result['success']}")
            return response
            
        except Exception as e:
            logger.exception(f"Error in create_video_with_full_text for user {user_id}")
            # Update record if exists
            if 'video_record' in locals():
                video_record.status = "failed"
                video_record.error_message = str(e)
                video_record.updated_at = datetime.now()
                self.db_session.commit()
            
            return {
                "success": False,
                "error": str(e),
                "total_processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def create_video_with_topic(self, user_id: int, reference_text: str, topic: str, 
                               description: str, keywords: str, audio_base64: str, image_base64: str,
                               language: str = "vietnamese", dynamic_scale: float = 1.0) -> Dict[str, Any]:
        """
        Trường hợp 2: Sử dụng LLM tạo target text từ topic/description/keywords, sau đó tạo video
        """
        start_time = datetime.now()
        text_gen_start = None
        video_gen_start = None
        
        try:
            # Validate user exists
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Step 1: Generate target text từ LLM
            text_gen_start = datetime.now()
            
            prompt = self._build_text_generation_prompt(topic, description, keywords, language)
            generated_text_result = self._call_llm_service(prompt, language)
            
            text_gen_time = (datetime.now() - text_gen_start).total_seconds()
            
            if not generated_text_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to generate text: {generated_text_result.get('error')}",
                    "text_generation_time": text_gen_time,
                    "total_processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            generated_target_text = generated_text_result["response"]
            
            # Create database record
            video_record = AICloneVideo(
                user_id=user_id,
                reference_text=reference_text,
                target_text=generated_target_text,
                language=language,
                dynamic_scale=dynamic_scale,
                is_ai_generated_text=True,
                topic=topic,
                description=description,
                keywords=keywords,
                status="pending"
            )
            
            self.db_session.add(video_record)
            self.db_session.commit()
            self.db_session.refresh(video_record)
            
            # Step 2: Create video với generated text
            video_gen_start = datetime.now()
            
            video_result = self._call_human_clone_service(
                audio_base64, image_base64, reference_text, generated_target_text, language, dynamic_scale
            )
            
            video_gen_time = (datetime.now() - video_gen_start).total_seconds()
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Update database record
            if video_result["success"]:
                video_record.session_id = video_result.get("session_id")
                video_record.video_url = video_result.get("video_url")
                video_record.video_filename = video_result.get("video_filename")
                video_record.status = "completed"
                video_record.processing_time = total_time
                video_record.completed_at = datetime.now()
                video_record.updated_at = datetime.now()
            else:
                video_record.status = "failed"
                video_record.error_message = video_result.get("error")
                video_record.processing_time = total_time
                video_record.updated_at = datetime.now()
            
            self.db_session.commit()
            
            # Build response
            response = {
                "success": video_result["success"],
                "video_id": video_record.id,
                "session_id": video_result.get("session_id"),
                "video_url": video_result.get("video_url"),
                "video_filename": video_result.get("video_filename"),
                "status": video_record.status,
                "generated_target_text": generated_target_text,
                "text_generation_time": text_gen_time,
                "video_generation_time": video_gen_time,
                "total_processing_time": total_time,
                "message": "Video created successfully with AI-generated script" if video_result["success"] else "Video creation failed",
                "error": video_result.get("error")
            }
            
            logger.info(f"Video creation with topic completed for user {user_id}, video_id: {video_record.id}, success: {video_result['success']}")
            return response
            
        except Exception as e:
            logger.exception(f"Error in create_video_with_topic for user {user_id}")
            # Update record if exists
            video_id = None
            if 'video_record' in locals():
                video_record.status = "failed"
                video_record.error_message = str(e)
                video_record.updated_at = datetime.now()
                self.db_session.commit()
                video_id = video_record.id
            return {
                "success": False,
                "video_id": video_id if video_id is not None else 0,
                "message": f"Video creation failed: {str(e)}",
                "error": str(e),
                "text_generation_time": (datetime.now() - text_gen_start).total_seconds() if text_gen_start else 0,
                "total_processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    def get_user_videos(self, user_id: int) -> Dict[str, Any]:
        """
        API 3: Get danh sách video theo user_id
        """
        try:
            # Validate user exists
            user = self.db_session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get videos của user, sắp xếp theo created_at desc
            videos = self.db_session.query(AICloneVideo).filter(
                AICloneVideo.user_id == user_id
            ).order_by(desc(AICloneVideo.created_at)).all()
            
            # Convert to response format
            video_list = []
            for video in videos:
                video_item = {
                    "id": video.id,
                    "reference_text": video.reference_text,
                    "target_text": video.target_text,
                    "language": video.language,
                    "status": video.status,
                    "video_url": video.video_url,
                    "video_filename": video.video_filename,
                    "is_ai_generated_text": video.is_ai_generated_text,
                    "topic": video.topic,
                    "description": video.description,
                    "keywords": video.keywords,
                    "processing_time": video.processing_time,
                    "created_at": video.created_at,
                    "completed_at": video.completed_at,
                    "error_message": video.error_message
                }
                video_list.append(video_item)
            
            return {
                "success": True,
                "user_id": user_id,
                "total_videos": len(video_list),
                "videos": video_list
            }
            
        except Exception as e:
            logger.exception(f"Error getting videos for user {user_id}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clean_text_for_voice_clone(self, text: str) -> str:
        """Clean text để tránh lỗi syntax """
        import re
        
        # Remove common LLM formatting issues
        text = re.sub(r'\[.*?\]', '', text)  # Remove [instructions] 
        text = re.sub(r'\*.*?\*', '', text)  # Remove *emphasis*
        text = re.sub(r'`.*?`', '', text)    # Remove `code`
        text = re.sub(r'#{1,6}\s*', '', text)  # Remove markdown headers
        
        # Clean up quotes and formatting
        text = text.replace('"', "'")        # Replace double quotes with single
        text = text.replace('\n', ' ')       # Replace newlines with spaces
        text = re.sub(r'\s+', ' ', text)     # Replace multiple spaces with single space
        text = text.strip('"\'')             # Remove leading/trailing quotes
        text = text.strip()                  # Remove leading/trailing whitespace
        
        # Escape for safety
        text = text.replace('\\', '\\\\')    # Escape backslashes
        text = text.replace("'", "\\'")      # Escape single quotes
        
        return text

    def _call_human_clone_service(self, audio_base64: str, image_base64: str, 
                                 reference_text: str, target_text: str, 
                                 language: str, dynamic_scale: float) -> Dict[str, Any]:
        """Call Human Clone AI service"""
        try:
            # Clean text để tránh syntax errors
            reference_text_clean = self._clean_text_for_voice_clone(reference_text)
            target_text_clean = self._clean_text_for_voice_clone(target_text)
            
            payload = {
                "reference_audio_base64": audio_base64,
                "reference_text": reference_text_clean,
                "target_text": target_text_clean,
                "image_base64": image_base64,
                "language": language,
                "dynamic_scale": dynamic_scale
            }
            
            response = requests.post(
                f"{self.human_clone_url}/ai/human-clone/generate",
                json=payload,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _call_llm_service(self, prompt: str, language: str) -> Dict[str, Any]:
        """Call SEA-LION API using openai.OpenAI client"""
        try:
            system_prompt = {
                "vietnamese": "Bạn là một chuyên gia viết script cho video AI Clone. Hãy tạo nội dung thuyết trình chuyên nghiệp, súc tích và cuốn hút. Tránh sử dụng ký tự đặc biệt, dấu ngoặc vuông, và format markdown.",
                "english": "You are a professional script writer for AI Clone videos. Create engaging, concise, and professional presentation content. Avoid special characters, square brackets, and markdown formatting."
            }
            client = OpenAI(
                api_key=self.llm_api_key,
                base_url=self.llm_url
            )
            completion = client.chat.completions.create(
                model=self.llm_model_name,
                messages=[
                    {"role": "system", "content": system_prompt.get(language, system_prompt["english"])} ,
                    {"role": "user", "content": prompt}
                ],
                max_tokens=750,
                temperature=0.7,
                extra_body={
                    "chat_template_kwargs": {"thinking_mode": "off"}
                }
            )
            content = completion.choices[0].message.content
            return {
                "success": True,
                "response": content,
                "usage": getattr(completion, "usage", {})
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_text_generation_prompt(self, topic: str, description: str, keywords: str, language: str) -> str:
        """Build prompt để generate target text"""
        
        if language == "vietnamese":
            base_prompt = f"""Tạo một script thuyết trình ngắn gọn về chủ đề: "{topic}"

Yêu cầu:
- Độ dài: 2-4 câu hoàn chỉnh (30-60 giây đọc)
- Phong cách: Chuyên nghiệp, rõ ràng, cuốn hút
- Nội dung: Truyền đạt thông tin chính một cách súc tích
- Format: Chỉ trả về text thuần, không có ký tự đặc biệt hay format

"""
        else:
            base_prompt = f"""Create a short presentation script about: "{topic}"

Requirements:
- Length: 2-4 complete sentences (30-60 seconds of speech)
- Style: Professional, clear, and engaging
- Content: Deliver key information concisely
- Format: Return plain text only, no special characters or formatting

"""
        
        if description:
            if language == "vietnamese":
                base_prompt += f"\nMô tả chi tiết: {description}"
            else:
                base_prompt += f"\nDetailed description: {description}"
        
        if keywords:
            if language == "vietnamese":
                base_prompt += f"\nTừ khóa cần đề cập: {keywords}"
            else:
                base_prompt += f"\nKeywords to include: {keywords}"
        
        if language == "vietnamese":
            base_prompt += "\n\nHãy viết script bằng tiếng Việt tự nhiên và dễ hiểu."
        else:
            base_prompt += "\n\nWrite the script in natural and clear English."
        
        if language == "english":
            base_prompt += "\n\nRespond in English language."
        else:
            base_prompt += "\n\nRespond in Vietnamese language."
        
        base_prompt += "\n\nChỉ trả về nội dung script, không cần giải thích thêm."
        
        return base_prompt
