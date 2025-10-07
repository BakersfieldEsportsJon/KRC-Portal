from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


# Association table for many-to-many relationship between clients and tags
client_tags = Table(
    'client_tags',
    Base.metadata,
    Column('client_id', UUID(as_uuid=True), ForeignKey('clients.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
    extend_existing=True
)


class Client(Base):
    """Client model for customer information"""
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    external_ids = Column(JSONB, default=dict, nullable=False)  # Store external system IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contact_methods = relationship("ContactMethod", back_populates="client", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="client", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=client_tags, back_populates="clients")
    memberships = relationship("Membership", back_populates="client", cascade="all, delete-orphan")
    check_ins = relationship("CheckIn", back_populates="client", cascade="all, delete-orphan")
    ggleap_links = relationship("GgleapLink", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(name='{self.first_name} {self.last_name}', email='{self.email}')>"

    @property
    def full_name(self) -> str:
        """Get client's full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_phone(self) -> str:
        """Get formatted phone number for display"""
        if not self.phone:
            return ""
        # Basic phone formatting
        phone = self.phone.replace("+1", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        return self.phone


class ContactMethod(Base):
    """Contact methods for clients (SMS, email, Discord, etc.)"""
    __tablename__ = "contact_methods"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    type = Column(String(20), nullable=False)  # sms, email, discord
    value = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("Client", back_populates="contact_methods")

    def __repr__(self):
        return f"<ContactMethod(type='{self.type}', value='{self.value}')>"


class Consent(Base):
    """Client consents for various purposes"""
    __tablename__ = "consents"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    kind = Column(String(20), nullable=False)  # sms, email, photo, tos, waiver
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(50), nullable=True)  # Where consent was granted
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("Client", back_populates="consents")

    def __repr__(self):
        return f"<Consent(kind='{self.kind}', granted={self.granted})>"


class Tag(Base):
    """Tags for categorizing clients"""
    __tablename__ = "tags"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    clients = relationship("Client", secondary=client_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"