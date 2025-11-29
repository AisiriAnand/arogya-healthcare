"""
Authentication Models
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="User full name")

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    last_sign_in_at: Optional[datetime]

class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserResponse
    access_token: str
    refresh_token: str
    expires_in: int

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr = Field(..., description="User email address")

class PasswordUpdate(BaseModel):
    """Password update request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")

class EmailVerification(BaseModel):
    """Email verification request"""
    email: EmailStr = Field(..., description="User email address")
