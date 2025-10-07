from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from core.database import Base


class WebhookStatus(str, enum.Enum):
    """Webhook status enumeration"""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class WebhookOut(Base):
    """Outbound webhook tracking for Zapier integration"""
    __tablename__ = "webhooks_out"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    status = Column(Enum(WebhookStatus), nullable=False, default=WebhookStatus.QUEUED, index=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    zap_run_id = Column(String(100), nullable=True)  # Zapier run ID for tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<WebhookOut(event='{self.event}', status='{self.status.value}', attempts={self.attempt_count})>"

    @property
    def is_failed(self) -> bool:
        """Check if webhook has permanently failed"""
        return self.status == WebhookStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """Check if webhook is pending send"""
        return self.status == WebhookStatus.QUEUED

    @property
    def is_sent(self) -> bool:
        """Check if webhook was successfully sent"""
        return self.status == WebhookStatus.SENT

    @property
    def max_attempts_reached(self, max_attempts: int = 3) -> bool:
        """Check if maximum retry attempts have been reached"""
        return self.attempt_count >= max_attempts