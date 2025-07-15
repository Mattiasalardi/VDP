from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Questionnaire(Base, BaseModel):
    """Question sets for each program"""
    
    __tablename__ = "questionnaires"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    program_id = Column(ForeignKey("programs.id"), nullable=False)
    
    # Relationships
    program = relationship("Program", back_populates="questionnaires")
    questions = relationship("Question", back_populates="questionnaire", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="questionnaire", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Questionnaire(id={self.id}, name='{self.name}')>"