from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.security import decode_jwt
from app.models.model_user import User
from fastapi_sqlalchemy import db
from app.utils.exception_handler import CustomException, ExceptionType


security = HTTPBearer()


def get_current_user_from_token(token: str) -> User:
    """Get current user from JWT token string"""
    try:
        payload = decode_jwt(token)
        if not payload:
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
        
        user_id = payload.get("sub")
        if not user_id:
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
        
        user = db.session.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise CustomException(exception=ExceptionType.UNAUTHORIZED)
        
        return user
        
    except CustomException:
        raise
    except Exception:
        raise CustomException(exception=ExceptionType.UNAUTHORIZED)


def login_required(token: str = Depends(security)) -> User:
    """Dependency function for routes that require authentication"""
    try:
        # Extract token from Bearer
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
        
        return get_current_user_from_token(token_str)
        
    except CustomException:
        raise
    except Exception:
        raise CustomException(exception=ExceptionType.UNAUTHORIZED)
