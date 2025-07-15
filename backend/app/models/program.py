from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Program(BaseModel):
    """Accelerator programs (e.g., TechEd Accelerator 2024)"""
    
    __tablename__ = "programs"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    organization_id = Column(ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="programs")
    questionnaires = relationship("Questionnaire", back_populates="program", cascade="all, delete-orphan")
    calibration_answers = relationship("CalibrationAnswer", back_populates="program", cascade="all, delete-orphan")
    ai_guidelines = relationship("AIGuideline", back_populates="program", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="program", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Program(id={self.id}, name='{self.name}')>"