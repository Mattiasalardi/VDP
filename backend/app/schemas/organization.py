from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    description: Optional[str] = None
    website: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    password: str = Field(..., min_length=6, max_length=100)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    website: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationLogin(BaseModel):
    """Schema for organization login"""
    email: EmailStr
    password: str