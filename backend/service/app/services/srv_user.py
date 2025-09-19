from fastapi_sqlalchemy import db
from sqlalchemy.orm import joinedload
from app.models.model_user import User, UserProfile, EmergencyContact
from app.core.security import get_password_hash
from app.schemas.sche_user import UserResponse, UserCreateRequest, UserUpdateRequest, UserProfileResponse, EmergencyContactResponse
from app.utils.exception_handler import CustomException, ExceptionType


class UserService(object):
    __instance = None

    @staticmethod
    def get_all_users() -> list[UserResponse]:
        users = (
            db.session.query(User)
            .options(joinedload(User.profile), joinedload(User.emergency_contacts))
            .all()
        )
        
        result = []
        for user in users:
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                phone=user.phone,
                created_at=str(user.created_at) if user.created_at else None,
                updated_at=str(user.updated_at) if user.updated_at else None,  # Added missing field
                profile=None,
                emergency_contacts=[]
            )
            
            if user.profile:
                user_response.profile = UserProfileResponse(
                    id=user.profile.id,
                    user_id=user.profile.user_id,
                    full_name=user.profile.full_name,
                    date_of_birth=user.profile.date_of_birth,
                    gender=user.profile.gender,
                    phone=user.profile.phone,
                    address=user.profile.address,
                    avatar_url=user.profile.avatar_url,
                    city=user.profile.city,
                    hometown=user.profile.hometown,
                    country=user.profile.country,
                    created_at=str(user.profile.created_at) if user.profile.created_at else None,
                    updated_at=str(user.profile.updated_at) if user.profile.updated_at else None
                )
            
            if user.emergency_contacts:
                user_response.emergency_contacts = [
                    EmergencyContactResponse(
                        id=contact.id,
                        user_id=contact.user_id,
                        contact_name=contact.contact_name,
                        relation=contact.relation,
                        phone=contact.phone,
                        email=contact.email,
                        address=contact.address,
                        is_primary=contact.is_primary,
                        created_at=str(contact.created_at) if contact.created_at else None
                    )
                    for contact in user.emergency_contacts
                ]
            
            result.append(user_response)
        
        return result

    @staticmethod
    def get_user_by_id(user_id: int) -> UserResponse:
        user = (
            db.session.query(User)
            .options(joinedload(User.profile), joinedload(User.emergency_contacts))
            .filter(User.id == user_id)
            .first()
        )
        
        if not user:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            phone=user.phone,
            created_at=str(user.created_at) if user.created_at else None,
            updated_at=str(user.updated_at) if user.updated_at else None,  # Added missing field
            profile=None,
            emergency_contacts=[]
        )
        
        if user.profile:
            user_response.profile = UserProfileResponse(
                id=user.profile.id,
                user_id=user.profile.user_id,
                full_name=user.profile.full_name,
                date_of_birth=user.profile.date_of_birth,
                gender=user.profile.gender,
                phone=user.profile.phone,
                address=user.profile.address,
                avatar_url=user.profile.avatar_url,
                city=user.profile.city,
                hometown=user.profile.hometown,
                country=user.profile.country,
                created_at=str(user.profile.created_at) if user.profile.created_at else None,
                updated_at=str(user.profile.updated_at) if user.profile.updated_at else None
            )
        
        if user.emergency_contacts:
            user_response.emergency_contacts = [
                EmergencyContactResponse(
                    id=contact.id,
                    user_id=contact.user_id,
                    contact_name=contact.contact_name,
                    relation=contact.relation,
                    phone=contact.phone,
                    email=contact.email,
                    address=contact.address,
                    is_primary=contact.is_primary,
                    created_at=str(contact.created_at) if contact.created_at else None
                )
                for contact in user.emergency_contacts
            ]
        
        return user_response

    @staticmethod
    def create_user(data: UserCreateRequest) -> UserResponse:
        # Check if user already exists
        exist_user = db.session.query(User).filter(User.email == data.email).first()
        if exist_user:
            raise CustomException(exception=ExceptionType.CONFLICT)
        
        # Check if phone is already used (if provided)
        if data.phone:
            exist_phone = db.session.query(User).filter(User.phone == data.phone).first()
            if exist_phone:
                raise CustomException(exception=ExceptionType.CONFLICT)
        
        # Create user
        new_user = User(
            email=data.email,
            phone=data.phone,
            password_hash=get_password_hash(data.password)
        )
        db.session.add(new_user)
        db.session.flush()  # Get the user ID
        
        # Create user profile
        profile_data = {
            "user_id": new_user.id,
            "full_name": data.profile.full_name,
            "date_of_birth": data.profile.date_of_birth,
            "gender": data.profile.gender,
            "phone": data.profile.phone,
            "address": data.profile.address,
            "avatar_url": data.profile.avatar_url,
            "city": data.profile.city,
            "hometown": data.profile.hometown,
            "country": data.profile.country
        }
        
        new_profile = UserProfile(**profile_data)
        db.session.add(new_profile)
        db.session.commit()
        
        # Return user response
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            phone=new_user.phone,
            created_at=str(new_user.created_at) if new_user.created_at else None,
            updated_at=str(new_user.updated_at) if new_user.updated_at else None,
            profile=UserProfileResponse(
                id=new_profile.id,
                user_id=new_profile.user_id,
                full_name=new_profile.full_name,
                date_of_birth=new_profile.date_of_birth,
                gender=new_profile.gender,
                phone=new_profile.phone,
                address=new_profile.address,
                avatar_url=new_profile.avatar_url,
                city=new_profile.city,
                hometown=new_profile.hometown,
                country=new_profile.country,
                created_at=str(new_profile.created_at) if new_profile.created_at else None,
                updated_at=str(new_profile.updated_at) if new_profile.updated_at else None
            )
        )

    @staticmethod
    def update_user(user_id: int, data: UserUpdateRequest) -> UserResponse:
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        # Update user fields
        if data.email is not None:
            # Check if email is already used by another user
            exist_email = db.session.query(User).filter(
                User.email == data.email, User.id != user_id
            ).first()
            if exist_email:
                raise CustomException(exception=ExceptionType.CONFLICT)
            user.email = data.email
        
        if data.phone is not None:
            # Check if phone is already used by another user
            exist_phone = db.session.query(User).filter(
                User.phone == data.phone, User.id != user_id
            ).first()
            if exist_phone:
                raise CustomException(exception=ExceptionType.CONFLICT)
            user.phone = data.phone
        
        # Update profile if provided
        if data.profile is not None:
            profile = db.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            if profile:
                profile.full_name = data.profile.full_name
                profile.date_of_birth = data.profile.date_of_birth
                profile.gender = data.profile.gender
                profile.phone = data.profile.phone
                profile.address = data.profile.address
                profile.avatar_url = data.profile.avatar_url
                profile.city = data.profile.city
                profile.hometown = data.profile.hometown
                profile.country = data.profile.country

        db.session.commit()
        
        return UserService.get_user_by_id(user_id)

    @staticmethod
    def delete_user(user_id: int):
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(exception=ExceptionType.NOT_FOUND)
        
        # Delete related records first
        db.session.query(UserProfile).filter(UserProfile.user_id == user_id).delete()
        db.session.query(EmergencyContact).filter(EmergencyContact.user_id == user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()