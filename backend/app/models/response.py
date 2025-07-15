from sqlalchemy import Column, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Response(BaseModel):
    """Answers to questionnaire questions"""
    
    __tablename__ = "responses"
    
    response_value = Column(JSON, nullable=False)  # Flexible storage for different answer types
    response_text = Column(Text)  # Human-readable version for text responses
    
    # Foreign keys
    application_id = Column(ForeignKey("applications.id"), nullable=False)
    question_id = Column(ForeignKey("questions.id"), nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(id={self.id}, application_id={self.application_id})>"