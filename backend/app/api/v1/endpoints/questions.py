from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api.deps.auth import get_current_organization
from app.api.deps.organization import get_organization_context
from app.core.database import get_db
from app.models.organization import Organization
from app.models.questionnaire import Questionnaire
from app.models.question import Question
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListResponse,
    QuestionReorderRequest
)

router = APIRouter()


@router.get("/questionnaires/{questionnaire_id}/questions", response_model=QuestionListResponse)
def get_questions(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Get all questions for a questionnaire"""
    
    # Verify questionnaire belongs to current organization
    questionnaire = db.query(Questionnaire).join(
        Questionnaire.program
    ).filter(
        and_(
            Questionnaire.id == questionnaire_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Get questions ordered by order_index
    questions = db.query(Question).filter(
        Question.questionnaire_id == questionnaire_id
    ).order_by(Question.order_index).all()
    
    return QuestionListResponse(
        questions=questions,
        total=len(questions),
        questionnaire_id=questionnaire_id
    )


@router.post("/questionnaires/{questionnaire_id}/questions", response_model=QuestionResponse)
def create_question(
    questionnaire_id: int,
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Create a new question"""
    
    # Verify questionnaire belongs to current organization
    questionnaire = db.query(Questionnaire).join(
        Questionnaire.program
    ).filter(
        and_(
            Questionnaire.id == questionnaire_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Check 50 question limit
    question_count = db.query(Question).filter(
        Question.questionnaire_id == questionnaire_id
    ).count()
    
    if question_count >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 questions allowed per questionnaire"
        )
    
    # Set questionnaire_id from URL parameter
    question.questionnaire_id = questionnaire_id
    
    # If order_index is not provided or conflicts, set it to the end
    if question.order_index is None:
        max_order = db.query(Question).filter(
            Question.questionnaire_id == questionnaire_id
        ).count()
        question.order_index = max_order
    else:
        # Check if order_index already exists
        existing_question = db.query(Question).filter(
            and_(
                Question.questionnaire_id == questionnaire_id,
                Question.order_index == question.order_index
            )
        ).first()
        
        if existing_question:
            # Shift existing questions to make room
            db.query(Question).filter(
                and_(
                    Question.questionnaire_id == questionnaire_id,
                    Question.order_index >= question.order_index
                )
            ).update({
                Question.order_index: Question.order_index + 1
            })
    
    # Create question
    db_question = Question(
        text=question.text,
        question_type=question.question_type.value,
        is_required=question.is_required,
        order_index=question.order_index,
        options=question.options.dict() if question.options else None,
        validation_rules=question.validation_rules.dict() if question.validation_rules else None,
        questionnaire_id=questionnaire_id
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Get a specific question"""
    
    # Verify question belongs to current organization
    question = db.query(Question).join(
        Question.questionnaire
    ).join(
        Questionnaire.program
    ).filter(
        and_(
            Question.id == question_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Update a question"""
    
    # Verify question belongs to current organization
    db_question = db.query(Question).join(
        Question.questionnaire
    ).join(
        Questionnaire.program
    ).filter(
        and_(
            Question.id == question_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Handle order_index changes
    if question_update.order_index is not None and question_update.order_index != db_question.order_index:
        # Check if new order_index is valid
        max_order = db.query(Question).filter(
            Question.questionnaire_id == db_question.questionnaire_id
        ).count() - 1
        
        if question_update.order_index > max_order:
            question_update.order_index = max_order
        
        # Reorder questions
        if question_update.order_index > db_question.order_index:
            # Moving down - shift questions up
            db.query(Question).filter(
                and_(
                    Question.questionnaire_id == db_question.questionnaire_id,
                    Question.order_index > db_question.order_index,
                    Question.order_index <= question_update.order_index,
                    Question.id != question_id
                )
            ).update({
                Question.order_index: Question.order_index - 1
            })
        else:
            # Moving up - shift questions down
            db.query(Question).filter(
                and_(
                    Question.questionnaire_id == db_question.questionnaire_id,
                    Question.order_index >= question_update.order_index,
                    Question.order_index < db_question.order_index,
                    Question.id != question_id
                )
            ).update({
                Question.order_index: Question.order_index + 1
            })
    
    # Update question fields
    update_data = question_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "options" and value is not None:
            setattr(db_question, field, value.dict())
        elif field == "validation_rules" and value is not None:
            setattr(db_question, field, value.dict())
        elif field == "question_type" and value is not None:
            setattr(db_question, field, value.value)
        else:
            setattr(db_question, field, value)
    
    db.commit()
    db.refresh(db_question)
    
    return db_question


@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Delete a question"""
    
    # Verify question belongs to current organization
    db_question = db.query(Question).join(
        Question.questionnaire
    ).join(
        Questionnaire.program
    ).filter(
        and_(
            Question.id == question_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    questionnaire_id = db_question.questionnaire_id
    order_index = db_question.order_index
    
    # Delete the question
    db.delete(db_question)
    
    # Reorder remaining questions
    db.query(Question).filter(
        and_(
            Question.questionnaire_id == questionnaire_id,
            Question.order_index > order_index
        )
    ).update({
        Question.order_index: Question.order_index - 1
    })
    
    db.commit()
    
    return {"detail": "Question deleted successfully"}


@router.post("/questionnaires/{questionnaire_id}/questions/reorder")
def reorder_questions(
    questionnaire_id: int,
    reorder_request: QuestionReorderRequest,
    db: Session = Depends(get_db),
    current_org: Organization = Depends(get_current_organization),
    org_context = Depends(get_organization_context)
):
    """Reorder questions in a questionnaire"""
    
    # Verify questionnaire belongs to current organization
    questionnaire = db.query(Questionnaire).join(
        Questionnaire.program
    ).filter(
        and_(
            Questionnaire.id == questionnaire_id,
            Questionnaire.program.has(organization_id=current_org.id)
        )
    ).first()
    
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    
    # Verify all questions belong to this questionnaire
    question_ids = set(reorder_request.question_order)
    existing_questions = db.query(Question).filter(
        and_(
            Question.questionnaire_id == questionnaire_id,
            Question.id.in_(question_ids)
        )
    ).all()
    
    if len(existing_questions) != len(question_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some questions do not belong to this questionnaire"
        )
    
    # Update order_index for each question
    for new_index, question_id in enumerate(reorder_request.question_order):
        db.query(Question).filter(
            Question.id == question_id
        ).update({
            Question.order_index: new_index
        })
    
    db.commit()
    
    return {"detail": "Questions reordered successfully"}