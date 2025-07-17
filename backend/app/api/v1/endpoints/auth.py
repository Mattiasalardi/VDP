from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps.auth import authenticate_organization, create_access_token, get_current_organization, get_password_hash
from app.core.config import settings
from app.core.database import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter()


@router.post("/register", response_model=OrganizationResponse)
def register(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db)
) -> Organization:
    """
    Register a new organization.
    """
    # Check if organization already exists
    existing_org = db.query(Organization).filter(Organization.email == organization_data.email).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this email already exists"
        )
    
    # Create new organization
    try:
        hashed_password = get_password_hash(organization_data.password)
        db_organization = Organization(
            name=organization_data.name,
            email=organization_data.email,
            password_hash=hashed_password,
            description=organization_data.description,
            website=organization_data.website,
            is_active=True
        )
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this email already exists"
        )


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