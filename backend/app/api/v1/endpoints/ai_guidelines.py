from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_organization
from app.api.deps.organization import get_organization_program
from app.core.database import get_db
from app.models.organization import Organization
from app.models.program import Program
from app.services.ai_guidelines_service import AIGuidelinesService
from app.schemas.ai_guidelines import (
    GuidelinesGenerationRequest,
    GuidelinesGenerationResponse,
    GuidelinesSaveRequest,
    GuidelinesResponse,
    GuidelinesListResponse
)

router = APIRouter()

@router.post("/programs/{program_id}/generate", response_model=GuidelinesGenerationResponse)
async def generate_ai_guidelines(
    program_id: int,
    request: GuidelinesGenerationRequest,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Generate AI scoring guidelines based on calibration answers.
    
    This endpoint uses the program's calibration responses to generate
    customized scoring guidelines via OpenRouter AI models.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = AIGuidelinesService(db)
    
    try:
        result = service.generate_guidelines(
            program_id=program_id,
            organization_id=current_org.id,
            model=request.model
        )
        
        return GuidelinesGenerationResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guidelines generation failed: {str(e)}"
        )

@router.post("/programs/{program_id}/save", response_model=GuidelinesResponse)
async def save_ai_guidelines(
    program_id: int,
    request: GuidelinesSaveRequest,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Save AI guidelines after review and optional modification.
    
    This endpoint allows saving generated guidelines with optional
    user modifications and approval status.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = AIGuidelinesService(db)
    
    try:
        saved_guideline = service.save_guidelines(
            program_id=program_id,
            guidelines_data=request.guidelines_data,
            is_approved=request.is_approved
        )
        
        return GuidelinesResponse(
            id=saved_guideline.id,
            program_id=saved_guideline.program_id,
            guidelines=saved_guideline.guidelines_json,
            version=saved_guideline.version,
            is_active=saved_guideline.is_active,
            model_used=saved_guideline.model_used,
            created_at=saved_guideline.created_at.isoformat(),
            generated_at=saved_guideline.generated_at.isoformat() if saved_guideline.generated_at else None
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Guidelines save failed: {str(e)}"
        )

@router.get("/programs/{program_id}/active", response_model=GuidelinesResponse)
async def get_active_guidelines(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get the currently active AI guidelines for a program.
    
    Returns the approved and active scoring guidelines that are
    currently being used for application evaluation.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = AIGuidelinesService(db)
    active_guideline = service.get_active_guidelines(program_id)
    
    if not active_guideline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active guidelines found for this program"
        )
    
    return GuidelinesResponse(
        id=active_guideline.id,
        program_id=active_guideline.program_id,
        guidelines=active_guideline.guidelines_json,
        version=active_guideline.version,
        is_active=active_guideline.is_active,
        model_used=active_guideline.model_used,
        created_at=active_guideline.created_at.isoformat(),
        generated_at=active_guideline.generated_at.isoformat() if active_guideline.generated_at else None
    )

@router.get("/programs/{program_id}/history", response_model=GuidelinesListResponse)
async def get_guidelines_history(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all guidelines versions for a program.
    
    Returns the complete history of guidelines generations
    for auditing and comparison purposes.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = AIGuidelinesService(db)
    guidelines_history = service.get_guidelines_history(program_id)
    
    guidelines_list = [
        GuidelinesResponse(
            id=guideline.id,
            program_id=guideline.program_id,
            guidelines=guideline.guidelines_json,
            version=guideline.version,
            is_active=guideline.is_active,
            model_used=guideline.model_used,
            created_at=guideline.created_at.isoformat(),
            generated_at=guideline.generated_at.isoformat() if guideline.generated_at else None
        )
        for guideline in guidelines_history
    ]
    
    return GuidelinesListResponse(
        guidelines=guidelines_list,
        total_count=len(guidelines_list)
    )

@router.post("/programs/{program_id}/activate/{version}")
async def activate_guidelines_version(
    program_id: int,
    version: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Activate a specific version of guidelines.
    
    This endpoint allows switching between different versions
    of generated guidelines for a program.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = AIGuidelinesService(db)
    
    # Get the specific version
    guidelines_history = service.get_guidelines_history(program_id)
    target_guideline = next((g for g in guidelines_history if g.version == version), None)
    
    if not target_guideline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Guidelines version {version} not found"
        )
    
    try:
        # Deactivate all current guidelines
        from sqlalchemy import and_
        from app.models.ai_guideline import AIGuideline
        
        db.query(AIGuideline).filter(
            and_(
                AIGuideline.program_id == program_id,
                AIGuideline.is_active == True
            )
        ).update({"is_active": False})
        
        # Activate the target version
        target_guideline.is_active = True
        db.commit()
        
        return {"message": f"Guidelines version {version} activated successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate guidelines version: {str(e)}"
        )