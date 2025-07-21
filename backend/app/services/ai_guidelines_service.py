"""
AI Guidelines Service - Business logic for AI-powered guidelines generation and management.
Handles the complete workflow from calibration data to stored, versioned guidelines.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models.ai_guideline import AIGuideline
from app.models.program import Program
from app.models.calibration_answer import CalibrationAnswer
from app.schemas.ai_guidelines import (
    GeneratedGuidelines, GuidelineCategory, SavedGuidelines,
    GuidelinesGenerationResponse, GuidelinesSaveResponse,
    GuidelinesListResponse, GuidelinesActivationResponse,
    GuidelinesStatusResponse, GuidelinesCacheStats
)
from app.services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

class AIGuidelinesService:
    """Service for AI guidelines generation, storage, and management."""
    
    def __init__(self):
        """Initialize the AI Guidelines Service."""
        pass
    
    async def generate_guidelines_from_calibration(
        self,
        db: Session,
        program_id: int,
        organization_id: int,
        model: Optional[str] = None
    ) -> GuidelinesGenerationResponse:
        """
        Generate AI guidelines based on calibration data for a program.
        
        Args:
            db: Database session
            program_id: Program ID to generate guidelines for
            organization_id: Organization ID for security
            model: AI model to use (optional)
            
        Returns:
            GuidelinesGenerationResponse with generated guidelines or error
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return GuidelinesGenerationResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            # Get calibration data for the program
            calibration_answers = db.query(CalibrationAnswer).filter(
                CalibrationAnswer.program_id == program_id
            ).all()
            
            if not calibration_answers:
                return GuidelinesGenerationResponse(
                    success=False,
                    error="No calibration data found. Please complete calibration first."
                )
            
            # Convert calibration answers to dictionary
            calibration_data = {}
            for answer in calibration_answers:
                calibration_data[answer.question_key] = answer.answer_value
            
            # Generate guidelines using OpenRouter
            logger.info(f"Generating guidelines for program {program_id} with {len(calibration_data)} calibration answers")
            
            generated_data = await openrouter_service.generate_guidelines(
                calibration_data=calibration_data,
                model=model
            )
            
            # Convert to Pydantic model for validation
            guidelines = GeneratedGuidelines(**generated_data)
            
            return GuidelinesGenerationResponse(
                success=True,
                guidelines=guidelines,
                model_used=model or "claude-3.5-sonnet",
                cached=False  # TODO: Implement cache tracking
            )
            
        except Exception as e:
            logger.error(f"Guidelines generation failed for program {program_id}: {str(e)}")
            return GuidelinesGenerationResponse(
                success=False,
                error=f"Guidelines generation failed: {str(e)}"
            )
    
    def save_guidelines(
        self,
        db: Session,
        program_id: int,
        organization_id: int,
        guidelines: GeneratedGuidelines,
        is_active: bool = False,
        notes: Optional[str] = None
    ) -> GuidelinesSaveResponse:
        """
        Save generated guidelines to database with versioning.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            guidelines: Generated guidelines to save
            is_active: Whether to activate immediately
            notes: Optional notes
            
        Returns:
            GuidelinesSaveResponse with saved guidelines or error
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return GuidelinesSaveResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            # Get next version number
            latest_version = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id
            ).order_by(AIGuideline.version.desc()).first()
            
            next_version = (latest_version.version + 1) if latest_version else 1
            
            # If activating, deactivate all existing guidelines
            if is_active:
                db.query(AIGuideline).filter(
                    AIGuideline.program_id == program_id,
                    AIGuideline.is_active == True
                ).update({"is_active": False})
            
            # Save each category as a separate record
            saved_guidelines = []
            for category in guidelines.categories:
                # Convert category to database format
                criteria_json = {
                    "name": category.name,
                    "criteria": category.criteria,
                    "red_flags": category.red_flags,
                    "scoring_guide": {
                        "1-3": category.scoring_guide.range_1_3,
                        "4-5": category.scoring_guide.range_4_5,
                        "6-7": category.scoring_guide.range_6_7,
                        "8-10": category.scoring_guide.range_8_10
                    }
                }
                
                # Create database record
                guideline_record = AIGuideline(
                    program_id=program_id,
                    section=category.section,
                    weight=category.weight,
                    criteria=criteria_json,
                    prompt_template="",  # TODO: Store prompts if needed
                    is_active=is_active,
                    version=next_version
                )
                
                db.add(guideline_record)
                saved_guidelines.append(guideline_record)
            
            # Commit the transaction
            db.commit()
            
            # Refresh the records to get IDs and timestamps
            for record in saved_guidelines:
                db.refresh(record)
            
            logger.info(f"Saved guidelines version {next_version} for program {program_id} ({len(saved_guidelines)} categories)")
            
            # Convert back to response format (using first record for metadata)
            first_record = saved_guidelines[0]
            response_guidelines = SavedGuidelines(
                id=first_record.id,
                program_id=program_id,
                guidelines=guidelines,
                version=next_version,
                is_active=is_active,
                notes=notes,
                created_at=first_record.created_at,
                updated_at=first_record.updated_at
            )
            
            return GuidelinesSaveResponse(
                success=True,
                guidelines=response_guidelines
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save guidelines for program {program_id}: {str(e)}")
            return GuidelinesSaveResponse(
                success=False,
                error=f"Failed to save guidelines: {str(e)}"
            )
    
    def get_guidelines_history(
        self,
        db: Session,
        program_id: int,
        organization_id: int
    ) -> GuidelinesListResponse:
        """
        Get all versions of guidelines for a program.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            
        Returns:
            GuidelinesListResponse with guidelines history
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return GuidelinesListResponse(
                    success=False,
                    guidelines=[],
                    error="Program not found or access denied"
                )
            
            # Get all guideline versions grouped by version number
            guidelines_records = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id
            ).order_by(AIGuideline.version.desc(), AIGuideline.section).all()
            
            if not guidelines_records:
                return GuidelinesListResponse(
                    success=True,
                    guidelines=[],
                    active_version=None
                )
            
            # Group by version and convert to response format
            guidelines_by_version = {}
            active_version = None
            
            for record in guidelines_records:
                version = record.version
                
                if record.is_active and not active_version:
                    active_version = version
                
                if version not in guidelines_by_version:
                    guidelines_by_version[version] = {
                        'metadata': record,
                        'categories': []
                    }
                
                # Convert database record to category
                criteria_data = record.criteria
                category = GuidelineCategory(
                    section=record.section,
                    name=criteria_data.get("name", record.section.replace("_", " ").title()),
                    weight=record.weight,
                    criteria=criteria_data.get("criteria", []),
                    red_flags=criteria_data.get("red_flags", []),
                    scoring_guide=criteria_data.get("scoring_guide", {
                        "1-3": "Low score",
                        "4-5": "Below average", 
                        "6-7": "Above average",
                        "8-10": "High score"
                    })
                )
                
                guidelines_by_version[version]['categories'].append(category)
            
            # Convert to SavedGuidelines format
            saved_guidelines_list = []
            for version, data in guidelines_by_version.items():
                metadata = data['metadata']
                guidelines = GeneratedGuidelines(categories=data['categories'])
                
                saved_guidelines = SavedGuidelines(
                    id=metadata.id,
                    program_id=program_id,
                    guidelines=guidelines,
                    version=version,
                    is_active=metadata.is_active,
                    notes=None,  # TODO: Add notes field to database
                    created_at=metadata.created_at,
                    updated_at=metadata.updated_at
                )
                
                saved_guidelines_list.append(saved_guidelines)
            
            return GuidelinesListResponse(
                success=True,
                guidelines=saved_guidelines_list,
                active_version=active_version
            )
            
        except Exception as e:
            logger.error(f"Failed to get guidelines history for program {program_id}: {str(e)}")
            return GuidelinesListResponse(
                success=False,
                guidelines=[],
                error=f"Failed to get guidelines: {str(e)}"
            )
    
    def get_active_guidelines(
        self,
        db: Session,
        program_id: int,
        organization_id: int
    ) -> Optional[SavedGuidelines]:
        """
        Get currently active guidelines for a program.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            
        Returns:
            SavedGuidelines if found, None otherwise
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return None
            
            # Get active guidelines
            active_records = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.is_active == True
            ).order_by(AIGuideline.section).all()
            
            if not active_records:
                return None
            
            # Convert to response format
            categories = []
            for record in active_records:
                criteria_data = record.criteria
                category = GuidelineCategory(
                    section=record.section,
                    name=criteria_data.get("name", record.section.replace("_", " ").title()),
                    weight=record.weight,
                    criteria=criteria_data.get("criteria", []),
                    red_flags=criteria_data.get("red_flags", []),
                    scoring_guide=criteria_data.get("scoring_guide", {})
                )
                categories.append(category)
            
            guidelines = GeneratedGuidelines(categories=categories)
            first_record = active_records[0]
            
            return SavedGuidelines(
                id=first_record.id,
                program_id=program_id,
                guidelines=guidelines,
                version=first_record.version,
                is_active=True,
                notes=None,
                created_at=first_record.created_at,
                updated_at=first_record.updated_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get active guidelines for program {program_id}: {str(e)}")
            return None
    
    def activate_guidelines_version(
        self,
        db: Session,
        program_id: int,
        organization_id: int,
        version: int
    ) -> GuidelinesActivationResponse:
        """
        Activate a specific version of guidelines.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            version: Version number to activate
            
        Returns:
            GuidelinesActivationResponse with result
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return GuidelinesActivationResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            # Check if version exists
            version_exists = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.version == version
            ).first()
            
            if not version_exists:
                return GuidelinesActivationResponse(
                    success=False,
                    error=f"Version {version} not found"
                )
            
            # Deactivate all existing guidelines
            db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.is_active == True
            ).update({"is_active": False})
            
            # Activate the specified version
            updated_count = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.version == version
            ).update({"is_active": True})
            
            db.commit()
            
            logger.info(f"Activated guidelines version {version} for program {program_id} ({updated_count} records)")
            
            return GuidelinesActivationResponse(
                success=True,
                activated_version=version
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to activate guidelines version {version} for program {program_id}: {str(e)}")
            return GuidelinesActivationResponse(
                success=False,
                error=f"Failed to activate version: {str(e)}"
            )
    
    def get_guidelines_status(
        self,
        db: Session,
        program_id: int,
        organization_id: int
    ) -> GuidelinesStatusResponse:
        """
        Get overall status of guidelines for a program.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            
        Returns:
            GuidelinesStatusResponse with status information
        """
        try:
            # Verify program belongs to organization
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return GuidelinesStatusResponse(
                    success=False,
                    has_active_guidelines=False,
                    active_version=None,
                    total_versions=0,
                    cache_stats=GuidelinesCacheStats(
                        total_entries=0,
                        valid_entries=0,
                        expired_entries=0
                    ),
                    error="Program not found or access denied"
                )
            
            # Get guidelines statistics
            active_guideline = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.is_active == True
            ).first()
            
            total_versions = db.query(AIGuideline.version).filter(
                AIGuideline.program_id == program_id
            ).distinct().count()
            
            # Get cache stats
            cache_stats_dict = openrouter_service.get_cache_stats()
            cache_stats = GuidelinesCacheStats(**cache_stats_dict)
            
            return GuidelinesStatusResponse(
                success=True,
                has_active_guidelines=active_guideline is not None,
                active_version=active_guideline.version if active_guideline else None,
                total_versions=total_versions,
                cache_stats=cache_stats
            )
            
        except Exception as e:
            logger.error(f"Failed to get guidelines status for program {program_id}: {str(e)}")
            return GuidelinesStatusResponse(
                success=False,
                has_active_guidelines=False,
                active_version=None,
                total_versions=0,
                cache_stats=GuidelinesCacheStats(
                    total_entries=0,
                    valid_entries=0,
                    expired_entries=0
                ),
                error=f"Failed to get status: {str(e)}"
            )

# Global service instance
ai_guidelines_service = AIGuidelinesService()