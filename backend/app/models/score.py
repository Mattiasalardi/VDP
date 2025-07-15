from sqlalchemy import Column, String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Score(Base, BaseModel):
    """Detailed scoring breakdown for applications"""
    
    __tablename__ = "scores"
    
    category = Column(String(255), nullable=False)  # e.g., "team_structure", "market_opportunity"
    score_value = Column(Float, nullable=False)  # 1-10 scale
    justification = Column(Text, nullable=False)  # AI-generated reasoning
    confidence = Column(Float)  # AI confidence in score (0-1)
    is_overridden = Column(Boolean, default=False, nullable=False)  # Manual override flag
    original_score = Column(Float)  # Original AI score before override
    
    # Foreign keys
    application_id = Column(ForeignKey("applications.id"), nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="scores")
    
    def __repr__(self):
        return f"<Score(id={self.id}, category='{self.category}', score={self.score_value})>"