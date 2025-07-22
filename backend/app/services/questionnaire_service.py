from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.questionnaire import Questionnaire
from app.models.question import Question
from app.schemas.questionnaire import QuestionnaireCreate, QuestionnaireUpdate


class QuestionnaireService:
    """Service for questionnaire management operations"""
    
    @staticmethod
    def get_questionnaires_by_program(
        db: Session,
        program_id: int,
        organization_id: int,
        include_inactive: bool = False
    ) -> List[Questionnaire]:
        """Get all questionnaires for a program"""
        from app.models.program import Program
        
        query = db.query(Questionnaire).join(Program).filter(
            Questionnaire.program_id == program_id,
            Program.organization_id == organization_id
        )
        
        if not include_inactive:
            query = query.filter(Questionnaire.is_active == True)
            
        return query.order_by(Questionnaire.created_at.desc()).all()
    
    @staticmethod
    def get_questionnaire_by_id(
        db: Session,
        questionnaire_id: int,
        organization_id: int
    ) -> Optional[Questionnaire]:
        """Get a specific questionnaire by ID"""
        from app.models.program import Program
        
        return db.query(Questionnaire).join(Program).filter(
            Questionnaire.id == questionnaire_id,
            Program.organization_id == organization_id
        ).first()
    
    @staticmethod
    def create_questionnaire(
        db: Session,
        questionnaire_data: QuestionnaireCreate,
        program_id: int,
        organization_id: int
    ) -> Questionnaire:
        """Create a new questionnaire"""
        db_questionnaire = Questionnaire(
            name=questionnaire_data.name,
            description=questionnaire_data.description,
            is_active=questionnaire_data.is_active,
            program_id=program_id
        )
        
        db.add(db_questionnaire)
        db.commit()
        db.refresh(db_questionnaire)
        return db_questionnaire
    
    @staticmethod
    def update_questionnaire(
        db: Session,
        questionnaire: Questionnaire,
        questionnaire_data: QuestionnaireUpdate
    ) -> Questionnaire:
        """Update an existing questionnaire"""
        update_data = questionnaire_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(questionnaire, field, value)
        
        db.commit()
        db.refresh(questionnaire)
        return questionnaire
    
    @staticmethod
    def delete_questionnaire(
        db: Session,
        questionnaire: Questionnaire
    ) -> bool:
        """Delete a questionnaire (soft delete by setting inactive)"""
        questionnaire.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_questionnaire_with_questions(
        db: Session,
        questionnaire_id: int,
        organization_id: int
    ) -> Optional[dict]:
        """Get questionnaire with its questions"""
        questionnaire = QuestionnaireService.get_questionnaire_by_id(
            db, questionnaire_id, organization_id
        )
        
        if questionnaire:
            # Load questions
            questions = db.query(Question).filter(
                Question.questionnaire_id == questionnaire_id
            ).order_by(Question.order_index).all()
            
            # Convert questions to dicts for JSON serialization
            questions_data = []
            for q in questions:
                questions_data.append({
                    "id": q.id,
                    "question_type": q.question_type,
                    "question_text": q.question_text,
                    "text": q.text,
                    "options": q.options,
                    "is_required": q.is_required,
                    "order_index": q.order_index,
                    "validation_rules": q.validation_rules,
                    "questionnaire_id": q.questionnaire_id,
                    "created_at": q.created_at,
                    "updated_at": q.updated_at
                })
            
            # Return as dict to avoid SQLAlchemy attribute issues
            return {
                "id": questionnaire.id,
                "name": questionnaire.name,
                "description": questionnaire.description,
                "is_active": questionnaire.is_active,
                "program_id": questionnaire.program_id,
                "created_at": questionnaire.created_at,
                "updated_at": questionnaire.updated_at,
                "question_count": len(questions),
                "questions": questions_data
            }
            
        return None
    
    @staticmethod
    def get_questionnaire_stats(
        db: Session,
        questionnaire: Questionnaire
    ) -> dict:
        """Get statistics for a questionnaire"""
        question_count = db.query(func.count(Question.id)).filter(
            Question.questionnaire_id == questionnaire.id
        ).scalar() or 0
        
        return {
            "question_count": question_count,
            "is_complete": question_count > 0,
            "can_be_published": question_count > 0 and questionnaire.is_active
        }