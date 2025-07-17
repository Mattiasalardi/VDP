from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_organization
from app.api.deps.organization import get_organization_context
from app.core.database import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationResponse, OrganizationUpdate

router = APIRouter()


@router.get("/me", response_model=OrganizationResponse)
def get_organization(
    current_organization: Organization = Depends(get_current_organization)
) -> Organization:
    """
    Get current organization details.
    This endpoint is scoped to the authenticated organization.
    """
    return current_organization


@router.put("/me", response_model=OrganizationResponse)
def update_organization(
    organization_update: OrganizationUpdate,
    current_organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Update current organization details.
    This endpoint is scoped to the authenticated organization.
    """
    # Update only provided fields
    update_data = organization_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_organization, field, value)
    
    db.commit()
    db.refresh(current_organization)
    
    return current_organization


@router.get("/programs")
def get_organization_programs(
    current_organization: Organization = Depends(get_current_organization)
) -> dict[str, Any]:
    """
    Get programs for the current organization.
    This demonstrates organization-scoped data access.
    """
    # Return programs belonging to the current organization
    programs = current_organization.programs
    
    return {
        "organization_id": current_organization.id,
        "organization_name": current_organization.name,
        "programs": [
            {
                "id": program.id,
                "name": program.name,
                "description": program.description,
                "created_at": program.created_at
            }
            for program in programs
        ]
    }