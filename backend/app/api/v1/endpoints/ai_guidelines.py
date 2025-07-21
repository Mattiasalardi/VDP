"""
AI Guidelines API endpoints.
Provides REST API for generating, managing, and versioning AI guidelines.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_organization
from app.api.deps.database import get_db
from app.models.organization import Organization
from app.schemas.ai_guidelines import (
    GenerateGuidelinesRequest,
    GeneratedGuidelines,
    SaveGuidelinesRequest,
    UpdateGuidelinesRequest,
    ActivateGuidelinesRequest,
    GuidelinesGenerationResponse,
    GuidelinesSaveResponse,
    GuidelinesListResponse,
    GuidelinesActivationResponse,
    GuidelinesStatusResponse,
    SavedGuidelines
)
from app.services.ai_guidelines_service import ai_guidelines_service

router = APIRouter()

@router.post("/generate", response_model=GuidelinesGenerationResponse)
async def generate_guidelines(
    request: GenerateGuidelinesRequest,
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Generate AI guidelines based on calibration data for a program.
    
    Requires completed calibration data to generate personalized guidelines.
    Uses OpenRouter API with configurable AI models.
    """
    try:
        # Use calibration data from request if provided, otherwise get from database
        response = await ai_guidelines_service.generate_guidelines_from_calibration(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            model=request.model
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
            detail=f"Guidelines generation failed: {str(e)}"
        )

@router.post("/save", response_model=GuidelinesSaveResponse)
def save_guidelines(
    request: SaveGuidelinesRequest,
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Save generated guidelines with versioning support.
    
    Can optionally activate immediately or save as draft for review.
    Creates a new version number automatically.
    """
    try:
        response = ai_guidelines_service.save_guidelines(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            guidelines=request.guidelines,
            is_active=request.is_active,
            notes=request.notes
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
            detail=f"Failed to save guidelines: {str(e)}"
        )

@router.get("/active", response_model=Optional[SavedGuidelines])
def get_active_guidelines(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get the currently active guidelines for a program.
    
    Returns None if no guidelines are currently active.
    """
    try:
        active_guidelines = ai_guidelines_service.get_active_guidelines(
            db=db,
            program_id=program_id,
            organization_id=current_org.id
        )
        
        return active_guidelines
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active guidelines: {str(e)}"
        )

@router.get("/history", response_model=GuidelinesListResponse)
def get_guidelines_history(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all versions of guidelines for a program.
    
    Returns list sorted by version number (newest first).
    Includes information about which version is currently active.
    """
    try:
        response = ai_guidelines_service.get_guidelines_history(
            db=db,
            program_id=program_id,
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
            detail=f"Failed to get guidelines history: {str(e)}"
        )

@router.post("/activate", response_model=GuidelinesActivationResponse)
def activate_guidelines_version(
    request: ActivateGuidelinesRequest,
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Activate a specific version of guidelines.
    
    Deactivates all other versions and activates the specified version.
    This is the approval workflow - guidelines must be explicitly activated.
    """
    try:
        response = ai_guidelines_service.activate_guidelines_version(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            version=request.version
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
            detail=f"Failed to activate guidelines: {str(e)}"
        )

@router.get("/status", response_model=GuidelinesStatusResponse)
def get_guidelines_status(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get overall status of guidelines system for a program.
    
    Includes information about active version, total versions,
    cache statistics, and system health.
    """
    try:
        response = ai_guidelines_service.get_guidelines_status(
            db=db,
            program_id=program_id,
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
            detail=f"Failed to get guidelines status: {str(e)}"
        )

# Additional utility endpoints

@router.post("/generate-and-save", response_model=GuidelinesSaveResponse)
async def generate_and_save_guidelines(
    program_id: int,
    model: Optional[str] = None,
    activate_immediately: bool = False,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Convenience endpoint to generate and immediately save guidelines.
    
    Combines generation and saving in a single API call.
    Useful for automated workflows.
    """
    try:
        # Generate guidelines
        generation_response = await ai_guidelines_service.generate_guidelines_from_calibration(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            model=model
        )
        
        if not generation_response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=generation_response.error
            )
        
        # Save guidelines
        save_response = ai_guidelines_service.save_guidelines(
            db=db,
            program_id=program_id,
            organization_id=current_org.id,
            guidelines=generation_response.guidelines,
            is_active=activate_immediately,
            notes=notes
        )
        
        if not save_response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=save_response.error
            )
        
        return save_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate and save guidelines: {str(e)}"
        )

@router.delete("/cache")
def clear_guidelines_cache(
    current_org: Organization = Depends(get_current_organization)
):
    """
    Clear the guidelines generation cache.
    
    Forces fresh generation for all subsequent requests.
    Useful for testing or when calibration data changes.
    """
    try:
        from app.services.openrouter_service import openrouter_service
        openrouter_service.clear_cache()
        
        return {"success": True, "message": "Guidelines cache cleared"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )