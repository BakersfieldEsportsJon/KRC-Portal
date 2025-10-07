from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class MembershipBase(BaseModel):
    """Base membership schema"""
    plan_code: str = Field(..., min_length=1, max_length=50)
    starts_on: date
    ends_on: date
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('ends_on')
    def validate_end_date(cls, v, values):
        if 'starts_on' in values and v <= values['starts_on']:
            raise ValueError('End date must be after start date')
        return v


class MembershipCreate(MembershipBase):
    """Schema for creating a membership"""
    client_id: UUID


class MembershipUpdate(BaseModel):
    """Schema for updating a membership"""
    plan_code: Optional[str] = Field(None, min_length=1, max_length=50)
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('ends_on')
    def validate_end_date(cls, v, values):
        if v and 'starts_on' in values and values['starts_on'] and v <= values['starts_on']:
            raise ValueError('End date must be after start date')
        return v


class MembershipResponse(MembershipBase):
    """Schema for membership response"""
    id: UUID
    client_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_expired(self) -> bool:
        return self.status == "expired"

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"


class MembershipWithClientResponse(MembershipResponse):
    """Schema for membership response with client info"""
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None

    class Config:
        from_attributes = True


class MembershipStatusUpdate(BaseModel):
    """Schema for updating membership status (internal use)"""
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None


class ExpiringMembershipsRequest(BaseModel):
    """Schema for getting expiring memberships"""
    days: int = Field(default=30, ge=1, le=365, description="Number of days to look ahead")
    plan_codes: Optional[list[str]] = Field(None, description="Filter by plan codes")


class MembershipStatsResponse(BaseModel):
    """Schema for membership statistics"""
    total_active: int
    total_expired: int
    total_pending: int
    expiring_30_days: int
    expiring_7_days: int
    plans: dict[str, int]  # Plan code -> count

    class Config:
        from_attributes = True