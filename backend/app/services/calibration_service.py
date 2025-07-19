from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.calibration_answer import CalibrationAnswer
from ..schemas.calibration import (
    CalibrationAnswerCreate,
    CalibrationAnswerUpdate,
    CalibrationAnswerResponse,
    CalibrationCompletionStatus,
    CalibrationQuestionsResponse
)
from ..core.calibration_questions import (
    CALIBRATION_QUESTIONS, 
    CALIBRATION_CATEGORIES,
    get_all_questions_organized,
    get_question_by_key
)

class CalibrationService:
    """Service class for handling calibration logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_calibration_questions(self) -> CalibrationQuestionsResponse:
        """Get all calibration questions organized by category"""
        organized_questions = get_all_questions_organized()
        total_questions = len(CALIBRATION_QUESTIONS)
        
        return CalibrationQuestionsResponse(
            categories=organized_questions,
            total_questions=total_questions
        )
    
    def get_program_calibration_answers(self, program_id: int) -> List[CalibrationAnswerResponse]:
        """Get all calibration answers for a program"""
        answers = (
            self.db.query(CalibrationAnswer)
            .filter(CalibrationAnswer.program_id == program_id)
            .all()
        )
        
        # Only return answers for questions that are currently defined
        all_question_keys = {question["key"] for question in CALIBRATION_QUESTIONS}
        valid_answers = [answer for answer in answers if answer.question_key in all_question_keys]
        
        return [
            CalibrationAnswerResponse(
                id=answer.id,
                question_key=answer.question_key,
                answer_value=answer.answer_value,
                answer_text=answer.answer_text,
                program_id=answer.program_id,
                created_at=answer.created_at.isoformat(),
                updated_at=answer.updated_at.isoformat()
            )
            for answer in valid_answers
        ]
    
    def get_completion_status(self, program_id: int) -> CalibrationCompletionStatus:
        """Get calibration completion status for a program"""
        existing_answers = (
            self.db.query(CalibrationAnswer.question_key)
            .filter(CalibrationAnswer.program_id == program_id)
            .all()
        )
        
        # Only count answers for questions that are currently defined
        all_question_keys = {question["key"] for question in CALIBRATION_QUESTIONS}
        answered_keys = {answer.question_key for answer in existing_answers if answer.question_key in all_question_keys}
        missing_keys = list(all_question_keys - answered_keys)
        
        answered_count = len(answered_keys)
        total_count = len(all_question_keys)
        completion_percentage = (answered_count / total_count) * 100 if total_count > 0 else 0
        is_complete = len(missing_keys) == 0
        
        # Determine next category to complete
        next_category = None
        if not is_complete:
            for category_key, category_info in CALIBRATION_CATEGORIES.items():
                category_questions = set(category_info["questions"])
                if not category_questions.issubset(answered_keys):
                    next_category = category_key
                    break
        
        return CalibrationCompletionStatus(
            is_complete=is_complete,
            total_questions=total_count,
            answered_questions=answered_count,
            completion_percentage=completion_percentage,
            missing_questions=missing_keys,
            next_category=next_category
        )
    
    def create_or_update_answer(
        self, 
        program_id: int, 
        answer_data: CalibrationAnswerCreate
    ) -> CalibrationAnswerResponse:
        """Create or update a calibration answer"""
        
        # Validate question key exists
        question = get_question_by_key(answer_data.question_key)
        if not question:
            raise ValueError(f"Invalid question key: {answer_data.question_key}")
        
        # Validate answer format based on question type
        self._validate_answer_format(question, answer_data.answer_value)
        
        # Check if answer already exists
        existing_answer = (
            self.db.query(CalibrationAnswer)
            .filter(
                and_(
                    CalibrationAnswer.program_id == program_id,
                    CalibrationAnswer.question_key == answer_data.question_key
                )
            )
            .first()
        )
        
        if existing_answer:
            # Update existing answer
            existing_answer.answer_value = answer_data.answer_value
            existing_answer.answer_text = answer_data.answer_text
            self.db.commit()
            self.db.refresh(existing_answer)
            answer = existing_answer
        else:
            # Create new answer
            answer = CalibrationAnswer(
                program_id=program_id,
                question_key=answer_data.question_key,
                answer_value=answer_data.answer_value,
                answer_text=answer_data.answer_text
            )
            self.db.add(answer)
            self.db.commit()
            self.db.refresh(answer)
        
        return CalibrationAnswerResponse(
            id=answer.id,
            question_key=answer.question_key,
            answer_value=answer.answer_value,
            answer_text=answer.answer_text,
            program_id=answer.program_id,
            created_at=answer.created_at.isoformat(),
            updated_at=answer.updated_at.isoformat()
        )
    
    def batch_create_or_update_answers(
        self, 
        program_id: int, 
        answers_data: List[CalibrationAnswerCreate]
    ) -> List[CalibrationAnswerResponse]:
        """Create or update multiple calibration answers in batch"""
        responses = []
        
        for answer_data in answers_data:
            try:
                response = self.create_or_update_answer(program_id, answer_data)
                responses.append(response)
            except Exception as e:
                # For batch operations, you might want to handle partial failures
                # For now, we'll let the error bubble up
                raise ValueError(f"Error processing answer for {answer_data.question_key}: {str(e)}")
        
        return responses
    
    def delete_answer(self, program_id: int, question_key: str) -> bool:
        """Delete a calibration answer"""
        answer = (
            self.db.query(CalibrationAnswer)
            .filter(
                and_(
                    CalibrationAnswer.program_id == program_id,
                    CalibrationAnswer.question_key == question_key
                )
            )
            .first()
        )
        
        if answer:
            self.db.delete(answer)
            self.db.commit()
            return True
        
        return False
    
    def _validate_answer_format(self, question: Dict[str, Any], answer_value: Dict[str, Any]) -> None:
        """Validate answer format matches question type"""
        question_type = question["type"]
        
        if question_type == "scale":
            if "scale_value" not in answer_value:
                raise ValueError("Scale questions require 'scale_value' in answer")
            
            scale_value = answer_value["scale_value"]
            if not isinstance(scale_value, int):
                raise ValueError("Scale value must be an integer")
            
            min_val = question.get("scale_min", 1)
            max_val = question.get("scale_max", 10)
            if not (min_val <= scale_value <= max_val):
                raise ValueError(f"Scale value must be between {min_val} and {max_val}")
        
        elif question_type == "multiple_choice":
            if "choice_value" not in answer_value:
                raise ValueError("Multiple choice questions require 'choice_value' in answer")
            
            choice_value = answer_value["choice_value"]
            valid_choices = [option["value"] for option in question.get("options", [])]
            if choice_value not in valid_choices:
                raise ValueError(f"Invalid choice. Valid options: {valid_choices}")
        
        elif question_type == "text":
            if "text_value" not in answer_value:
                raise ValueError("Text questions require 'text_value' in answer")
            
            text_value = answer_value["text_value"]
            if not isinstance(text_value, str):
                raise ValueError("Text value must be a string")
            
            max_length = question.get("max_length")
            if max_length and len(text_value) > max_length:
                raise ValueError(f"Text value exceeds maximum length of {max_length}")
    
    def get_answer_by_question_key(self, program_id: int, question_key: str) -> Optional[CalibrationAnswerResponse]:
        """Get a specific calibration answer by question key"""
        answer = (
            self.db.query(CalibrationAnswer)
            .filter(
                and_(
                    CalibrationAnswer.program_id == program_id,
                    CalibrationAnswer.question_key == question_key
                )
            )
            .first()
        )
        
        if not answer:
            return None
        
        return CalibrationAnswerResponse(
            id=answer.id,
            question_key=answer.question_key,
            answer_value=answer.answer_value,
            answer_text=answer.answer_text,
            program_id=answer.program_id,
            created_at=answer.created_at.isoformat(),
            updated_at=answer.updated_at.isoformat()
        )