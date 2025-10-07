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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(admin|staff)$")
    is_active: bool = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, pattern="^(admin|staff)$")
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
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
            email=obj.email,
            role=obj.role,
            is_active=obj.is_active,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )


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


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    password_hash = pwd_context.hash(user_data.password)

    # Create user
    from datetime import datetime
    now = datetime.utcnow()
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        role=user_data.role,
        is_active=user_data.is_active,
        created_at=now,
        updated_at=now
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.from_orm(new_user)


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
    if user_data.email:
        # Check if new email is already taken
        result = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

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
