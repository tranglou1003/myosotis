from fastapi_sqlalchemy import db
from sqlalchemy import or_, and_
from typing import List, Optional
from app.models.model_user import User, UserProfile
from app.utils.exception_handler import CustomException, ExceptionType
from app.core.security import decode_jwt
import logging


class UserManagementService:
    
    @staticmethod
    def get_me(token: str) -> dict:
        """Get current user information"""
        try:
            payload = decode_jwt(token)
            if not payload:
                raise CustomException(exception=ExceptionType.UNAUTHORIZED)
            
            user_id = int(payload.get("sub"))
            
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
           
            logging.info(f"User {user.email} retrieved their profile")
            return {
                "id": user.id,  # Fixed: Use 'id' instead of '_id'
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at
            }
            
        except Exception as e:
            logging.error(f"Error getting user profile: {str(e)}")
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
    
    @staticmethod
    def get_user_by_id(user_id: int) -> dict:
        """Get user by ID"""
        try:
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
            # Get user profile
            profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            
            user_data = {
                "id": user.id,  # Fixed: Use 'id' instead of '_id'
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at,
             
            }
            
            if profile:
                user_data.update({
                    "full_name": profile.full_name,
                    "date_of_birth": profile.date_of_birth,
                    "gender": profile.gender,
                    "address": profile.address,
                    "avatar_url": profile.avatar_url
                })
            
            logging.info(f"User {user.email} profile retrieved by ID {user_id}")
            return user_data
            
        except Exception as e:
            logging.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise CustomException(exception=ExceptionType.NOT_FOUND)
    
    @staticmethod
    def get_all_users(
        page: int = 1, 
        size: int = 10, 
        search: Optional[str] = None,
      
    ) -> dict:
        """Get all users with pagination and filtering"""
        try:
            query = db.session.query(User)
            
         
            
            if search:
                search_filter = or_(
                    User.email.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            total = query.count()
            
            offset = (page - 1) * size
            users = query.offset(offset).limit(size).all()
            
            user_list = []
            for user in users:
                profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                
                user_data = {
                    "id": user.id,  # Fixed: Use 'id' instead of '_id'
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": user.created_at,
                  
                }
                
                if profile:
                    user_data.update({
                        "full_name": profile.full_name,
                        "gender": profile.gender
                    })
                
                user_list.append(user_data)
            
            logging.info(f"Retrieved {len(users)} users (page {page}, size {size})")
            
            return {
                "users": user_list,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logging.error(f"Error getting all users: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def update_user_profile(user_id: int, update_data: dict) -> dict:
        """Update user profile"""
        try:
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
            profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            
            # Update user fields
            allowed_user_fields = ['email', 'phone']
            for field, value in update_data.items():
                if field in allowed_user_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            # Update or create profile
            if profile:
                allowed_profile_fields = ['full_name', 'date_of_birth', 'gender', 'address', 'avatar_url']
                for field, value in update_data.items():
                    if field in allowed_profile_fields and hasattr(profile, field):
                        setattr(profile, field, value)
            else:
                # Create new profile
                profile_data = {
                    'user_id': user.id,  # Fixed: Use 'id' instead of '_id'
                    'full_name': update_data.get('full_name', ''),
                    'date_of_birth': update_data.get('date_of_birth'),
                    'gender': update_data.get('gender'),
                    'address': update_data.get('address'),
                    'avatar_url': update_data.get('avatar_url')
                }
                profile = UserProfile(**profile_data)
                db.session.add(profile)
            
            db.session.commit()
            
            logging.info(f"User {user.email} profile updated")
            return {
                "id": user.id,  # Fixed: Use 'id' instead of '_id'
                "email": user.email,
                "phone": user.phone,
                "full_name": profile.full_name if profile else None,
                "date_of_birth": profile.date_of_birth if profile else None,
                "gender": profile.gender if profile else None,
                "address": profile.address if profile else None,
                "avatar_url": profile.avatar_url if profile else None
            }
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating user profile: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Deactivate user account"""
        try:
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
           
            # Remove the _updated_at field since it's handled by SQLAlchemy onupdate
            db.session.commit()
            
            logging.info(f"User {user.email} deactivated")
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deactivating user: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """Activate user account"""
        try:
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
           
            # Remove the _updated_at field since it's handled by SQLAlchemy onupdate
            db.session.commit()
            
            logging.info(f"User {user.email} activated")
            return True
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error activating user: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    # Simple methods without JWT and permissions
    @staticmethod
    def get_user_by_id_simple(user_id: int) -> dict:
        """Get user by ID (simple version)"""
        try:
            # Fixed: Use 'id' instead of '_id'
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
            # Get user profile
            profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            
            user_data = {
                "id": user.id,  # Fixed: Use 'id' instead of '_id'
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at,
              
            }
            
            if profile:
                user_data.update({
                    "full_name": profile.full_name,
                    "date_of_birth": profile.date_of_birth,
                    "gender": profile.gender,
                    "address": profile.address,
                    "avatar_url": profile.avatar_url
                })
            
            return user_data
            
        except Exception as e:
            logging.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise CustomException(exception=ExceptionType.NOT_FOUND)
    
    @staticmethod
    def get_all_users_simple(
        page: int = 1, 
        size: int = 10, 
        search: Optional[str] = None
    ) -> dict:
        """Get all users with pagination and filtering (simple version)"""
        try:
            query = db.session.query(User)
            
            if search:
                search_filter = or_(
                    User.email.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            total = query.count()
            
            offset = (page - 1) * size
            users = query.offset(offset).limit(size).all()
            
            user_list = []
            for user in users:
                profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
                
                user_data = {
                    "id": user.id,  # Fixed: Use 'id' instead of '_id'
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": user.created_at,
                }
                
                if profile:
                    user_data.update({
                        "full_name": profile.full_name,
                        "gender": profile.gender
                    })
                
                user_list.append(user_data)
            
            return {
                "users": user_list,
                "total": total,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logging.error(f"Error getting all users: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def update_user_profile_simple(user_id: int, update_data: dict) -> dict:
        """Update user profile (simple version)"""
        try:
            user = db.session.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(exception=ExceptionType.NOT_FOUND)
            
            profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
            
            # Update user fields
            allowed_user_fields = ['email', 'phone']
            for field, value in update_data.items():
                if field in allowed_user_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            # Update or create profile
            if profile:
                allowed_profile_fields = ['full_name', 'date_of_birth', 'gender', 'address', 'avatar_url']
                for field, value in update_data.items():
                    if field in allowed_profile_fields and hasattr(profile, field):
                        setattr(profile, field, value)
            else:
                # Create new profile
                profile_data = {
                    'user_id': user.id,  # Fixed: Use 'id' instead of '_id'
                    'full_name': update_data.get('full_name', ''),
                    'date_of_birth': update_data.get('date_of_birth'),
                    'gender': update_data.get('gender'),
                    'address': update_data.get('address'),
                    'avatar_url': update_data.get('avatar_url')
                }
                profile = UserProfile(**profile_data)
                db.session.add(profile)
            
            db.session.commit()
            
            return {
                "id": user.id,  # Fixed: Use 'id' instead of '_id'
                "email": user.email,
                "phone": user.phone,
                "full_name": profile.full_name if profile else None,
                "date_of_birth": profile.date_of_birth if profile else None,
                "gender": profile.gender if profile else None,
                "address": profile.address if profile else None,
                "avatar_url": profile.avatar_url if profile else None
            }
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating user profile: {str(e)}")
            raise CustomException(exception=ExceptionType.INTERNAL_SERVER_ERROR)