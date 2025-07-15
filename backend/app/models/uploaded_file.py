from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class UploadedFile(BaseModel):
    """PDF document references and metadata"""
    
    __tablename__ = "uploaded_files"
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    extracted_text = Column(Text)  # Extracted PDF text content
    extraction_status = Column(String(50), default="pending")  # pending, completed, failed
    
    # Foreign keys
    application_id = Column(ForeignKey("applications.id"), nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="uploaded_files")
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename='{self.filename}')>"