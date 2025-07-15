from sqlalchemy import Column, String, Text, ForeignKey, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base, BaseModel

class Report(Base, BaseModel):
    """Generated PDF reports with scores and analysis"""
    
    __tablename__ = "reports"
    
    overall_score = Column(Float, nullable=False)  # 1-10 scale
    overall_summary = Column(Text, nullable=False)
    
    # 10 report sections with scores and content
    problem_solution_score = Column(Float, nullable=False)
    problem_solution_content = Column(Text, nullable=False)
    
    customer_profile_score = Column(Float, nullable=False)
    customer_profile_content = Column(Text, nullable=False)
    
    product_technology_score = Column(Float, nullable=False)
    product_technology_content = Column(Text, nullable=False)
    
    team_structure_score = Column(Float, nullable=False)
    team_structure_content = Column(Text, nullable=False)
    
    market_opportunity_score = Column(Float, nullable=False)
    market_opportunity_content = Column(Text, nullable=False)
    
    financial_overview_score = Column(Float, nullable=False)
    financial_overview_content = Column(Text, nullable=False)
    
    key_challenges_score = Column(Float, nullable=False)
    key_challenges_content = Column(Text, nullable=False)
    
    validation_achievements_score = Column(Float, nullable=False)
    validation_achievements_content = Column(Text, nullable=False)
    
    investigation_areas_score = Column(Float, nullable=False)
    investigation_areas_content = Column(Text, nullable=False)
    
    # PDF generation
    pdf_file_path = Column(String(500))  # Path to generated PDF
    pdf_generated_at = Column(DateTime)
    generation_status = Column(String(50), default="pending")  # pending, completed, failed
    
    # Version tracking
    version = Column(Integer, default=1, nullable=False)
    is_latest = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    application_id = Column(ForeignKey("applications.id"), nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, overall_score={self.overall_score})>"