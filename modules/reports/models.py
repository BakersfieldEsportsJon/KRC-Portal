from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class AuditLog(Base):
    """Audit log for tracking changes to important entities"""
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for system actions
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, etc.
    entity = Column(String(50), nullable=False, index=True)  # client, membership, etc.
    entity_id = Column(String(100), nullable=False, index=True)  # ID of the affected entity
    diff = Column(JSONB, nullable=True)  # Changes made (before/after)
    metadata = Column(JSONB, nullable=True)  # Additional context
    at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    actor = relationship("User", foreign_keys=[actor_user_id])

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', entity='{self.entity}', entity_id='{self.entity_id}')>"

    @property
    def is_system_action(self) -> bool:
        """Check if this was a system-generated action"""
        return self.actor_user_id is None

    @property
    def summary(self) -> str:
        """Get a human-readable summary of the action"""
        actor = "System" if self.is_system_action else f"User {self.actor_user_id}"
        return f"{actor} {self.action}d {self.entity} {self.entity_id}"