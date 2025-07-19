from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GuidelinesGenerationRequest(BaseModel):
    """Request to generate AI guidelines"""
    model: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="OpenRouter model to use for generation"
    )

class GuidelinesMetadata(BaseModel):
    """Metadata about guidelines generation"""
    program_id: int
    organization_id: int
    model: str
    generated_at: str
    calibration_questions_count: int
    rate_limit_remaining: int

class CalibrationSummary(BaseModel):
    """Summary of calibration responses used for generation"""
    total_questions_answered: int
    key_preferences: Dict[str, str]
    risk_profile: str
    stage_focus: str
    industry_focus: str

class GuidelinesGenerationResponse(BaseModel):
    """Response from guidelines generation"""
    guidelines: Dict[str, Any] = Field(..., description="Generated scoring guidelines in JSON format")
    metadata: GuidelinesMetadata
    calibration_summary: CalibrationSummary

class GuidelinesSaveRequest(BaseModel):
    """Request to save guidelines"""
    guidelines_data: Dict[str, Any] = Field(..., description="Guidelines data including metadata")
    is_approved: bool = Field(default=False, description="Whether to approve and activate these guidelines")

class GuidelinesResponse(BaseModel):
    """Response for saved guidelines"""
    id: int
    program_id: int
    guidelines: Dict[str, Any]
    version: int
    is_active: bool
    model_used: str
    created_at: str
    generated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class GuidelinesListResponse(BaseModel):
    """Response for guidelines history list"""
    guidelines: List[GuidelinesResponse]
    total_count: int

# Specific schemas for guidelines structure validation
class ScoringGuidance(BaseModel):
    """Scoring guidance for a category"""
    high_score_indicators: List[str]
    medium_score_indicators: List[str]
    low_score_indicators: List[str]
    key_questions: List[str]

class GuidelinesCategory(BaseModel):
    """Individual guidelines category"""
    name: str
    weight: float = Field(..., ge=0, le=1)
    description: str
    scoring_guidance: ScoringGuidance

class OverallApproach(BaseModel):
    """Overall evaluation approach"""
    risk_tolerance: str
    stage_focus: str
    industry_focus: str
    key_priorities: List[str]

class ScoringScale(BaseModel):
    """Scoring scale definitions"""
    range: str
    descriptions: Dict[str, str]

class GuidelinesStructure(BaseModel):
    """Complete guidelines structure"""
    categories: List[GuidelinesCategory]
    overall_approach: OverallApproach
    scoring_scale: ScoringScale
    
    def validate_weights_sum_to_one(self):
        """Validate that category weights sum to 1.0"""
        total_weight = sum(category.weight for category in self.categories)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Category weights must sum to 1.0, got {total_weight}")
        return self

class FullGuidelinesResponse(BaseModel):
    """Complete guidelines response with validation"""
    guidelines: GuidelinesStructure
    
    def __init__(self, **data):
        super().__init__(**data)
        self.guidelines.validate_weights_sum_to_one()