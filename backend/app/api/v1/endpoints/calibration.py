from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_organization
from app.api.deps.organization import get_organization_program
from app.core.database import get_db
from app.models.organization import Organization
from app.models.program import Program
from app.services.calibration_service import CalibrationService
from app.schemas.calibration import (
    CalibrationQuestionsResponse,
    CalibrationAnswerCreate,
    CalibrationAnswerResponse,
    CalibrationAnswerBatch,
    CalibrationCompletionStatus,
    CalibrationSessionResponse
)

router = APIRouter()

@router.get("/questions", response_model=CalibrationQuestionsResponse)
async def get_calibration_questions(
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all calibration questions organized by category.
    
    This endpoint returns the complete set of calibration questions
    that accelerators need to answer to set up AI scoring guidelines.
    """
    service = CalibrationService(db=None)  # Questions are static, no DB needed
    return service.get_calibration_questions()

@router.get("/programs/{program_id}/status", response_model=CalibrationCompletionStatus)
async def get_calibration_status(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get calibration completion status for a specific program.
    
    Returns information about which questions have been answered
    and what percentage of calibration is complete.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    return service.get_completion_status(program_id)

@router.get("/programs/{program_id}/answers", response_model=List[CalibrationAnswerResponse])
async def get_program_calibration_answers(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get all calibration answers for a specific program.
    
    Returns all the calibration answers that have been submitted
    for the specified program.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    return service.get_program_calibration_answers(program_id)

@router.get("/programs/{program_id}/session", response_model=CalibrationSessionResponse)
async def get_calibration_session(
    program_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get complete calibration session data including answers and status.
    
    Returns both the current answers and completion status in a single response,
    useful for loading the calibration form interface.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    
    # Get current answers and status
    answers = service.get_program_calibration_answers(program_id)
    status_info = service.get_completion_status(program_id)
    
    return CalibrationSessionResponse(
        program_id=program_id,
        total_questions=status_info.total_questions,
        answered_questions=status_info.answered_questions,
        completion_percentage=status_info.completion_percentage,
        answers=answers,
        missing_questions=status_info.missing_questions
    )

@router.post("/programs/{program_id}/answers", response_model=CalibrationAnswerResponse)
async def create_or_update_calibration_answer(
    program_id: int,
    answer_data: CalibrationAnswerCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Create or update a single calibration answer.
    
    If an answer for the specified question already exists, it will be updated.
    Otherwise, a new answer will be created.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    
    try:
        return service.create_or_update_answer(program_id, answer_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/programs/{program_id}/answers/batch", response_model=List[CalibrationAnswerResponse])
async def batch_create_or_update_answers(
    program_id: int,
    batch_data: CalibrationAnswerBatch,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Create or update multiple calibration answers in a single request.
    
    This is useful for saving progress when users complete multiple
    questions at once or when saving an entire category of questions.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    
    try:
        return service.batch_create_or_update_answers(program_id, batch_data.answers)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/programs/{program_id}/answers/{question_key}", response_model=CalibrationAnswerResponse)
async def get_calibration_answer_by_key(
    program_id: int,
    question_key: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Get a specific calibration answer by question key.
    
    Returns the answer for a specific calibration question,
    or 404 if no answer has been provided yet.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    answer = service.get_answer_by_question_key(program_id, question_key)
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No answer found for question key: {question_key}"
        )
    
    return answer

@router.delete("/programs/{program_id}/answers/{question_key}")
async def delete_calibration_answer(
    program_id: int,
    question_key: str,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization)
):
    """
    Delete a calibration answer.
    
    Removes the answer for a specific calibration question.
    Returns 404 if the answer doesn't exist.
    """
    # Verify program belongs to organization
    program = get_organization_program(db, current_org.id, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )
    
    service = CalibrationService(db)
    deleted = service.delete_answer(program_id, question_key)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No answer found for question key: {question_key}"
        )
    
    return {"message": f"Answer for {question_key} deleted successfully"}