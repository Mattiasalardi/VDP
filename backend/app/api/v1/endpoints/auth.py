from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps.auth import authenticate_organization, create_access_token, get_current_organization
from app.core.config import settings
from app.core.database import get_db
from app.models.organization import Organization

router = APIRouter()


@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> dict[str, Any]:
    """
    Login endpoint for organizations.
    Uses OAuth2 compatible token response.
    """
    organization = authenticate_organization(db, form_data.username, form_data.password)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(organization.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organization_id": organization.id,
        "organization_name": organization.name
    }


@router.post("/logout")
def logout(
    current_organization: Organization = Depends(get_current_organization)
) -> dict[str, str]:
    """
    Logout endpoint (token invalidation would be handled client-side for stateless JWT).
    """
    return {"message": "Successfully logged out"}


@router.get("/me")
def get_current_user(
    current_organization: Organization = Depends(get_current_organization)
) -> dict[str, Any]:
    """
    Get current authenticated organization details.
    """
    return {
        "id": current_organization.id,
        "name": current_organization.name,
        "email": current_organization.email,
        "created_at": current_organization.created_at
    }