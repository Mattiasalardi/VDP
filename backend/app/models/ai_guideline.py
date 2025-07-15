from sqlalchemy import Column, String, Text, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class AIGuideline(Base, BaseModel):
    """Generated and user-modified AI scoring guidelines"""
    
    __tablename__ = "ai_guidelines"
    
    section = Column(String(255), nullable=False)  # e.g., "team_structure", "market_opportunity"
    weight = Column(Integer, default=1, nullable=False)  # Scoring weight (1-10)
    criteria = Column(JSON, nullable=False)  # Detailed scoring criteria
    prompt_template = Column(Text, nullable=False)  # AI prompt for this section
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)  # For versioning guidelines
    
    # Foreign keys
    program_id = Column(ForeignKey("programs.id"), nullable=False)
    
    # Relationships
    program = relationship("Program", back_populates="ai_guidelines")
    
    def __repr__(self):
        return f"<AIGuideline(id={self.id}, section='{self.section}')>"