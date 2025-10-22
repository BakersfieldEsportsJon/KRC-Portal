"""
Temporary auth endpoint workaround until module loading is fixed
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import logging
import asyncio
import random

from core.database import AsyncSessionLocal
from core.config import settings

logger = logging.getLogger(__name__)

# Password hashing - support both bcrypt and argon2
pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")

# Security
security = HTTPBearer()

# Router
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    dark_mode: bool


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Import User model from centralized models file
from models import User


# Auth functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")

    return user


# Routes
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint with rate limiting and security hardening

    Rate limit: 5 requests per minute per IP address
    """
    from slowapi.util import get_remote_address

    # Rate limiting is applied at the app level via slowapi middleware

    # Mask username in logs for privacy (show only first 3 chars)
    masked_username = login_data.username[:3] + "***" if len(login_data.username) > 3 else "***"
    logger.info(f"Login attempt from IP {get_remote_address(request)} for user: {masked_username}")

    # Dummy hash to prevent timing attacks when user doesn't exist
    dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU.TLqxKvlOe"

    # Find user by username
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()

    # Always hash password to maintain constant time
    password_hash = user.password_hash if user else dummy_hash
    is_valid_password = verify_password(login_data.password, password_hash)

    # Check all conditions together to prevent timing attacks
    if not user or not is_valid_password or not user.is_active:
        logger.warning(f"Failed login attempt from IP {get_remote_address(request)} for user: {masked_username}")
        # Add random delay to prevent timing attacks
        await asyncio.sleep(random.uniform(0.1, 0.3))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    logger.info(f"Login successful for user: {masked_username}")

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        dark_mode=current_user.dark_mode
    )


class DarkModeUpdate(BaseModel):
    dark_mode: bool


@router.patch("/me/dark-mode", response_model=UserResponse)
async def update_dark_mode(
    dark_mode_data: DarkModeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's dark mode preference"""
    current_user.dark_mode = dark_mode_data.dark_mode
    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        dark_mode=current_user.dark_mode
    )


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password for current user"""
    from modules.core_auth.utils import is_strong_password

    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_strong, message = is_strong_password(request.new_password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Update password
    current_user.password_hash = pwd_context.hash(request.new_password)

    await db.commit()

    logger.info(f"Password changed successfully for user: {current_user.username}")

    return {"message": "Password changed successfully"}
