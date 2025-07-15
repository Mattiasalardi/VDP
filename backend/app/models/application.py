from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Application(Base, BaseModel):
    """Startup applications with unique IDs"""
    
    __tablename__ = "applications"
    
    unique_id = Column(String(255), nullable=False, unique=True, index=True)  # Non-guessable URL ID
    startup_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    is_submitted = Column(Boolean, default=False, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    submitted_at = Column(DateTime)
    processed_at = Column(DateTime)
    
    # Foreign keys
    program_id = Column(ForeignKey("programs.id"), nullable=False)
    questionnaire_id = Column(ForeignKey("questionnaires.id"), nullable=False)
    
    # Relationships
    program = relationship("Program", back_populates="applications")
    questionnaire = relationship("Questionnaire", back_populates="applications")
    responses = relationship("Response", back_populates="application", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="application", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="application", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Application(id={self.id}, startup_name='{self.startup_name}')>"