from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from core.database import Base


class CheckInMethod(str, enum.Enum):
    """Check-in method enumeration"""
    KIOSK = "kiosk"
    STAFF = "staff"


class CheckIn(Base):
    """Check-in model for tracking client visits"""
    __tablename__ = "check_ins"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    method = Column(Enum(CheckInMethod), nullable=False, default=CheckInMethod.STAFF)
    station = Column(String(100), nullable=True)  # Gaming station or kiosk ID
    happened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("Client", back_populates="check_ins")

    def __repr__(self):
        return f"<CheckIn(client_id='{self.client_id}', method='{self.method.value}', station='{self.station}')>"

    @property
    def is_kiosk_checkin(self) -> bool:
        """Check if this was a kiosk check-in"""
        return self.method == CheckInMethod.KIOSK

    @property
    def is_staff_checkin(self) -> bool:
        """Check if this was a staff-assisted check-in"""
        return self.method == CheckInMethod.STAFF