from sqlalchemy import Column, String, Boolean, Integer, Date, Text, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.model_base import BareBaseModel
import enum
from datetime import datetime


class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(BareBaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    emergency_contacts = relationship("EmergencyContact", back_populates="user")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    ai_clone_videos = relationship("AICloneVideo", back_populates="user", cascade="all, delete-orphan")   
    sudoku_games = relationship("Sudoku", back_populates="user", cascade="all, delete-orphan")



class UserProfile(BareBaseModel):
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(Enum(GenderEnum))
    phone = Column(String)
    address = Column(Text)
    avatar_url = Column(String)
    emergency_contact = Column(String)
    city = Column(String)  # Thành phố hiện tại
    hometown = Column(String)  # Quê hương
    country = Column(String)  # Quốc gia
    
    # Relationships
    user = relationship("User", back_populates="profile")



class EmergencyContact(BareBaseModel):
    __tablename__ = "emergency_contacts"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_name = Column(String, nullable=False)
    relation = Column(String, nullable=False)  
    phone = Column(String, nullable=False)
    email = Column(String)
    address = Column(Text)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="emergency_contacts")