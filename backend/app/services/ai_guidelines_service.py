import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.ai_guideline import AIGuideline
from app.models.calibration_answer import CalibrationAnswer
from app.schemas.calibration import CalibrationAnswerResponse
from app.services.openrouter_service import OpenRouterService
from app.services.rate_limiter import rate_limiter
from app.core.calibration_questions import CALIBRATION_QUESTIONS

logger = logging.getLogger(__name__)

class AIGuidelinesService:
    """
    Service for generating and managing AI scoring guidelines
    Handles the complete workflow: calibration → AI generation → review → storage
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.openrouter_service = OpenRouterService(db)
    
    def generate_guidelines(
        self, 
        program_id: int, 
        organization_id: int,
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """
        Generate AI guidelines based on calibration answers
        
        Args:
            program_id: Program ID to generate guidelines for
            organization_id: Organization ID for rate limiting
            model: OpenRouter model to use
            
        Returns:
            Dictionary containing generated guidelines and metadata
        """
        
        # Check rate limit (10 requests per organization per hour)
        rate_limit_key = f"org_{organization_id}_ai_guidelines"
        rate_limit_result = rate_limiter.check_rate_limit(rate_limit_key, limit=10, window_seconds=3600)
        
        if not rate_limit_result["allowed"]:
            raise ValueError(
                f"Rate limit exceeded. You can make {rate_limit_result['remaining']} more requests. "
                f"Rate limit resets at {datetime.fromtimestamp(rate_limit_result['reset_time']).strftime('%H:%M:%S')}"
            )
        
        # Get calibration answers for the program
        calibration_data = self._get_calibration_data(program_id)
        if not calibration_data:
            raise ValueError("No calibration answers found. Please complete the calibration questionnaire first.")
        
        # Generate guidelines using AI
        try:
            import asyncio
            guidelines_json = asyncio.run(
                self.openrouter_service.generate_ai_guidelines(
                    organization_id=organization_id,
                    calibration_answers=calibration_data,
                    model=model
                )
            )
            
            # Validate the generated guidelines
            validated_guidelines = self._validate_guidelines(guidelines_json)
            
            # Prepare response with metadata
            response = {
                "guidelines": validated_guidelines,
                "metadata": {
                    "program_id": program_id,
                    "organization_id": organization_id,
                    "model": model,
                    "generated_at": datetime.utcnow().isoformat(),
                    "calibration_questions_count": len(calibration_data),
                    "rate_limit_remaining": rate_limit_result["remaining"]
                },
                "calibration_summary": self._create_calibration_summary(calibration_data)
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Guidelines generation failed for program {program_id}: {str(e)}")
            raise ValueError(f"Failed to generate guidelines: {str(e)}")
    
    def save_guidelines(
        self, 
        program_id: int, 
        guidelines_data: Dict[str, Any],
        is_approved: bool = False
    ) -> AIGuideline:
        """
        Save guidelines to database with versioning
        
        Args:
            program_id: Program ID
            guidelines_data: Guidelines JSON data
            is_approved: Whether the guidelines are approved for use
            
        Returns:
            Saved AIGuideline instance
        """
        
        # Get current version number
        current_version = self._get_next_version_number(program_id)
        
        # Create new guideline entry
        guideline = AIGuideline(
            program_id=program_id,
            guidelines_json=guidelines_data["guidelines"],
            prompt_template=self._get_current_prompt_template(),
            model_used=guidelines_data.get("metadata", {}).get("model", "unknown"),
            version=current_version,
            is_active=is_approved,
            generated_at=datetime.utcnow()
        )
        
        # If this is being approved, deactivate other versions
        if is_approved:
            self.db.query(AIGuideline).filter(
                and_(
                    AIGuideline.program_id == program_id,
                    AIGuideline.is_active == True
                )
            ).update({"is_active": False})
        
        self.db.add(guideline)
        self.db.commit()
        self.db.refresh(guideline)
        
        logger.info(f"Guidelines saved for program {program_id}, version {current_version}, approved: {is_approved}")
        
        return guideline
    
    def get_active_guidelines(self, program_id: int) -> Optional[AIGuideline]:
        """Get the currently active guidelines for a program"""
        return (
            self.db.query(AIGuideline)
            .filter(
                and_(
                    AIGuideline.program_id == program_id,
                    AIGuideline.is_active == True
                )
            )
            .first()
        )
    
    def get_guidelines_history(self, program_id: int) -> List[AIGuideline]:
        """Get all guidelines versions for a program"""
        return (
            self.db.query(AIGuideline)
            .filter(AIGuideline.program_id == program_id)
            .order_by(AIGuideline.version.desc())
            .all()
        )
    
    def _get_calibration_data(self, program_id: int) -> Dict[str, Any]:
        """Get and format calibration answers for AI processing"""
        answers = (
            self.db.query(CalibrationAnswer)
            .filter(CalibrationAnswer.program_id == program_id)
            .all()
        )
        
        if not answers:
            return {}
        
        # Create a mapping of question keys to question details
        questions_map = {q["key"]: q for q in CALIBRATION_QUESTIONS}
        
        calibration_data = {}
        for answer in answers:
            question_info = questions_map.get(answer.question_key)
            if question_info:
                calibration_data[answer.question_key] = {
                    "question": question_info["question"],
                    "type": question_info["type"],
                    "answer_value": answer.answer_value,
                    "answer_text": answer.answer_text,
                    "description": question_info["description"]
                }
        
        return calibration_data
    
    def _validate_guidelines(self, guidelines_json: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated guidelines structure"""
        
        # Check required top-level keys
        required_keys = ["guidelines"]
        for key in required_keys:
            if key not in guidelines_json:
                raise ValueError(f"Missing required key: {key}")
        
        guidelines = guidelines_json["guidelines"]
        
        # Check required guideline keys
        required_guideline_keys = ["categories", "overall_approach", "scoring_scale"]
        for key in required_guideline_keys:
            if key not in guidelines:
                raise ValueError(f"Missing required guidelines key: {key}")
        
        # Validate categories
        categories = guidelines["categories"]
        if not isinstance(categories, list) or len(categories) == 0:
            raise ValueError("Categories must be a non-empty list")
        
        # Expected category names
        expected_categories = [
            "Problem-Solution Fit",
            "Customer Profile & Business Model",
            "Product & Technology", 
            "Team Assessment",
            "Market Opportunity",
            "Competition & Differentiation",
            "Financial Overview",
            "Validation & Achievements"
        ]
        
        # Validate each category
        total_weight = 0
        found_categories = []
        
        for category in categories:
            if not isinstance(category, dict):
                raise ValueError("Each category must be a dictionary")
            
            required_category_keys = ["name", "weight", "description", "scoring_guidance"]
            for key in required_category_keys:
                if key not in category:
                    raise ValueError(f"Missing required category key: {key}")
            
            found_categories.append(category["name"])
            
            # Validate weight
            weight = category["weight"]
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                raise ValueError(f"Category weight must be between 0 and 1, got: {weight}")
            
            total_weight += weight
        
        # Check if weights sum to approximately 1.0 (allow small floating point errors)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Category weights must sum to 1.0, got: {total_weight}")
        
        # Check if all expected categories are present
        missing_categories = set(expected_categories) - set(found_categories)
        if missing_categories:
            logger.warning(f"Missing expected categories: {missing_categories}")
        
        return guidelines_json
    
    def _create_calibration_summary(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a human-readable summary of calibration responses"""
        summary = {
            "total_questions_answered": len(calibration_data),
            "key_preferences": {},
            "risk_profile": "unknown",
            "stage_focus": "unknown",
            "industry_focus": "unknown"
        }
        
        # Extract key insights from calibration data
        for key, data in calibration_data.items():
            answer_value = data["answer_value"]
            
            if key == "risk_tolerance_moonshots":
                summary["risk_profile"] = answer_value.get("choice_value", "unknown")
            elif key == "startup_stage_preference":
                summary["stage_focus"] = answer_value.get("choice_value", "unknown")
            elif key == "industry_focus_preference":
                summary["industry_focus"] = answer_value.get("choice_value", "unknown")
            
            # Store simplified answer for display
            if "scale_value" in answer_value:
                summary["key_preferences"][key] = f"Scale: {answer_value['scale_value']}/10"
            elif "choice_value" in answer_value:
                summary["key_preferences"][key] = answer_value["choice_value"]
            elif "text_value" in answer_value:
                text = answer_value["text_value"][:100] + "..." if len(answer_value["text_value"]) > 100 else answer_value["text_value"]
                summary["key_preferences"][key] = text
        
        return summary
    
    def _get_next_version_number(self, program_id: int) -> int:
        """Get the next version number for guidelines"""
        latest = (
            self.db.query(AIGuideline)
            .filter(AIGuideline.program_id == program_id)
            .order_by(AIGuideline.version.desc())
            .first()
        )
        
        return (latest.version + 1) if latest else 1
    
    def _get_current_prompt_template(self) -> str:
        """Get the current prompt template for versioning"""
        # This could be loaded from a file or database
        # For now, we'll use a simple identifier
        return "v1.0_report_aligned_prompt"