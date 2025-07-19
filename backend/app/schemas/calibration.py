from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class CalibrationQuestionType(str, Enum):
    """Types of calibration questions"""
    SCALE = "scale"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"

class CalibrationAnswerBase(BaseModel):
    """Base calibration answer schema"""
    question_key: str = Field(..., min_length=1, max_length=255)
    answer_value: Dict[str, Any] = Field(..., description="Flexible storage for answer data")
    answer_text: Optional[str] = Field(None, description="Human-readable answer description")

class CalibrationAnswerCreate(CalibrationAnswerBase):
    """Schema for creating calibration answers"""
    pass

class CalibrationAnswerUpdate(BaseModel):
    """Schema for updating calibration answers"""
    answer_value: Optional[Dict[str, Any]] = None
    answer_text: Optional[str] = None

class CalibrationAnswerResponse(CalibrationAnswerBase):
    """Schema for calibration answer responses"""
    id: int
    program_id: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class CalibrationQuestionOption(BaseModel):
    """Option for multiple choice calibration questions"""
    value: str
    label: str

class CalibrationQuestionScaleLabels(BaseModel):
    """Scale labels for scale questions"""
    min_label: Optional[str] = None
    max_label: Optional[str] = None
    scale_labels: Optional[Dict[int, str]] = None

class CalibrationQuestion(BaseModel):
    """Complete calibration question with metadata"""
    key: str
    question: str
    type: CalibrationQuestionType
    description: str
    
    # Scale question fields
    scale_min: Optional[int] = Field(None, ge=1)
    scale_max: Optional[int] = Field(None, le=10)
    scale_labels: Optional[Dict[int, str]] = None
    
    # Multiple choice fields
    options: Optional[List[CalibrationQuestionOption]] = None
    
    # Text question fields
    placeholder: Optional[str] = None
    max_length: Optional[int] = Field(None, gt=0)

class CalibrationCategory(BaseModel):
    """Category of calibration questions"""
    title: str
    description: str
    questions: List[str]  # Question keys

class CalibrationSessionRequest(BaseModel):
    """Request to start or update calibration session"""
    answers: List[CalibrationAnswerCreate] = Field(..., min_items=1)

class CalibrationSessionResponse(BaseModel):
    """Response for calibration session"""
    program_id: int
    total_questions: int
    answered_questions: int
    completion_percentage: float
    answers: List[CalibrationAnswerResponse]
    missing_questions: List[str]
    
    class Config:
        from_attributes = True

class CalibrationCompletionStatus(BaseModel):
    """Calibration completion status"""
    is_complete: bool
    total_questions: int
    answered_questions: int
    completion_percentage: float
    missing_questions: List[str]
    next_category: Optional[str] = None

class CalibrationQuestionsResponse(BaseModel):
    """Response containing all calibration questions organized by category"""
    categories: Dict[str, Dict[str, Any]]  # category_key -> {info, questions}
    total_questions: int

class CalibrationAnswerBatch(BaseModel):
    """Batch submission of calibration answers"""
    answers: List[CalibrationAnswerCreate] = Field(..., min_length=1, max_length=20)
    
    @field_validator('answers')
    @classmethod
    def validate_unique_questions(cls, v):
        """Ensure no duplicate question keys in batch"""
        question_keys = [answer.question_key for answer in v]
        if len(question_keys) != len(set(question_keys)):
            raise ValueError("Duplicate question keys not allowed in batch submission")
        return v