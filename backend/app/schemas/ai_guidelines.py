"""
Pydantic schemas for AI guidelines API endpoints.
Handles request/response validation for guidelines generation and management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Base schemas for guidelines structure
class ScoringGuide(BaseModel):
    """Scoring guide for a guidelines category."""
    range_1_3: str = Field(..., alias="1-3", description="Description for scores 1-3")
    range_4_5: str = Field(..., alias="4-5", description="Description for scores 4-5") 
    range_6_7: str = Field(..., alias="6-7", description="Description for scores 6-7")
    range_8_10: str = Field(..., alias="8-10", description="Description for scores 8-10")
    
    class Config:
        populate_by_name = True

class GuidelineCategory(BaseModel):
    """Individual guideline category with scoring criteria."""
    section: str = Field(..., description="Section identifier (e.g., 'problem_solution_fit')")
    name: str = Field(..., description="Human-readable category name")
    weight: int = Field(..., ge=1, le=10, description="Importance weight (1-10)")
    criteria: List[str] = Field(..., min_items=1, description="List of evaluation criteria")
    red_flags: List[str] = Field(..., min_items=1, description="List of warning signs")
    scoring_guide: ScoringGuide = Field(..., description="Scoring guidance for 1-10 scale")

class GeneratedGuidelines(BaseModel):
    """Complete set of generated guidelines."""
    categories: List[GuidelineCategory] = Field(..., min_items=1, description="Guidelines categories")
    
    @validator('categories')
    def validate_categories(cls, v):
        """Validate guidelines categories."""
        if len(v) == 0:
            raise ValueError("At least one category is required")
        
        # Check for duplicate sections
        sections = [cat.section for cat in v]
        if len(sections) != len(set(sections)):
            raise ValueError("Duplicate category sections found")
        
        return v

# Request schemas
class GenerateGuidelinesRequest(BaseModel):
    """Request to generate AI guidelines from calibration data."""
    calibration_data: Dict[str, Any] = Field(..., description="Calibration responses")
    model: Optional[str] = Field(
        default="claude-3.5-sonnet",
        description="AI model to use for generation"
    )
    
    @validator('model')
    def validate_model(cls, v):
        """Validate AI model selection."""
        supported_models = [
            "claude-3.5-sonnet", "claude-3-opus", "claude-3-haiku",
            "gpt-4o", "gpt-4o-mini"
        ]
        if v and v not in supported_models:
            raise ValueError(f"Unsupported model. Supported models: {supported_models}")
        return v

class SaveGuidelinesRequest(BaseModel):
    """Request to save generated guidelines."""
    guidelines: GeneratedGuidelines = Field(..., description="Generated guidelines to save")
    is_active: bool = Field(default=False, description="Whether to activate immediately")
    notes: Optional[str] = Field(default=None, description="Optional notes about the guidelines")

class UpdateGuidelinesRequest(BaseModel):
    """Request to update existing guidelines."""
    guidelines: GeneratedGuidelines = Field(..., description="Updated guidelines")
    notes: Optional[str] = Field(default=None, description="Optional notes about the update")

class ActivateGuidelinesRequest(BaseModel):
    """Request to activate specific guidelines version."""
    version: int = Field(..., ge=1, description="Version number to activate")

# Response schemas  
class GuidelinesGenerationResponse(BaseModel):
    """Response for guidelines generation."""
    success: bool = Field(..., description="Whether generation was successful")
    guidelines: Optional[GeneratedGuidelines] = Field(default=None, description="Generated guidelines")
    model_used: Optional[str] = Field(default=None, description="AI model that was used")
    cached: bool = Field(default=False, description="Whether result was from cache")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class SavedGuidelines(BaseModel):
    """Saved guidelines with metadata."""
    id: int = Field(..., description="Guidelines ID")
    program_id: int = Field(..., description="Associated program ID")
    guidelines: GeneratedGuidelines = Field(..., description="Guidelines content")
    version: int = Field(..., description="Version number")
    is_active: bool = Field(..., description="Whether currently active")
    notes: Optional[str] = Field(default=None, description="Optional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class GuidelinesSaveResponse(BaseModel):
    """Response for saving guidelines."""
    success: bool = Field(..., description="Whether save was successful")
    guidelines: Optional[SavedGuidelines] = Field(default=None, description="Saved guidelines")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class GuidelinesListResponse(BaseModel):
    """Response for listing guidelines."""
    success: bool = Field(..., description="Whether request was successful")
    guidelines: List[SavedGuidelines] = Field(..., description="List of saved guidelines")
    active_version: Optional[int] = Field(default=None, description="Currently active version")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class GuidelinesActivationResponse(BaseModel):
    """Response for guidelines activation."""
    success: bool = Field(..., description="Whether activation was successful")
    activated_version: Optional[int] = Field(default=None, description="Activated version number")
    error: Optional[str] = Field(default=None, description="Error message if failed")

# Stats and status schemas
class GuidelinesCacheStats(BaseModel):
    """Cache statistics."""
    total_entries: int = Field(..., description="Total cache entries")
    valid_entries: int = Field(..., description="Valid (non-expired) entries")
    expired_entries: int = Field(..., description="Expired entries")

class GuidelinesStatusResponse(BaseModel):
    """Overall guidelines system status."""
    success: bool = Field(..., description="Whether status check was successful")
    has_active_guidelines: bool = Field(..., description="Whether program has active guidelines")
    active_version: Optional[int] = Field(default=None, description="Active version number")
    total_versions: int = Field(..., description="Total saved versions")
    cache_stats: GuidelinesCacheStats = Field(..., description="Cache statistics")
    error: Optional[str] = Field(default=None, description="Error message if failed")

# Database model conversion schemas
class AIGuidelineDB(BaseModel):
    """Database representation of AI guidelines."""
    id: int
    program_id: int
    section: str
    weight: int
    criteria: Dict[str, Any]
    prompt_template: Optional[str]
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True