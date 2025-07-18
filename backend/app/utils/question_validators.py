from typing import Any, Dict, List, Optional, Union
from enum import Enum
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class QuestionValidators:
    """Collection of validation functions for different question types"""
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 0, max_length: int = 10000) -> bool:
        """Validate text length constraints"""
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        
        if len(text) < min_length:
            raise ValidationError(f"Text must be at least {min_length} characters long")
        
        if len(text) > max_length:
            raise ValidationError(f"Text must be at most {max_length} characters long")
        
        return True
    
    @staticmethod
    def validate_multiple_choice_options(choices: List[str], allow_duplicates: bool = False) -> bool:
        """Validate multiple choice options"""
        if not isinstance(choices, list):
            raise ValidationError("Choices must be a list")
        
        if len(choices) < 2:
            raise ValidationError("At least 2 choices are required")
        
        if len(choices) > 20:
            raise ValidationError("Maximum 20 choices allowed")
        
        if not allow_duplicates and len(choices) != len(set(choices)):
            raise ValidationError("Duplicate choices are not allowed")
        
        for choice in choices:
            if not isinstance(choice, str):
                raise ValidationError("All choices must be strings")
            
            if len(choice.strip()) == 0:
                raise ValidationError("Choices cannot be empty")
            
            if len(choice) > 200:
                raise ValidationError("Choice text cannot exceed 200 characters")
        
        return True
    
    @staticmethod
    def validate_scale_range(min_value: int, max_value: int, step: int = 1) -> bool:
        """Validate scale range parameters"""
        if not isinstance(min_value, int) or not isinstance(max_value, int):
            raise ValidationError("Scale values must be integers")
        
        if min_value >= max_value:
            raise ValidationError("Maximum value must be greater than minimum value")
        
        if min_value < 1 or max_value > 10:
            raise ValidationError("Scale values must be between 1 and 10")
        
        if step < 1:
            raise ValidationError("Step must be at least 1")
        
        if (max_value - min_value) % step != 0:
            raise ValidationError("Step must evenly divide the range")
        
        return True
    
    @staticmethod
    def validate_file_extensions(extensions: List[str]) -> bool:
        """Validate file extension list"""
        if not isinstance(extensions, list):
            raise ValidationError("Extensions must be a list")
        
        if len(extensions) == 0:
            raise ValidationError("At least one file extension is required")
        
        allowed_extensions = [".pdf", ".doc", ".docx", ".txt", ".jpg", ".jpeg", ".png"]
        
        for ext in extensions:
            if not isinstance(ext, str):
                raise ValidationError("Extensions must be strings")
            
            if not ext.startswith("."):
                raise ValidationError("Extensions must start with a dot")
            
            if ext.lower() not in allowed_extensions:
                raise ValidationError(f"Extension {ext} is not allowed")
        
        return True
    
    @staticmethod
    def validate_file_size_limit(size_mb: int) -> bool:
        """Validate file size limit"""
        if not isinstance(size_mb, int):
            raise ValidationError("File size must be an integer")
        
        if size_mb < 1:
            raise ValidationError("File size must be at least 1 MB")
        
        if size_mb > 100:
            raise ValidationError("File size cannot exceed 100 MB")
        
        return True
    
    @staticmethod
    def validate_question_text(text: str) -> bool:
        """Validate question text"""
        if not isinstance(text, str):
            raise ValidationError("Question text must be a string")
        
        if len(text.strip()) == 0:
            raise ValidationError("Question text cannot be empty")
        
        if len(text) > 1000:
            raise ValidationError("Question text cannot exceed 1000 characters")
        
        # Check for basic HTML/script injection
        if re.search(r'<script|<iframe|javascript:', text, re.IGNORECASE):
            raise ValidationError("Question text contains potentially unsafe content")
        
        return True
    
    @staticmethod
    def validate_order_index(order_index: int, max_questions: int = 50) -> bool:
        """Validate question order index"""
        if not isinstance(order_index, int):
            raise ValidationError("Order index must be an integer")
        
        if order_index < 0:
            raise ValidationError("Order index cannot be negative")
        
        if order_index >= max_questions:
            raise ValidationError(f"Order index cannot exceed {max_questions - 1}")
        
        return True
    
    @staticmethod
    def validate_question_limit(current_count: int, max_questions: int = 50) -> bool:
        """Validate question count limit"""
        if current_count >= max_questions:
            raise ValidationError(f"Maximum {max_questions} questions allowed per questionnaire")
        
        return True
    
    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """Sanitize text input to prevent XSS and other issues"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove potentially dangerous characters and patterns
        sanitized = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<iframe.*?</iframe>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str] = None) -> bool:
        """Validate JSON structure for options and validation rules"""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        if required_fields:
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return True


class QuestionTypeValidators:
    """Question type-specific validation functions"""
    
    @staticmethod
    def validate_text_question_options(options: Dict[str, Any]) -> bool:
        """Validate text question options"""
        QuestionValidators.validate_json_structure(options)
        
        if "max_length" in options:
            max_length = options["max_length"]
            if not isinstance(max_length, int) or max_length < 1 or max_length > 10000:
                raise ValidationError("max_length must be between 1 and 10000")
        
        if "min_length" in options:
            min_length = options["min_length"]
            if not isinstance(min_length, int) or min_length < 0:
                raise ValidationError("min_length must be non-negative")
        
        if "max_length" in options and "min_length" in options:
            if options["min_length"] >= options["max_length"]:
                raise ValidationError("min_length must be less than max_length")
        
        if "placeholder" in options:
            if not isinstance(options["placeholder"], str):
                raise ValidationError("placeholder must be a string")
        
        if "multiline" in options:
            if not isinstance(options["multiline"], bool):
                raise ValidationError("multiline must be a boolean")
        
        return True
    
    @staticmethod
    def validate_multiple_choice_question_options(options: Dict[str, Any]) -> bool:
        """Validate multiple choice question options"""
        QuestionValidators.validate_json_structure(options, ["choices"])
        
        QuestionValidators.validate_multiple_choice_options(options["choices"])
        
        if "allow_multiple" in options:
            if not isinstance(options["allow_multiple"], bool):
                raise ValidationError("allow_multiple must be a boolean")
        
        if "randomize_order" in options:
            if not isinstance(options["randomize_order"], bool):
                raise ValidationError("randomize_order must be a boolean")
        
        return True
    
    @staticmethod
    def validate_scale_question_options(options: Dict[str, Any]) -> bool:
        """Validate scale question options"""
        QuestionValidators.validate_json_structure(options, ["min_value", "max_value"])
        
        min_value = options["min_value"]
        max_value = options["max_value"]
        step = options.get("step", 1)
        
        QuestionValidators.validate_scale_range(min_value, max_value, step)
        
        if "min_label" in options:
            if not isinstance(options["min_label"], str):
                raise ValidationError("min_label must be a string")
        
        if "max_label" in options:
            if not isinstance(options["max_label"], str):
                raise ValidationError("max_label must be a string")
        
        return True
    
    @staticmethod
    def validate_file_upload_question_options(options: Dict[str, Any]) -> bool:
        """Validate file upload question options"""
        QuestionValidators.validate_json_structure(options)
        
        if "max_file_size_mb" in options:
            QuestionValidators.validate_file_size_limit(options["max_file_size_mb"])
        
        if "allowed_extensions" in options:
            QuestionValidators.validate_file_extensions(options["allowed_extensions"])
        
        if "max_files" in options:
            max_files = options["max_files"]
            if not isinstance(max_files, int) or max_files < 1 or max_files > 5:
                raise ValidationError("max_files must be between 1 and 5")
        
        return True