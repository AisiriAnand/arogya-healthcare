"""
Authentication Module

This module handles user authentication using Supabase.
"""

from .services import auth_service
from .models import (
    UserRegister, UserLogin, AuthResponse, UserResponse,
    PasswordReset, PasswordUpdate, EmailVerification
)

__all__ = [
    "auth_service",
    "UserRegister",
    "UserLogin", 
    "AuthResponse",
    "UserResponse",
    "PasswordReset",
    "PasswordUpdate",
    "EmailVerification"
]
