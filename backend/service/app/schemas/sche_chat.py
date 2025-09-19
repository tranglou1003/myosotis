# app/schemas/sche_chat.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    user_id: int = Field(..., description="ID of the user from database")
    message: str = Field(..., min_length=1, max_length=1000)
    session_number: int

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatStreamRequest(BaseModel):
    """Request schema for streaming chat endpoint"""
    user_id: int = Field(..., description="ID of the user from database")
    message: str = Field(..., min_length=1, max_length=1000)
    session_number: int = Field(default=0, description="Session number (0 for latest)")

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    session_id: str
    response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatStreamChunk(BaseModel):
    """Schema for streaming response chunks"""
    session_id: str
    content: str
    is_complete: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionListItem(BaseModel):
    """Schema for session list item"""
    session_id: str
    user_name: str
    created_at: str
    total_messages: int
    last_active: str

class SessionSummary(BaseModel):
    """Schema for detailed session information"""
    user_name: str
    created_at: str
    total_messages: int
    last_active: str
    history_length: int


class ChatMessageItem(BaseModel):
    """Schema for individual chat message"""
    id: int
    user_message: str
    bot_response: str
    created_at: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistory(BaseModel):
    """Schema for chat history response"""
    session_id: str
    user_id: int
    session_number: int
    session_name: Optional[str] = None
    total_messages: int
    messages: List[ChatMessageItem]
    created_at: str
    last_active: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistoryListItem(BaseModel):
    """Schema for chat history list item (summary view)"""
    session_id: str
    session_number: int
    session_name: Optional[str] = None
    total_messages: int
    last_message_preview: Optional[str] = None
    created_at: str
    last_active: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatRawRequest(BaseModel):
    message: str

class ChatRawResponse(BaseModel):
    response: str