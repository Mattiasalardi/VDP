from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.question import Question
from app.models.questionnaire import Questionnaire
from app.schemas.question import (
    QuestionType,
    TextQuestionOptions,
    MultipleChoiceQuestionOptions,
    ScaleQuestionOptions,
    FileUploadQuestionOptions,
    QuestionValidationRules
)


class QuestionService:
    """Service class for question-related business logic"""
    
    @staticmethod
    def validate_question_options(question_type: QuestionType, options: Optional[Dict[str, Any]]) -> bool:
        """Validate question options based on question type"""
        if not options:
            return question_type in [QuestionType.TEXT, QuestionType.FILE_UPLOAD]
        
        try:
            if question_type == QuestionType.TEXT:
                TextQuestionOptions(**options)
            elif question_type == QuestionType.MULTIPLE_CHOICE:
                MultipleChoiceQuestionOptions(**options)
            elif question_type == QuestionType.SCALE:
                ScaleQuestionOptions(**options)
            elif question_type == QuestionType.FILE_UPLOAD:
                FileUploadQuestionOptions(**options)
            else:
                return False
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_question_response(question: Question, response_value: Any) -> tuple[bool, Optional[str]]:
        """Validate a response value against question validation rules"""
        
        # Check if question is required
        if question.is_required and (response_value is None or response_value == ""):
            return False, "This question is required"
        
        # If not required and empty, it's valid
        if not question.is_required and (response_value is None or response_value == ""):
            return True, None
        
        # Type-specific validation
        if question.question_type == QuestionType.TEXT:
            return QuestionService._validate_text_response(question, response_value)
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            return QuestionService._validate_multiple_choice_response(question, response_value)
        elif question.question_type == QuestionType.SCALE:
            return QuestionService._validate_scale_response(question, response_value)
        elif question.question_type == QuestionType.FILE_UPLOAD:
            return QuestionService._validate_file_upload_response(question, response_value)
        
        return True, None
    
    @staticmethod
    def _validate_text_response(question: Question, response_value: str) -> tuple[bool, Optional[str]]:
        """Validate text response"""
        if not isinstance(response_value, str):
            return False, "Response must be a string"
        
        options = question.options or {}
        
        if "min_length" in options and len(response_value) < options["min_length"]:
            return False, f"Response must be at least {options['min_length']} characters"
        
        if "max_length" in options and len(response_value) > options["max_length"]:
            return False, f"Response must be at most {options['max_length']} characters"
        
        return True, None
    
    @staticmethod
    def _validate_multiple_choice_response(question: Question, response_value: Any) -> tuple[bool, Optional[str]]:
        """Validate multiple choice response"""
        options = question.options or {}
        choices = options.get("choices", [])
        allow_multiple = options.get("allow_multiple", False)
        
        if allow_multiple:
            if not isinstance(response_value, list):
                return False, "Response must be a list for multiple choice questions"
            
            if not all(choice in choices for choice in response_value):
                return False, "Invalid choice(s) selected"
        else:
            if not isinstance(response_value, str):
                return False, "Response must be a string for single choice questions"
            
            if response_value not in choices:
                return False, "Invalid choice selected"
        
        return True, None
    
    @staticmethod
    def _validate_scale_response(question: Question, response_value: Any) -> tuple[bool, Optional[str]]:
        """Validate scale response"""
        if not isinstance(response_value, (int, float)):
            return False, "Response must be a number"
        
        options = question.options or {}
        min_value = options.get("min_value", 1)
        max_value = options.get("max_value", 10)
        step = options.get("step", 1)
        
        if response_value < min_value or response_value > max_value:
            return False, f"Response must be between {min_value} and {max_value}"
        
        if step != 1 and (response_value - min_value) % step != 0:
            return False, f"Response must be in increments of {step}"
        
        return True, None
    
    @staticmethod
    def _validate_file_upload_response(question: Question, response_value: Any) -> tuple[bool, Optional[str]]:
        """Validate file upload response"""
        if not isinstance(response_value, (str, list)):
            return False, "Response must be a file path or list of file paths"
        
        options = question.options or {}
        max_files = options.get("max_files", 1)
        allowed_extensions = options.get("allowed_extensions", [".pdf"])
        
        file_paths = response_value if isinstance(response_value, list) else [response_value]
        
        if len(file_paths) > max_files:
            return False, f"Maximum {max_files} file(s) allowed"
        
        for file_path in file_paths:
            if not any(file_path.lower().endswith(ext.lower()) for ext in allowed_extensions):
                return False, f"Only {', '.join(allowed_extensions)} files are allowed"
        
        return True, None
    
    @staticmethod
    def get_question_default_options(question_type: QuestionType) -> Dict[str, Any]:
        """Get default options for a question type"""
        defaults = {
            QuestionType.TEXT: {
                "max_length": 1000,
                "min_length": 0,
                "placeholder": "Enter your answer...",
                "multiline": False
            },
            QuestionType.MULTIPLE_CHOICE: {
                "choices": ["Option 1", "Option 2"],
                "allow_multiple": False,
                "randomize_order": False
            },
            QuestionType.SCALE: {
                "min_value": 1,
                "max_value": 10,
                "step": 1,
                "min_label": "Poor",
                "max_label": "Excellent"
            },
            QuestionType.FILE_UPLOAD: {
                "max_file_size_mb": 50,
                "allowed_extensions": [".pdf"],
                "max_files": 1
            }
        }
        
        return defaults.get(question_type, {})
    
    @staticmethod
    def reorder_questions(db: Session, questionnaire_id: int, question_order: List[int]) -> bool:
        """Reorder questions in a questionnaire"""
        try:
            # Verify all questions belong to the questionnaire
            existing_questions = db.query(Question).filter(
                and_(
                    Question.questionnaire_id == questionnaire_id,
                    Question.id.in_(question_order)
                )
            ).all()
            
            if len(existing_questions) != len(question_order):
                return False
            
            # Update order_index for each question
            for new_index, question_id in enumerate(question_order):
                db.query(Question).filter(
                    Question.id == question_id
                ).update({
                    Question.order_index: new_index
                })
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    @staticmethod
    def get_next_order_index(db: Session, questionnaire_id: int) -> int:
        """Get the next order index for a new question"""
        max_order = db.query(Question).filter(
            Question.questionnaire_id == questionnaire_id
        ).count()
        
        return max_order