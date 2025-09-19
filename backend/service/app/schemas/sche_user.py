from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import date
from app.models.model_user import GenderEnum
from app.schemas.sche_base import BaseModelResponse


class UserProfileBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None 
    hometown: Optional[str] = None 
    country: Optional[str] = None

    @validator('full_name', 'phone', 'address', 'avatar_url', 'city', 'hometown', 'country', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class EmergencyContactBase(BaseModel):
    contact_name: str
    relation: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    is_primary: bool = False

    @validator('contact_name', 'relation', 'phone', 'email', 'address', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None
    profile: UserProfileBase

    @validator('email', 'phone', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile: Optional[UserProfileBase] = None

    @validator('email', 'phone', pre=True)
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    hometown: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class EmergencyContactResponse(EmergencyContactBase):
    id: int
    user_id: int
    created_at: Optional[str] = None


class UserResponse(BaseModel):  
    id: int
    email: EmailStr
    phone: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    profile: Optional[UserProfileResponse] = None
    emergency_contacts: Optional[List[EmergencyContactResponse]] = None
