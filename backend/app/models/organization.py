from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Organization(Base, BaseModel):
    """Accelerator organizations"""
    
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    description = Column(Text)
    website = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    programs = relationship("Program", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"