from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


class ClientBase(BaseModel):
    """Base client schema"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    external_ids: Dict[str, Any] = Field(default_factory=dict)
    parent_guardian_name: Optional[str] = Field(None, max_length=200)
    pos_number: Optional[str] = Field(None, max_length=50)
    service_coordinator: Optional[str] = Field(None, max_length=200)
    pos_start_date: Optional[date] = None
    pos_end_date: Optional[date] = None
    notes: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)

    @validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        # Basic phone validation - remove common separators
        cleaned = v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v


class ClientCreate(ClientBase):
    """Schema for creating a client"""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    external_ids: Optional[Dict[str, Any]] = None
    parent_guardian_name: Optional[str] = Field(None, max_length=200)
    pos_number: Optional[str] = Field(None, max_length=50)
    service_coordinator: Optional[str] = Field(None, max_length=200)
    pos_start_date: Optional[date] = None
    pos_end_date: Optional[date] = None
    notes: Optional[str] = None
    language: Optional[str] = Field(None, max_length=50)

    @validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = v.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '')
        if not cleaned.isdigit() or len(cleaned) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v


class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class TagResponse(TagBase):
    """Schema for tag response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ContactMethodBase(BaseModel):
    """Base contact method schema"""
    type: str = Field(..., pattern=r'^(sms|email|discord)$')
    value: str = Field(..., min_length=1, max_length=255)
    verified: bool = Field(default=False)


class ContactMethodCreate(ContactMethodBase):
    """Schema for creating a contact method"""
    pass


class ContactMethodResponse(ContactMethodBase):
    """Schema for contact method response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ConsentBase(BaseModel):
    """Base consent schema"""
    kind: str = Field(..., pattern=r'^(sms|email|photo|tos|waiver)$')
    granted: bool
    source: Optional[str] = Field(None, max_length=50)


class ConsentCreate(ConsentBase):
    """Schema for creating a consent"""
    pass


class ConsentResponse(ConsentBase):
    """Schema for consent response"""
    id: UUID
    granted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    contact_methods: List[ContactMethodResponse] = []
    consents: List[ConsentResponse] = []

    class Config:
        from_attributes = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ClientListResponse(BaseModel):
    """Schema for client list response"""
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ClientSearchRequest(BaseModel):
    """Schema for client search request"""
    query: Optional[str] = Field(None, description="Search query for name, email, or phone")
    tags: Optional[List[str]] = Field(None, description="Filter by tag names")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class AddTagRequest(BaseModel):
    """Schema for adding tags to client"""
    tag_names: List[str] = Field(..., min_items=1, description="List of tag names to add")


class AddConsentRequest(BaseModel):
    """Schema for adding consent to client"""
    consents: List[ConsentCreate] = Field(..., min_items=1, description="List of consents to add")