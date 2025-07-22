from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class QuestionnaireBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the questionnaire")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the questionnaire")
    is_active: bool = Field(default=True, description="Whether the questionnaire is active")


class QuestionnaireCreate(QuestionnaireBase):
    pass


class QuestionnaireUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class QuestionnaireResponse(QuestionnaireBase):
    id: int
    program_id: int
    created_at: datetime
    updated_at: datetime
    question_count: int = Field(default=0, description="Number of questions in this questionnaire")

    class Config:
        from_attributes = True


class QuestionnaireListResponse(BaseModel):
    questionnaires: List[QuestionnaireResponse]
    total_count: int


class QuestionnaireDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    program_id: int
    created_at: datetime
    updated_at: datetime
    question_count: int = Field(default=0, description="Number of questions in this questionnaire")
    questions: List = Field(default_factory=list, description="List of questions in this questionnaire")

    class Config:
        from_attributes = True