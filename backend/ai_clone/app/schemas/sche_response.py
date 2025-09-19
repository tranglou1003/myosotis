"""
Response Schemas - Base response models for API
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    http_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data payload")
    success: bool = Field(True, description="Success status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "http_code": 200,
                "message": "Operation completed successfully",
                "data": None,
                "success": True
            }
        }


class SuccessResponse(BaseResponse):
    """Success response model"""
    http_code: int = Field(200, description="HTTP status code")
    success: bool = Field(True, description="Success status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "http_code": 200,
                "message": "Operation completed successfully",
                "data": {"result": "success"},
                "success": True
            }
        }


class ErrorResponse(BaseResponse):
    """Error response model"""
    http_code: int = Field(400, description="HTTP error code")
    success: bool = Field(False, description="Success status")
    error_code: Optional[str] = Field(None, description="Internal error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "http_code": 400,
                "message": "Bad request - invalid input data",
                "data": None,
                "success": False,
                "error_code": "INVALID_INPUT",
                "details": {"field": "email", "reason": "Invalid format"}
            }
        }
