from typing import Type, TypeVar
from fastapi import Depends
from sqlalchemy.orm import Session, Query

from app.api.deps.auth import get_current_organization
from app.core.database import get_db
from app.models.organization import Organization
from app.models.program import Program

T = TypeVar('T')


def get_organization_scoped_query(
    model: Type[T],
    current_organization: Organization = Depends(get_current_organization),
    db: Session = Depends(get_db)
) -> Query[T]:
    """
    Get a query scoped to the current organization.
    This ensures multi-tenant data isolation.
    """
    return db.query(model).filter(model.organization_id == current_organization.id)


def get_organization_context():
    """
    Dependency to get organization context for API routes.
    This ensures all routes are properly scoped to the authenticated organization.
    """
    def _get_context(
        current_organization: Organization = Depends(get_current_organization),
        db: Session = Depends(get_db)
    ):
        return {
            "organization": current_organization,
            "db": db,
            "organization_id": current_organization.id
        }
    
    return _get_context


def get_organization_program(db: Session, organization_id: int, program_id: int) -> Program:
    """
    Get a program that belongs to the specified organization.
    Returns None if the program doesn't exist or doesn't belong to the organization.
    """
    return (
        db.query(Program)
        .filter(
            Program.id == program_id,
            Program.organization_id == organization_id
        )
        .first()
    )