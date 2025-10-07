from pydantic import BaseModel, Field, validator
from typing import Optional, Union
from datetime import datetime
from uuid import UUID
from .models import CheckInMethod


class CheckInBase(BaseModel):
    """Base check-in schema"""
    station: Optional[str] = Field(None, max_length=100, description="Gaming station or kiosk ID")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class CheckInCreate(CheckInBase):
    """Schema for creating a check-in"""
    # One of these must be provided to identify the client
    client_id: Optional[UUID] = None
    phone: Optional[str] = Field(None, description="Client phone number")
    code: Optional[str] = Field(None, description="Client lookup code")

    method: CheckInMethod = Field(default=CheckInMethod.STAFF, description="Check-in method")

    @validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        # Basic phone validation
        cleaned = v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v

    def validate_client_identifier(self):
        """Validate that at least one client identifier is provided"""
        if not any([self.client_id, self.phone, self.code]):
            raise ValueError("Must provide client_id, phone, or code to identify client")


class KioskCheckInRequest(BaseModel):
    """Schema for kiosk check-in request (simplified)"""
    phone: Optional[str] = Field(None, description="Client phone number")
    code: Optional[str] = Field(None, description="Client lookup code")
    station: Optional[str] = Field(None, max_length=100, description="Kiosk/station ID")

    @validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v

    def validate_identifier(self):
        """Validate that at least one identifier is provided"""
        if not any([self.phone, self.code]):
            raise ValueError("Must provide phone or code to check in")


class CheckInResponse(CheckInBase):
    """Schema for check-in response"""
    id: UUID
    client_id: UUID
    method: CheckInMethod
    happened_at: datetime
    created_at: datetime

    # Client information
    client_name: str
    client_email: Optional[str] = None
    client_phone: Optional[str] = None

    class Config:
        from_attributes = True


class CheckInListResponse(BaseModel):
    """Schema for check-in list response (simplified)"""
    id: UUID
    client_id: UUID
    client_name: str
    method: CheckInMethod
    station: Optional[str]
    happened_at: datetime

    class Config:
        from_attributes = True


class ClientLookupResponse(BaseModel):
    """Schema for client lookup response"""
    id: UUID
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    membership_status: Optional[str] = None
    membership_expires: Optional[str] = None

    class Config:
        from_attributes = True


class CheckInStatsResponse(BaseModel):
    """Schema for check-in statistics"""
    today: int
    this_week: int
    this_month: int
    unique_clients_today: int
    unique_clients_week: int
    unique_clients_month: int
    popular_stations: dict[str, int]

    class Config:
        from_attributes = True