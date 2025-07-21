"""
Pydantic schemas for Program management API endpoints.
Handles request/response validation for program CRUD operations.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Base program schemas
class ProgramBase(BaseModel):
    """Base program model with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Program name")
    description: Optional[str] = Field(default=None, max_length=2000, description="Program description")
    is_active: bool = Field(default=True, description="Whether program is active")

    @validator('name')
    def validate_name(cls, v):
        """Validate program name."""
        if not v or not v.strip():
            raise ValueError("Program name cannot be empty")
        return v.strip()

# Request schemas
class ProgramCreate(ProgramBase):
    """Schema for creating a new program."""
    pass

class ProgramUpdate(BaseModel):
    """Schema for updating an existing program."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Program name")
    description: Optional[str] = Field(default=None, max_length=2000, description="Program description")
    is_active: Optional[bool] = Field(default=None, description="Whether program is active")

    @validator('name')
    def validate_name(cls, v):
        """Validate program name if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError("Program name cannot be empty")
        return v.strip() if v else v

# Response schemas
class Program(ProgramBase):
    """Complete program model for responses."""
    id: int = Field(..., description="Program ID")
    organization_id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class ProgramWithStats(Program):
    """Program with additional statistics."""
    questionnaire_count: int = Field(default=0, description="Number of questionnaires")
    calibration_completion: float = Field(default=0.0, description="Calibration completion percentage")
    has_active_guidelines: bool = Field(default=False, description="Whether program has active AI guidelines")
    application_count: int = Field(default=0, description="Number of applications received")

# List response schemas
class ProgramListResponse(BaseModel):
    """Response for program list endpoint."""
    success: bool = Field(..., description="Whether request was successful")
    programs: List[ProgramWithStats] = Field(..., description="List of programs")
    total_count: int = Field(..., description="Total number of programs")
    error: Optional[str] = Field(default=None, description="Error message if failed")

# Single program response schemas
class ProgramResponse(BaseModel):
    """Response for single program operations."""
    success: bool = Field(..., description="Whether operation was successful")
    program: Optional[Program] = Field(default=None, description="Program data")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class ProgramDetailsResponse(BaseModel):
    """Response for detailed program information."""
    success: bool = Field(..., description="Whether request was successful")
    program: Optional[ProgramWithStats] = Field(default=None, description="Program with statistics")
    error: Optional[str] = Field(default=None, description="Error message if failed")

# Program context schemas
class ProgramContext(BaseModel):
    """Program context for navigation and UI."""
    id: int = Field(..., description="Program ID")
    name: str = Field(..., description="Program name")
    organization_id: int = Field(..., description="Organization ID")
    is_active: bool = Field(..., description="Whether program is active")

class ProgramSummary(BaseModel):
    """Summary information about a program."""
    program: Program = Field(..., description="Program information")
    questionnaires: int = Field(..., description="Number of questionnaires")
    calibration_complete: bool = Field(..., description="Whether calibration is complete")
    guidelines_active: bool = Field(..., description="Whether guidelines are active")
    applications: int = Field(..., description="Number of applications")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")

# Database model conversion schemas  
class ProgramDB(BaseModel):
    """Database representation of program."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True