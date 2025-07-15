from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Question(BaseModel):
    """Individual questions with types and validation"""
    
    __tablename__ = "questions"
    
    text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # text, multiple_choice, scale, file_upload
    is_required = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, nullable=False)
    options = Column(JSON)  # For multiple choice options, scale ranges, etc.
    validation_rules = Column(JSON)  # For text length, file size limits, etc.
    
    # Foreign keys
    questionnaire_id = Column(ForeignKey("questionnaires.id"), nullable=False)
    
    # Relationships
    questionnaire = relationship("Questionnaire", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type='{self.question_type}')>"