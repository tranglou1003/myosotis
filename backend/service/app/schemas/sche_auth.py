from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from app.models.model_user import GenderEnum


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None  # Thành phố hiện tại
    hometown: Optional[str] = None  # Quê quán
    country: Optional[str] = None  # Quốc gia

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    message: str = "Login successful"