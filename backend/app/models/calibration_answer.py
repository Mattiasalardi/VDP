from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class CalibrationAnswer(Base, BaseModel):
    """Accelerator preferences and calibration responses"""
    
    __tablename__ = "calibration_answers"
    
    question_key = Column(String(255), nullable=False)  # e.g., "team_importance", "market_size_preference"
    answer_value = Column(JSON, nullable=False)  # Flexible storage for various answer types
    answer_text = Column(Text)  # Human-readable version of the answer
    
    # Foreign keys
    program_id = Column(ForeignKey("programs.id"), nullable=False)
    
    # Relationships
    program = relationship("Program", back_populates="calibration_answers")
    
    def __repr__(self):
        return f"<CalibrationAnswer(id={self.id}, question_key='{self.question_key}')>"