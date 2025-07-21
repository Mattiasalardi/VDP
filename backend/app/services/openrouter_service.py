"""
OpenRouter API service for AI-powered guidelines generation.
Provides secure integration with OpenRouter API using developer-configurable models.
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
import asyncio
import httpx
from datetime import datetime, timedelta

from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Service for interacting with OpenRouter API for AI guidelines generation."""
    
    # Developer-configurable model options
    SUPPORTED_MODELS = {
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-3-opus": "anthropic/claude-3-opus", 
        "claude-3-haiku": "anthropic/claude-3-haiku",
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini"
    }
    
    # Default model for guidelines generation
    DEFAULT_MODEL = "claude-3.5-sonnet"
    
    # Request limits
    MAX_TOKENS = 2000
    REQUEST_TIMEOUT = 30.0
    
    def __init__(self):
        """Initialize OpenRouter service."""
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings.OPENROUTER_API_KEY
        self.app_domain = settings.APP_DOMAIN
        
        # Simple in-memory cache for guidelines
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(hours=24)
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not configured")
    
    def _get_cache_key(self, calibration_data: Dict[str, Any], model: str) -> str:
        """Generate cache key from calibration data and model."""
        cache_content = json.dumps(calibration_data, sort_keys=True) + model
        return hashlib.md5(cache_content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        
        cache_time = datetime.fromisoformat(cached_at)
        return datetime.now() - cache_time < self._cache_ttl
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for OpenRouter API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.app_domain,
            "X-Title": "VDP Application Platform"
        }
    
    def _build_guidelines_prompt(self, calibration_data: Dict[str, Any]) -> str:
        """Build AI prompt for guidelines generation based on calibration data."""
        
        # Extract key calibration preferences
        preferences = {
            "startup_stage": calibration_data.get("startup_stage", "any"),
            "risk_tolerance": calibration_data.get("risk_tolerance", "moderate"),
            "innovation_focus": calibration_data.get("innovation_focus", "balanced"),
            "team_importance": calibration_data.get("team_assessment_priority", "high"),
            "market_size_preference": calibration_data.get("minimum_market_size", "medium"),
            "revenue_requirements": calibration_data.get("revenue_stage_preference", "flexible"),
            "validation_standards": calibration_data.get("minimum_validation_level", "moderate")
        }
        
        prompt = f"""You are an expert startup accelerator evaluator. Based on these accelerator preferences, generate comprehensive AI guidelines for evaluating startup applications:

ACCELERATOR PREFERENCES:
- Startup Stage Preference: {preferences['startup_stage']}
- Risk Tolerance: {preferences['risk_tolerance']}
- Innovation Focus: {preferences['innovation_focus']}
- Team Assessment Priority: {preferences['team_importance']}
- Market Size Preference: {preferences['market_size_preference']}
- Revenue Requirements: {preferences['revenue_requirements']}
- Validation Standards: {preferences['validation_standards']}

Generate guidelines for these 8 evaluation categories, adjusting weights based on the preferences above:

1. Problem-Solution Fit
2. Customer Profile & Business Model
3. Product & Technology
4. Team Assessment
5. Market Opportunity
6. Competition & Differentiation
7. Financial Overview
8. Validation & Achievements

For each category, provide:
- Weight (1-10 integer, higher = more important)
- Key evaluation criteria (3-5 bullet points)
- Red flags to watch for (2-3 bullet points)
- Scoring guidance for 1-10 scale

Respond with ONLY a valid JSON object in this exact format:
{{
  "categories": [
    {{
      "section": "problem_solution_fit",
      "name": "Problem-Solution Fit", 
      "weight": 8,
      "criteria": [
        "Clear problem definition and market pain point identification",
        "Solution directly addresses the identified problem",
        "Evidence of product-market fit or strong validation"
      ],
      "red_flags": [
        "Vague or non-existent problem definition",
        "Solution seems to be searching for a problem"
      ],
      "scoring_guide": {{
        "1-3": "Poor problem-solution alignment",
        "4-5": "Basic understanding but unclear fit",
        "6-7": "Good alignment with some validation", 
        "8-10": "Excellent fit with strong validation"
      }}
    }}
  ]
}}

Adjust weights based on accelerator preferences - higher weights for categories that align with their priorities."""

        return prompt
    
    async def generate_guidelines(
        self, 
        calibration_data: Dict[str, Any], 
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI guidelines based on calibration data.
        
        Args:
            calibration_data: Calibration responses from accelerator
            model: OpenRouter model to use (defaults to claude-3.5-sonnet)
            
        Returns:
            Dict containing generated guidelines
            
        Raises:
            Exception: If API call fails or response is invalid
        """
        if not self.api_key:
            raise Exception("OpenRouter API key not configured")
        
        # Use default model if none specified
        if not model:
            model = self.DEFAULT_MODEL
        
        # Check cache first
        cache_key = self._get_cache_key(calibration_data, model)
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
            logger.info(f"Returning cached guidelines for key: {cache_key[:8]}...")
            return self._cache[cache_key]["guidelines"]
        
        # Validate model
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model: {model}. Supported: {list(self.SUPPORTED_MODELS.keys())}")
        
        # Build prompt
        prompt = self._build_guidelines_prompt(calibration_data)
        
        # Prepare request
        openrouter_model = self.SUPPORTED_MODELS[model]
        payload = {
            "model": openrouter_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.MAX_TOKENS,
            "temperature": 0.1  # Low temperature for consistent output
        }
        
        headers = self._get_headers()
        
        try:
            logger.info(f"Generating guidelines using model: {openrouter_model}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.REQUEST_TIMEOUT
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                response_data = response.json()
                
                # Extract content from response
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content:
                    raise Exception("Empty response from OpenRouter API")
                
                # Parse JSON response
                try:
                    guidelines = json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON from response if wrapped in markdown
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        guidelines = json.loads(json_match.group(1))
                    else:
                        # Attempt to find JSON object in text
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            guidelines = json.loads(json_match.group(0))
                        else:
                            raise Exception(f"Invalid JSON response: {content[:200]}...")
                
                # Validate response structure
                if not isinstance(guidelines, dict) or "categories" not in guidelines:
                    raise Exception("Invalid guidelines structure - missing 'categories' key")
                
                # Cache successful result
                self._cache[cache_key] = {
                    "guidelines": guidelines,
                    "cached_at": datetime.now().isoformat()
                }
                
                logger.info(f"Generated guidelines with {len(guidelines.get('categories', []))} categories")
                return guidelines
                
        except httpx.TimeoutException:
            error_msg = f"OpenRouter API timeout after {self.REQUEST_TIMEOUT}s"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.RequestError as e:
            error_msg = f"OpenRouter API request error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Guidelines generation failed: {str(e)}")
            raise
    
    def clear_cache(self) -> None:
        """Clear the guidelines cache."""
        self._cache.clear()
        logger.info("Guidelines cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        valid_entries = 0
        total_entries = len(self._cache)
        
        for entry in self._cache.values():
            if self._is_cache_valid(entry):
                valid_entries += 1
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries
        }

# Global service instance
openrouter_service = OpenRouterService()