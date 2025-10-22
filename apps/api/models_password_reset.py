"""
Password Reset Token Model
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import secrets

from core.database import Base


class PasswordResetToken(Base):
    """Password reset/setup token model"""
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), nullable=False, unique=True, index=True)
    token_type = Column(String(20), nullable=False)  # 'setup' or 'reset'
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    # Note: back_populates removed because UserWorkaround doesn't define password_tokens relationship
    user = relationship("User", foreign_keys=[user_id])
    created_by_user = relationship("User", foreign_keys=[created_by])

    @staticmethod
    def generate_token() -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(32)

    @classmethod
    def create_setup_token(cls, user_id: uuid.UUID, expires_in_hours: int = 24):
        """Create a new password setup token"""
        return cls(
            user_id=user_id,
            token=cls.generate_token(),
            token_type='setup',
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )

    @classmethod
    def create_reset_token(cls, user_id: uuid.UUID, created_by: uuid.UUID, expires_in_hours: int = 24):
        """Create a new password reset token"""
        return cls(
            user_id=user_id,
            token=cls.generate_token(),
            token_type='reset',
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            created_by=created_by
        )

    def is_valid(self) -> bool:
        """Check if token is valid (not used and not expired)"""
        return (
            self.used_at is None and
            self.expires_at > datetime.utcnow()
        )

    def mark_used(self):
        """Mark token as used"""
        self.used_at = datetime.utcnow()
