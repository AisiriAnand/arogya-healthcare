"""
Authentication Services
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from supabase import Client

from .config import supabase, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from .models import UserRegister, UserLogin, AuthResponse, UserResponse

class AuthService:
    def __init__(self):
        self.supabase = supabase
    
    async def register_user(self, user_data: UserRegister) -> AuthResponse:
        """Register a new user with email verification"""
        try:
            # Register user with Supabase
            response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed. User might already exist."
                )
            
            # Create user response
            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at
            )
            
            return AuthResponse(
                user=user_response,
                access_token=response.session.access_token if response.session else "",
                refresh_token=response.session.refresh_token if response.session else "",
                expires_in=3600  # 1 hour
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Login user and return tokens"""
        try:
            # Sign in with Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Create user response
            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at
            )
            
            return AuthResponse(
                user=user_response,
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {str(e)}"
            )
    
    async def logout_user(self, token: str) -> bool:
        """Logout user and invalidate token"""
        try:
            # Sign out with Supabase
            self.supabase.auth.sign_out(token)
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Logout failed: {str(e)}"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token refresh failed: {str(e)}"
            )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return user info"""
        try:
            # Verify token with Supabase
            response = self.supabase.auth.get_user(token)
            
            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name"),
                "aud": response.user.aud
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    async def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        try:
            # Send password reset email
            self.supabase.auth.reset_password_email(email)
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password reset failed: {str(e)}"
            )
    
    async def update_password(self, token: str, new_password: str) -> bool:
        """Update user password"""
        try:
            # Update password with Supabase
            self.supabase.auth.update_user({
                "password": new_password
            })
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password update failed: {str(e)}"
            )

# Create auth service instance
auth_service = AuthService()
