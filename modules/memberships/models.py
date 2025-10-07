from sqlalchemy import Column, Integer, String, DateTime, Date, Text, Boolean, ForeignKey, func as sql_func
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from datetime import datetime, date
from core.database import Base


class Membership(Base):
    """Membership model for client subscriptions"""
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

    # Relationships
    client = relationship("Client", back_populates="memberships")

    @validates('ends_on')
    def validate_end_date(self, key, ends_on):
        """Validate that end date is after start date"""
        if hasattr(self, 'starts_on') and self.starts_on and ends_on:
            if ends_on <= self.starts_on:
                raise ValueError("Membership end date must be after start date")
        return ends_on

    @hybrid_property
    def status(self) -> str:
        """Calculate membership status based on dates"""
        today = date.today()

        if today < self.starts_on:
            return "pending"
        elif today > self.ends_on:
            return "expired"
        else:
            return "active"

    @status.expression
    def status(cls):
        """SQL expression for status calculation"""
        today = func.current_date()
        return sql_func.case(
            (today < cls.starts_on, "pending"),
            (today > cls.ends_on, "expired"),
            else_="active"
        )

    @property
    def is_active(self) -> bool:
        """Check if membership is currently active"""
        return self.status == "active"

    @property
    def is_expired(self) -> bool:
        """Check if membership is expired"""
        return self.status == "expired"

    @property
    def is_pending(self) -> bool:
        """Check if membership is pending"""
        return self.status == "pending"

    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in membership"""
        if self.is_expired:
            return 0
        today = date.today()
        if today < self.starts_on:
            return (self.ends_on - self.starts_on).days
        return (self.ends_on - today).days

    @property
    def is_expiring_soon(self, days: int = 30) -> bool:
        """Check if membership is expiring within specified days"""
        if self.is_expired or self.is_pending:
            return False
        return self.days_remaining <= days

    def __repr__(self):
        return f"<Membership(client_id='{self.client_id}', plan='{self.plan_code}', status='{self.status}')>"


# Common membership plan codes that can be referenced
MEMBERSHIP_PLANS = {
    "unlimited": "Unlimited Gaming",
    "10_hours": "10 Hour Package",
    "20_hours": "20 Hour Package",
    "day_pass": "Day Pass",
    "student": "Student Discount",
    "tournament": "Tournament Entry"
}