from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps.database import get_db
from app.models.application import Application
from app.models.program import Program
from app.models.questionnaire import Questionnaire
from app.models.question import Question
from app.schemas.question import QuestionResponse

router = APIRouter()

class PublicQuestionnaireResponse:
    def __init__(self, questionnaire_data: dict):
        self.id = questionnaire_data['id']
        self.name = questionnaire_data['name']
        self.description = questionnaire_data['description']
        self.program_name = questionnaire_data['program_name']
        self.questions = questionnaire_data['questions']

@router.get("/applications/{unique_id}/questionnaire")
def get_public_questionnaire(
    unique_id: str,
    program_id: Optional[int] = None,  # Optional program validation from URL
    db: Session = Depends(get_db)
):
    """
    Get questionnaire data for a specific application (public endpoint)
    Used by startup applicants to fill out their application form
    """
    # Get application with unique ID
    application = db.query(Application).filter(
        Application.unique_id == unique_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or invalid link"
        )
    
    # Validate program context if provided in URL
    if program_id and application.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Application does not belong to specified program"
        )
    
    # Check if application is already submitted
    if application.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application has already been submitted"
        )
    
    # Get questionnaire with questions
    questionnaire = db.query(Questionnaire).filter(
        Questionnaire.id == application.questionnaire_id
    ).first()
    
    if not questionnaire or not questionnaire.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found or inactive"
        )
    
    # Get questions ordered by order_index
    questions = db.query(Question).filter(
        Question.questionnaire_id == questionnaire.id
    ).order_by(Question.order_index).all()
    
    # Convert questions to dictionaries
    questions_data = []
    for q in questions:
        questions_data.append({
            "id": q.id,
            "question_type": q.question_type,
            "text": q.text,
            "options": q.options,
            "is_required": q.is_required,
            "order_index": q.order_index,
            "validation_rules": q.validation_rules,
            "questionnaire_id": q.questionnaire_id,
            "created_at": q.created_at,
            "updated_at": q.updated_at
        })
    
    # Get program name for context
    program = db.query(Program).filter(Program.id == application.program_id).first()
    
    return {
        "success": True,
        "application": {
            "id": application.id,
            "unique_id": application.unique_id,
            "startup_name": application.startup_name,
            "contact_email": application.contact_email,
            "is_submitted": application.is_submitted,
            "program_id": application.program_id,
            "program_name": program.name if program else "Unknown"
        },
        "questionnaire": {
            "id": questionnaire.id,
            "name": questionnaire.name,
            "description": questionnaire.description,
            "questions": questions_data
        }
    }

@router.get("/applications/{unique_id}")
def get_application_status(
    unique_id: str,
    db: Session = Depends(get_db)
):
    """
    Get application status (public endpoint)
    Used to show application status to startups
    """
    application = db.query(Application).filter(
        Application.unique_id == unique_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get program name
    program = db.query(Program).filter(Program.id == application.program_id).first()
    
    return {
        "success": True,
        "application": {
            "unique_id": application.unique_id,
            "startup_name": application.startup_name,
            "is_submitted": application.is_submitted,
            "is_processed": application.is_processed,
            "processing_status": application.processing_status,
            "submitted_at": application.submitted_at,
            "processed_at": application.processed_at,
            "program_name": program.name if program else "Unknown"
        }
    }