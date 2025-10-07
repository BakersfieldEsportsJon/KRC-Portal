from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from core.database import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="staff")  # admin, staff
    mfa_secret = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"

    @property
    def is_staff(self) -> bool:
        """Check if user is staff"""
        return self.role in ["admin", "staff"]