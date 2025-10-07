from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from typing import Optional, Tuple
from uuid import UUID
from core.exceptions import NotFoundError, ValidationError, AuthenticationError, DuplicateError
from .models import User
from .schemas import UserCreate, UserUpdate, ChangePasswordRequest
from .utils import hash_password, verify_password, create_access_token, create_refresh_token, is_strong_password
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and user management service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check password strength
        is_strong, message = is_strong_password(user_data.password)
        if not is_strong:
            raise ValidationError(message)

        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise DuplicateError("User", "email")

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active
        )

        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Created user: {user.email}")
            return user
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateError("User", "email")

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        logger.info(f"User authenticated: {user.email}")
        return user

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Update fields
        if user_data.email is not None:
            # Check for email uniqueness
            stmt = select(User).where(User.email == user_data.email, User.id != user_id)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise DuplicateError("User", "email")
            user.email = user_data.email

        if user_data.role is not None:
            user.role = user_data.role

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        if user_data.password is not None:
            # Check password strength
            is_strong, message = is_strong_password(user_data.password)
            if not is_strong:
                raise ValidationError(message)
            user.password_hash = hash_password(user_data.password)

        try:
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Updated user: {user.email}")
            return user
        except IntegrityError:
            await self.db.rollback()
            raise DuplicateError("User", "email")

    async def change_password(self, user_id: UUID, password_data: ChangePasswordRequest) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        # Check new password strength
        is_strong, message = is_strong_password(password_data.new_password)
        if not is_strong:
            raise ValidationError(message)

        # Update password
        user.password_hash = hash_password(password_data.new_password)

        await self.db.commit()
        logger.info(f"Password changed for user: {user.email}")
        return True

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user (soft delete by deactivating)"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        user.is_active = False
        await self.db.commit()
        logger.info(f"Deactivated user: {user.email}")
        return True

    def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user"""
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return access_token, refresh_token