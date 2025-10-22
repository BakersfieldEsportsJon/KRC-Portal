"""
Central models file to avoid ORM conflicts
All models defined in one place so SQLAlchemy doesn't get confused
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, ForeignKey, Table, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from core.database import Base


# Association table for many-to-many relationship between clients and tags
client_tags = Table(
    'client_tags',
    Base.metadata,
    Column('client_id', UUID(as_uuid=True), ForeignKey('clients.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)


# User model (used to be in auth_workaround.py but moved here to avoid ORM issues)
class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="staff")
    mfa_secret = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    dark_mode = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class Client(Base):
    """Client model"""
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)

    # POS/Service fields
    parent_guardian_name = Column(String(200), nullable=True)
    pos_number = Column(String(50), nullable=True, index=True)
    service_coordinator = Column(String(200), nullable=True)
    pos_start_date = Column(Date, nullable=True)
    pos_end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)

    external_ids = Column(JSONB, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (will be set up after all models are defined)
    contact_methods = relationship("ContactMethod", back_populates="client", lazy="selectin")
    consents = relationship("Consent", back_populates="client", lazy="selectin")
    tags = relationship("Tag", secondary=client_tags, back_populates="clients", lazy="selectin")
    memberships = relationship("Membership", back_populates="client", lazy="selectin")
    check_ins = relationship("CheckIn", back_populates="client", lazy="selectin")
    client_notes = relationship("ClientNote", back_populates="client", lazy="selectin", order_by="ClientNote.created_at.desc()")


class ContactMethod(Base):
    """Contact methods for clients"""
    __tablename__ = "contact_methods"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    type = Column(String(20), nullable=False)
    value = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="contact_methods")


class Consent(Base):
    """Client consents"""
    __tablename__ = "consents"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    kind = Column(String(20), nullable=False)
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="consents")


class Tag(Base):
    """Tags for categorizing clients"""
    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    clients = relationship("Client", secondary=client_tags, back_populates="tags")


class Membership(Base):
    """Membership model"""
    __tablename__ = "memberships"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    plan_code = Column(String(50), nullable=False, index=True)
    starts_on = Column(Date, nullable=False)
    ends_on = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client = relationship("Client", back_populates="memberships")


class CheckInMethod(str, enum.Enum):
    """Check-in method enumeration"""
    KIOSK = "kiosk"
    STAFF = "staff"


class CheckIn(Base):
    """Check-in model"""
    __tablename__ = "check_ins"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    method = Column(Enum(CheckInMethod), nullable=False, default=CheckInMethod.STAFF)
    station = Column(String(100), nullable=True)
    happened_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client = relationship("Client", back_populates="check_ins")


class ClientNote(Base):
    """Client notes model for timestamped notes by staff"""
    __tablename__ = "client_notes"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    client = relationship("Client", back_populates="client_notes")
    user = relationship("User")
