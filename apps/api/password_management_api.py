"""
Password Management API Endpoints
Handles password setup and reset flows
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from core.database import AsyncSessionLocal
from auth_workaround import User, get_current_user, pwd_context
from models_password_reset import PasswordResetToken
from modules.core_auth.utils import is_strong_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/password", tags=["Password Management"])


# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Schemas
class PasswordSetupRequest(BaseModel):
    token: str
    password: str
    password_confirm: str


class PasswordResetInitiateRequest(BaseModel):
    user_id: str


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


# Helper function to send email (placeholder - integrate with your email service)
async def send_password_setup_email(user_email: str, token: str, base_url: str):
    """
    Send password setup email to user

    TODO: Integrate with actual email service (SendGrid, AWS SES, etc.)
    For now, just log the link
    """
    setup_link = f"{base_url}/setup-password?token={token}"

    logger.info(f"Password setup link for {user_email}: {setup_link}")
    logger.info("=" * 80)
    logger.info(f"SETUP LINK: {setup_link}")
    logger.info("=" * 80)

    # TODO: Replace with actual email sending
    # email_service.send(
    #     to=user_email,
    #     subject="Set Up Your Password - KRC Gaming Center",
    #     template="password_setup",
    #     data={"setup_link": setup_link, "expires_hours": 24}
    # )


async def send_password_reset_email(user_email: str, token: str, base_url: str):
    """
    Send password reset email to user

    TODO: Integrate with actual email service
    """
    reset_link = f"{base_url}/setup-password?token={token}"

    logger.info(f"Password reset link for {user_email}: {reset_link}")
    logger.info("=" * 80)
    logger.info(f"RESET LINK: {reset_link}")
    logger.info("=" * 80)

    # TODO: Replace with actual email sending
    # email_service.send(
    #     to=user_email,
    #     subject="Reset Your Password - KRC Gaming Center",
    #     template="password_reset",
    #     data={"reset_link": reset_link, "expires_hours": 24}
    # )


# Routes
@router.post("/setup", response_model=MessageResponse)
async def setup_password(
    request: PasswordSetupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Set up password using setup token (for new users)

    This endpoint is called when a new user clicks the setup link in their email.
    No authentication required - token provides authorization.
    """
    # Validate passwords match
    if request.password != request.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Validate password strength
    is_strong, message = is_strong_password(request.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Find and validate token
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == request.token)
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )

    if not token.is_valid():
        if token.used_at:
            detail = "This password setup link has already been used"
        else:
            detail = "This password setup link has expired. Please contact your administrator for a new link."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

    # Get user
    user_result = await db.execute(
        select(User).where(User.id == token.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user password
    user.password_hash = pwd_context.hash(request.password)
    user.password_setup_required = False
    user.last_password_change = datetime.utcnow()
    user.is_active = True  # Activate user on password setup

    # Mark token as used
    token.mark_used()

    await db.commit()

    logger.info(f"Password successfully set up for user: {user.username or user.email}")

    return MessageResponse(
        message="Password set up successfully",
        detail="You can now login with your new password"
    )


@router.post("/initiate-reset", response_model=MessageResponse)
async def initiate_password_reset(
    request: PasswordResetInitiateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate password reset for a user (admin only)

    Creates a reset token and sends email to user.
    Only admins can reset passwords for staff.
    """
    # Check if current user is admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset passwords"
        )

    # Get target user
    result = await db.execute(
        select(User).where(User.id == request.user_id)
    )
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-password-reset (should use change password instead)
    if str(target_user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reset your own password. Use change password instead."
        )

    # Create reset token
    reset_token = PasswordResetToken.create_reset_token(
        user_id=target_user.id,
        created_by=current_user.id
    )
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)

    # Send email (use admin hostname from env)
    # TODO: Get base_url from settings
    base_url = "https://krc.bakersfieldesports.com"  # or from settings
    await send_password_reset_email(target_user.email, reset_token.token, base_url)

    logger.info(f"Password reset initiated by admin {current_user.username} for user {target_user.username or target_user.email}")

    return MessageResponse(
        message=f"Password reset email sent to {target_user.email}",
        detail="The user will receive an email with a password reset link valid for 24 hours"
    )


@router.get("/validate-token/{token}")
async def validate_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate a password setup/reset token

    Returns token info if valid, error if invalid/expired/used
    Used by frontend to check token before showing password form
    """
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    token_obj = result.scalar_one_or_none()

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token"
        )

    if not token_obj.is_valid():
        if token_obj.used_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This link has already been used"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This link has expired"
            )

    # Get user info
    user_result = await db.execute(
        select(User).where(User.id == token_obj.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "valid": True,
        "token_type": token_obj.token_type,
        "user_email": user.email,
        "expires_at": token_obj.expires_at.isoformat()
    }
