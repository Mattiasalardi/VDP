"""
Program Service - Business logic for program management operations.
Handles CRUD operations, statistics, and program-related business rules.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.program import Program
from app.models.questionnaire import Questionnaire
from app.models.calibration_answer import CalibrationAnswer
from app.models.ai_guideline import AIGuideline
from app.models.application import Application
from app.schemas.program import (
    Program as ProgramSchema,
    ProgramWithStats,
    ProgramCreate,
    ProgramUpdate,
    ProgramListResponse,
    ProgramResponse,
    ProgramDetailsResponse
)

logger = logging.getLogger(__name__)

class ProgramService:
    """Service for program management operations."""
    
    def create_program(
        self,
        db: Session,
        program_data: ProgramCreate,
        organization_id: int
    ) -> ProgramResponse:
        """
        Create a new program for an organization.
        
        Args:
            db: Database session
            program_data: Program creation data
            organization_id: Organization ID
            
        Returns:
            ProgramResponse with created program or error
        """
        try:
            # Check for duplicate program name within organization
            existing_program = db.query(Program).filter(
                Program.organization_id == organization_id,
                Program.name == program_data.name,
                Program.is_active == True
            ).first()
            
            if existing_program:
                return ProgramResponse(
                    success=False,
                    error=f"Program '{program_data.name}' already exists"
                )
            
            # Create new program
            program = Program(
                name=program_data.name,
                description=program_data.description,
                is_active=program_data.is_active,
                organization_id=organization_id
            )
            
            db.add(program)
            db.commit()
            db.refresh(program)
            
            logger.info(f"Created program '{program.name}' for organization {organization_id}")
            
            return ProgramResponse(
                success=True,
                program=ProgramSchema.from_orm(program)
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create program: {str(e)}")
            return ProgramResponse(
                success=False,
                error=f"Failed to create program: {str(e)}"
            )
    
    def get_programs(
        self,
        db: Session,
        organization_id: int,
        include_inactive: bool = False
    ) -> ProgramListResponse:
        """
        Get all programs for an organization with statistics.
        
        Args:
            db: Database session
            organization_id: Organization ID
            include_inactive: Whether to include inactive programs
            
        Returns:
            ProgramListResponse with programs and stats
        """
        try:
            # Base query
            query = db.query(Program).filter(Program.organization_id == organization_id)
            
            if not include_inactive:
                query = query.filter(Program.is_active == True)
            
            programs = query.order_by(desc(Program.updated_at)).all()
            
            # Get statistics for each program
            programs_with_stats = []
            for program in programs:
                stats = self._get_program_statistics(db, program.id)
                
                program_with_stats = ProgramWithStats(
                    id=program.id,
                    name=program.name,
                    description=program.description,
                    is_active=program.is_active,
                    organization_id=program.organization_id,
                    created_at=program.created_at,
                    updated_at=program.updated_at,
                    questionnaire_count=stats['questionnaire_count'],
                    calibration_completion=stats['calibration_completion'],
                    has_active_guidelines=stats['has_active_guidelines'],
                    application_count=stats['application_count']
                )
                
                programs_with_stats.append(program_with_stats)
            
            return ProgramListResponse(
                success=True,
                programs=programs_with_stats,
                total_count=len(programs_with_stats)
            )
            
        except Exception as e:
            logger.error(f"Failed to get programs for organization {organization_id}: {str(e)}")
            return ProgramListResponse(
                success=False,
                programs=[],
                total_count=0,
                error=f"Failed to get programs: {str(e)}"
            )
    
    def get_program(
        self,
        db: Session,
        program_id: int,
        organization_id: int
    ) -> ProgramDetailsResponse:
        """
        Get a specific program with detailed statistics.
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            
        Returns:
            ProgramDetailsResponse with program details
        """
        try:
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return ProgramDetailsResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            # Get detailed statistics
            stats = self._get_program_statistics(db, program_id)
            
            program_with_stats = ProgramWithStats(
                id=program.id,
                name=program.name,
                description=program.description,
                is_active=program.is_active,
                organization_id=program.organization_id,
                created_at=program.created_at,
                updated_at=program.updated_at,
                questionnaire_count=stats['questionnaire_count'],
                calibration_completion=stats['calibration_completion'],
                has_active_guidelines=stats['has_active_guidelines'],
                application_count=stats['application_count']
            )
            
            return ProgramDetailsResponse(
                success=True,
                program=program_with_stats
            )
            
        except Exception as e:
            logger.error(f"Failed to get program {program_id}: {str(e)}")
            return ProgramDetailsResponse(
                success=False,
                error=f"Failed to get program: {str(e)}"
            )
    
    def update_program(
        self,
        db: Session,
        program_id: int,
        program_data: ProgramUpdate,
        organization_id: int
    ) -> ProgramResponse:
        """
        Update a program.
        
        Args:
            db: Database session
            program_id: Program ID
            program_data: Update data
            organization_id: Organization ID for security
            
        Returns:
            ProgramResponse with updated program or error
        """
        try:
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return ProgramResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            # Check for duplicate name if updating name
            if program_data.name and program_data.name != program.name:
                existing_program = db.query(Program).filter(
                    Program.organization_id == organization_id,
                    Program.name == program_data.name,
                    Program.id != program_id,
                    Program.is_active == True
                ).first()
                
                if existing_program:
                    return ProgramResponse(
                        success=False,
                        error=f"Program '{program_data.name}' already exists"
                    )
            
            # Update fields
            update_data = program_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(program, field, value)
            
            db.commit()
            db.refresh(program)
            
            logger.info(f"Updated program {program_id}")
            
            return ProgramResponse(
                success=True,
                program=ProgramSchema.from_orm(program)
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update program {program_id}: {str(e)}")
            return ProgramResponse(
                success=False,
                error=f"Failed to update program: {str(e)}"
            )
    
    def delete_program(
        self,
        db: Session,
        program_id: int,
        organization_id: int,
        hard_delete: bool = False
    ) -> ProgramResponse:
        """
        Delete a program (soft delete by default).
        
        Args:
            db: Database session
            program_id: Program ID
            organization_id: Organization ID for security
            hard_delete: Whether to permanently delete (dangerous)
            
        Returns:
            ProgramResponse with success/error status
        """
        try:
            program = db.query(Program).filter(
                Program.id == program_id,
                Program.organization_id == organization_id
            ).first()
            
            if not program:
                return ProgramResponse(
                    success=False,
                    error="Program not found or access denied"
                )
            
            if hard_delete:
                # Permanent deletion (use with caution)
                db.delete(program)
                logger.warning(f"Hard deleted program {program_id}")
            else:
                # Soft delete
                program.is_active = False
                logger.info(f"Soft deleted program {program_id}")
            
            db.commit()
            
            return ProgramResponse(
                success=True,
                program=None
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete program {program_id}: {str(e)}")
            return ProgramResponse(
                success=False,
                error=f"Failed to delete program: {str(e)}"
            )
    
    def _get_program_statistics(self, db: Session, program_id: int) -> Dict[str, Any]:
        """Get statistics for a program."""
        try:
            # Questionnaire count
            questionnaire_count = db.query(Questionnaire).filter(
                Questionnaire.program_id == program_id
            ).count()
            
            # Calibration completion (simplified - check if any answers exist)
            calibration_answers_count = db.query(CalibrationAnswer).filter(
                CalibrationAnswer.program_id == program_id
            ).count()
            
            # Rough calibration completion percentage (assume 8 total questions)
            calibration_completion = min(100.0, (calibration_answers_count / 8.0) * 100.0)
            
            # Active guidelines check
            has_active_guidelines = db.query(AIGuideline).filter(
                AIGuideline.program_id == program_id,
                AIGuideline.is_active == True
            ).first() is not None
            
            # Application count  
            application_count = db.query(Application).filter(
                Application.program_id == program_id
            ).count()
            
            return {
                'questionnaire_count': questionnaire_count,
                'calibration_completion': calibration_completion,
                'has_active_guidelines': has_active_guidelines,
                'application_count': application_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics for program {program_id}: {str(e)}")
            return {
                'questionnaire_count': 0,
                'calibration_completion': 0.0,
                'has_active_guidelines': False,
                'application_count': 0
            }

# Global service instance
program_service = ProgramService()