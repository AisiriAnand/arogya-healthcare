"""
Authentication Router
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from .services import auth_service
from .models import (
    UserRegister, UserLogin, AuthResponse, UserResponse,
    PasswordReset, PasswordUpdate, EmailVerification
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user with email verification"""
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin):
    """Login user and return access token"""
    return await auth_service.login_user(login_data)

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate token"""
    token = credentials.credentials
    await auth_service.logout_user(token)
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    return await auth_service.refresh_token(refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user.get("created_at", ""),
        last_sign_in_at=current_user.get("last_sign_in_at")
    )

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Send password reset email"""
    await auth_service.reset_password(reset_data.email)
    return {"message": "Password reset email sent"}

@router.post("/update-password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user password"""
    await auth_service.update_password(password_data.new_password)
    return {"message": "Password updated successfully"}

@router.post("/verify-email")
async def verify_email(verification_data: EmailVerification):
    """Resend email verification"""
    # This would typically trigger Supabase to send verification email
    return {"message": "Verification email sent"}

@router.get("/check")
async def check_auth():
    """Check if authentication service is running"""
    return {"status": "Authentication service is running", "provider": "Supabase"}
