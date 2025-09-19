from fastapi_sqlalchemy import db
from sqlalchemy import or_
from app.models.model_user import User, UserProfile
from app.core.security import verify_password, get_password_hash
from app.schemas.sche_auth import RegisterRequest, LoginRequest, LoginResponse
from app.schemas.sche_user import UserCreateRequest, UserResponse, UserProfileResponse
from app.utils.exception_handler import CustomException, ExceptionType


class AuthService(object):
    __instance = None

    @staticmethod
    def login(data: LoginRequest) -> LoginResponse:
        email = data.email
        password = data.password
        
        if not email or not password:
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
        
        user = db.session.query(User).filter(User.email == email).first()
        
        if not user:
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
        
        if not verify_password(password, user.password_hash):
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)

        # Get user profile
        profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        full_name = profile.full_name if profile else "Unknown"
        
        return LoginResponse(
            user_id=user.id,
            email=user.email,
            full_name=full_name
        )

    @staticmethod
    def register(data: UserCreateRequest) -> UserResponse:
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
