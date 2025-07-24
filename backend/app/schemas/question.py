from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration"""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    FILE_UPLOAD = "file_upload"


class TextQuestionOptions(BaseModel):
    """Options for text questions"""
    max_length: Optional[int] = Field(None, ge=1, le=10000)
    min_length: Optional[int] = Field(None, ge=0)
    placeholder: Optional[str] = None
    multiline: bool = False


class MultipleChoiceQuestionOptions(BaseModel):
    """Options for multiple choice questions"""
    choices: List[str] = Field(..., min_items=2, max_items=20)
    allow_multiple: bool = False
    randomize_order: bool = False


class ScaleQuestionOptions(BaseModel):
    """Options for scale questions"""
    min_value: int = Field(1, ge=1, le=10)
    max_value: int = Field(10, ge=1, le=10)
    step: int = Field(1, ge=1)
    min_label: Optional[str] = None
    max_label: Optional[str] = None


class FileUploadQuestionOptions(BaseModel):
    """Options for file upload questions"""
    max_file_size_mb: int = Field(50, ge=1, le=100)
    allowed_extensions: List[str] = Field(default_factory=lambda: [".pdf"])
    max_files: int = Field(1, ge=1, le=5)


class QuestionValidationRules(BaseModel):
    """Validation rules for questions"""
    required: bool = True
    custom_error_message: Optional[str] = None


class QuestionBase(BaseModel):
    """Base question schema"""
    text: str = Field(..., min_length=1, max_length=1000)
    question_type: QuestionType
    is_required: bool = True
    order_index: int = Field(..., ge=0)
    options: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None



class QuestionCreate(QuestionBase):
    """Schema for creating a question"""
    questionnaire_id: Optional[int] = Field(None, gt=0)  # Optional since it comes from URL path


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""
    text: Optional[str] = Field(None, min_length=1, max_length=1000)
    question_type: Optional[QuestionType] = None
    is_required: Optional[bool] = None
    order_index: Optional[int] = Field(None, ge=0)
    options: Optional[Union[
        TextQuestionOptions,
        MultipleChoiceQuestionOptions,
        ScaleQuestionOptions,
        FileUploadQuestionOptions
    ]] = None
    validation_rules: Optional[QuestionValidationRules] = None

    @validator('options')
    def validate_options_match_type(cls, v, values):
        """Validate that options match the question type if both are provided"""
        if v is None or 'question_type' not in values or values['question_type'] is None:
            return v
        
        question_type = values['question_type']
        
        type_option_map = {
            QuestionType.TEXT: TextQuestionOptions,
            QuestionType.MULTIPLE_CHOICE: MultipleChoiceQuestionOptions,
            QuestionType.SCALE: ScaleQuestionOptions,
            QuestionType.FILE_UPLOAD: FileUploadQuestionOptions
        }
        
        if not isinstance(v, type_option_map[question_type]):
            raise ValueError(f"Invalid options type for {question_type} question")
        
        return v


class QuestionResponse(QuestionBase):
    """Schema for question responses"""
    id: int
    questionnaire_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for question list responses"""
    questions: List[QuestionResponse]
    total: int
    questionnaire_id: int


class QuestionReorderRequest(BaseModel):
    """Schema for reordering questions"""
    question_order: List[int] = Field(..., min_items=1)

    @validator('question_order')
    def validate_unique_ids(cls, v):
        """Ensure all question IDs are unique"""
        if len(v) != len(set(v)):
            raise ValueError("Question IDs must be unique")
        return v