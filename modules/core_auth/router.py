from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from core.exceptions import CRMException
from .schemas import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    UserCreate, UserResponse, UserUpdate, ChangePasswordRequest
)
from .service import AuthService
from .dependencies import get_current_user, require_admin, require_staff, security
from .utils import verify_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Authenticate user and return tokens"""
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create tokens
    access_token, refresh_token = auth_service.create_tokens(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, "refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    auth_service = AuthService(db)
    user_id = payload.get("sub")
    user = await auth_service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    access_token, refresh_token = auth_service.create_tokens(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
) -> UserResponse:
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.post("/auth/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change current user's password"""
    auth_service = AuthService(db)

    try:
        await auth_service.change_password(current_user.id, password_data)
        return {"message": "Password changed successfully"}
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Admin-only endpoints
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user (admin only)"""
    auth_service = AuthService(db)

    try:
        user = await auth_service.create_user(user_data)
        return UserResponse.from_orm(user)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> List[UserResponse]:
    """List all users (admin only)"""
    # This would be implemented with pagination in a real system
    from sqlalchemy import select
    from .models import User

    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()

    return [UserResponse.from_orm(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID (admin only)"""
    auth_service = AuthService(db)

    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update user (admin only)"""
    auth_service = AuthService(db)

    try:
        user = await auth_service.update_user(user_id, user_data)
        return UserResponse.from_orm(user)
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)"""
    auth_service = AuthService(db)

    try:
        await auth_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except CRMException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)