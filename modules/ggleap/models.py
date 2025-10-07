from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from core.database import Base


class GgleapGroupType(str, enum.Enum):
    """ggLeap group type mapping"""
    ACTIVE = "active"
    EXPIRED = "expired"


class GgleapLink(Base):
    """Links between CRM clients and ggLeap users"""
    __tablename__ = "ggleap_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    ggleap_user_id = Column(String(100), nullable=False, index=True)
    linked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("Client", back_populates="ggleap_links")

    def __repr__(self):
        return f"<GgleapLink(client_id='{self.client_id}', ggleap_user_id='{self.ggleap_user_id}')>"


class GgleapGroup(Base):
    """ggLeap group configuration mapping"""
    __tablename__ = "ggleap_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    map_key = Column(Enum(GgleapGroupType), nullable=False, unique=True)
    ggleap_group_id = Column(String(100), nullable=False)
    group_name = Column(String(200), nullable=True)  # Human readable name
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<GgleapGroup(map_key='{self.map_key.value}', group_id='{self.ggleap_group_id}')>"

    @property
    def is_active_group(self) -> bool:
        """Check if this is the active members group"""
        return self.map_key == GgleapGroupType.ACTIVE

    @property
    def is_expired_group(self) -> bool:
        """Check if this is the expired members group"""
        return self.map_key == GgleapGroupType.EXPIRED