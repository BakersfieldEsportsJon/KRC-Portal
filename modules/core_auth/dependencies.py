from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from core.database import get_db
from core.exceptions import AuthenticationError, AuthorizationError
from .models import User
from .utils import verify_token

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    token = credentials.credentials

    # Verify token
    payload = verify_token(token, "access")
    if payload is None:
        raise AuthenticationError("Invalid token")

    # Get user ID from token
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    # Fetch user from database
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found or inactive")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require admin role"""
    if not current_user.is_admin:
        raise AuthorizationError("Admin role required")
    return current_user


async def require_staff(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require staff role (admin or staff)"""
    if not current_user.is_staff:
        raise AuthorizationError("Staff role required")
    return current_user


class RoleChecker:
    """Role-based access control checker"""

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise AuthorizationError(
                f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Common role checkers
require_admin_role = RoleChecker(["admin"])
require_staff_role = RoleChecker(["admin", "staff"])


# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except (AuthenticationError, AuthorizationError):
        return None