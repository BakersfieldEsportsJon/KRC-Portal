"""
User management API for admin functions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

from core.database import AsyncSessionLocal
from auth_workaround import get_current_user, User

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=4)  # Temporary password - user must change on first login
    role: str = Field(..., pattern="^(admin|staff)$")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, pattern="^(admin|staff)$")
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    dark_mode: bool
    password_setup_required: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            username=obj.username,
            email=obj.email,
            role=obj.role,
            is_active=obj.is_active,
            dark_mode=obj.dark_mode,
            password_setup_required=getattr(obj, 'password_setup_required', False),
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )


class UserCreateResponse(UserResponse):
    """Response when creating a user - includes setup info"""
    setup_token: Optional[str] = None
    setup_link: Optional[str] = None
    message: str


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (admin only)"""
    result = await db.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("", response_model=UserCreateResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (admin only)

    Admin sets a simple temporary password.
    User will be required to change password on first login.
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with temporary password - must be changed on first login
    now = datetime.utcnow()

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=pwd_context.hash(user_data.password),  # Temporary, must be changed
        role=user_data.role,
        is_active=True,  # Active immediately
        password_setup_required=True,  # Must change on first login
        created_at=now,
        updated_at=now
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"NEW USER CREATED: {new_user.username} ({new_user.email}) - Password change required on first login")

    response = UserCreateResponse.from_orm(new_user)
    response.message = f"User created successfully. User will be prompted to change password on first login."

    return response


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user (admin only)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from demoting themselves
    if str(user.id) == str(current_user.id) and user_data.role and user_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )

    # Update fields
    if user_data.username:
        # Check if new username is already taken
        result = await db.execute(
            select(User).where(User.username == user_data.username, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        user.username = user_data.username
        user.email = f"{user_data.username}@example.com"  # Update placeholder email

    if user_data.password:
        user.password_hash = pwd_context.hash(user_data.password)

    if user_data.role:
        user.role = user_data.role

    if user_data.is_active is not None:
        # Prevent admin from deactivating themselves
        if str(user.id) == str(current_user.id) and not user_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        user.is_active = user_data.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse.from_orm(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user (admin only)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deleting themselves
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    await db.delete(user)
    await db.commit()

    return {"message": "User deleted successfully"}
