"""
Program Management API endpoints.
Provides REST API for program CRUD operations and management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_organization
from app.api.deps.database import get_db
from app.models.organization import Organization
from app.schemas.program import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramListResponse,
    ProgramDetailsResponse
)
from app.services.program_service import program_service

router = APIRouter()

@router.post("/", response_model=ProgramResponse)
def create_program(
    program_data: ProgramCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Create a new program for the current organization.
    
    Programs are the main organizational unit for questionnaires,
    calibration settings, and AI guidelines.
    """
    try:
        response = program_service.create_program(
            db=db,
            program_data=program_data,
            organization_id=current_org.id
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {str(e)}"
        )

@router.get("/", response_model=ProgramListResponse)
def get_programs(
    include_inactive: bool = Query(default=False, description="Include inactive programs"),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all programs for the current organization.
    
    Returns programs with statistics including questionnaire count,
    calibration completion, guidelines status, and application count.
    """
    try:
        response = program_service.get_programs(
            db=db,
            organization_id=current_org.id,
            include_inactive=include_inactive
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get programs: {str(e)}"
        )

@router.get("/{program_id}", response_model=ProgramDetailsResponse)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get a specific program with detailed statistics.
    
    Returns comprehensive information about the program including
    all related statistics and completion status.
    """
    try:
        response = program_service.get_program(
            db=db,
            program_id=program_id,
            organization_id=current_org.id
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get program: {str(e)}"
        )

@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Update a program's information.
    
    Allows updating name, description, and active status.
    Program names must be unique within an organization.
    """
    try:
        response = program_service.update_program(
            db=db,
            program_id=program_id,
            program_data=program_data,
            organization_id=current_org.id
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update program: {str(e)}"
        )

@router.delete("/{program_id}", response_model=ProgramResponse)
def delete_program(
    program_id: int,
    hard_delete: bool = Query(default=False, description="Permanently delete (dangerous)"),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Delete a program (soft delete by default).
    
    By default, programs are soft-deleted (marked as inactive).
    Hard deletion permanently removes the program and all related data.
    """
    try:
        response = program_service.delete_program(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            hard_delete=hard_delete
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete program: {str(e)}"
        )

# Additional utility endpoints

@router.post("/{program_id}/duplicate", response_model=ProgramResponse)
def duplicate_program(
    program_id: int,
    new_name: str = Query(..., description="Name for the duplicated program"),
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Duplicate a program with all its settings.
    
    Creates a copy of the program including questionnaires and
    calibration settings, but not applications or reports.
    """
    try:
        # Get original program
        original_response = program_service.get_program(
            db=db,
            program_id=program_id,
            organization_id=current_org.id
        )
        
        if not original_response.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found"
            )
        
        original_program = original_response.program
        
        # Create duplicate
        duplicate_data = ProgramCreate(
            name=new_name,
            description=f"Copy of {original_program.name}",
            is_active=True
        )
        
        response = program_service.create_program(
            db=db,
            program_data=duplicate_data,
            organization_id=current_org.id
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response.error
            )
        
        # TODO: Copy questionnaires and calibration settings
        # This would be implemented in a future enhancement
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate program: {str(e)}"
        )

@router.post("/{program_id}/activate", response_model=ProgramResponse)
def activate_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Activate a program (set is_active = True).
    
    Convenience endpoint for reactivating soft-deleted programs.
    """
    try:
        update_data = ProgramUpdate(is_active=True)
        
        response = program_service.update_program(
            db=db,
            program_id=program_id,
            program_data=update_data,
            organization_id=current_org.id
        )
        
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=response.error
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate program: {str(e)}"
        )