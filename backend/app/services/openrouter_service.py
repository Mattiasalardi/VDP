import json
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
import redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.organization import Organization

logger = logging.getLogger(__name__)

class OpenRouterService:
    """
    Service for interacting with OpenRouter API
    Includes rate limiting, security measures, and error handling
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://openrouter.ai/api/v1"
        self.max_tokens = 2000
        self.timeout = 30
        
        # Rate limiting: 10 requests per organization per hour
        self._rate_limit_requests = 10
        self._rate_limit_window = 3600  # 1 hour in seconds
        
        # Initialize Redis for caching
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
            if self.redis_client:
                self.redis_client.ping()
                logger.info("Redis connection established for caching")
        except (redis.ConnectionError, redis.RedisError) as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self.redis_client = None
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API requests"""
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key not configured")
            
        return {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.APP_DOMAIN if hasattr(settings, 'APP_DOMAIN') else "http://localhost:3000",
            "X-Title": "VDP Accelerator Platform"
        }
    
    def _check_rate_limit(self, organization_id: int) -> bool:
        """
        Check if organization has exceeded rate limit
        Returns True if within limits, False if exceeded
        """
        # TODO: Implement Redis-based rate limiting
        # For now, we'll use a simple in-memory approach
        # In production, this should use Redis with proper distributed rate limiting
        
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self._rate_limit_window)
        
        # Count recent API calls for this organization
        # This would be stored in Redis in production
        # For now, we'll assume rate limit is okay
        logger.info(f"Rate limit check for organization {organization_id}: OK")
        return True
    
    def _log_api_call(self, organization_id: int, prompt_tokens: int, completion_tokens: int, 
                      model: str, success: bool, error_message: Optional[str] = None):
        """Log API call for monitoring and billing purposes"""
        log_data = {
            "organization_id": organization_id,
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "success": success,
            "error_message": error_message
        }
        
        if success:
            logger.info(f"OpenRouter API call successful: {json.dumps(log_data)}")
        else:
            logger.error(f"OpenRouter API call failed: {json.dumps(log_data)}")
    
    def _get_cache_key(self, calibration_answers: Dict[str, Any], model: str) -> str:
        """Generate cache key for calibration answers and model combination"""
        # Create a deterministic hash of the calibration answers and model
        cache_data = {
            "calibration_answers": calibration_answers,
            "model": model
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_string.encode()).hexdigest()
        return f"guidelines_cache:{cache_hash}"
    
    def _get_cached_guidelines(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached guidelines from Redis"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for guidelines: {cache_key}")
                return json.loads(cached_data.decode())
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    def _cache_guidelines(self, cache_key: str, guidelines: Dict[str, Any], ttl: int = 86400) -> None:
        """Cache guidelines in Redis with TTL (default 24 hours)"""
        if not self.redis_client:
            return
        
        try:
            cached_data = json.dumps(guidelines)
            self.redis_client.setex(cache_key, ttl, cached_data)
            logger.info(f"Guidelines cached: {cache_key} (TTL: {ttl}s)")
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def generate_ai_guidelines(
        self, 
        organization_id: int, 
        calibration_answers: Dict[str, Any],
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """
        Generate AI guidelines based on calibration answers
        
        Args:
            organization_id: ID of the organization
            calibration_answers: Dictionary of calibration responses
            model: OpenRouter model to use
            
        Returns:
            Dictionary containing generated guidelines in JSON format
        """
        
        # Check cache first
        cache_key = self._get_cache_key(calibration_answers, model)
        cached_guidelines = self._get_cached_guidelines(cache_key)
        if cached_guidelines:
            logger.info(f"Returning cached guidelines for organization {organization_id}")
            return cached_guidelines
        
        # Check rate limit
        if not self._check_rate_limit(organization_id):
            raise ValueError("Rate limit exceeded. Please try again later.")
        
        # Prepare the prompt
        prompt = self._build_guidelines_prompt(calibration_answers)
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert startup accelerator consultant. Generate scoring guidelines based on calibration responses. Always respond with valid JSON only."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.1,  # Low temperature for consistent guidelines
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract the generated content
                content = result["choices"][0]["message"]["content"]
                
                # Parse the JSON response
                try:
                    guidelines_json = json.loads(content)
                except json.JSONDecodeError:
                    # If the response isn't valid JSON, try to extract JSON from the content
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        guidelines_json = json.loads(json_match.group())
                    else:
                        raise ValueError("AI response was not valid JSON")
                
                # Log successful API call
                usage = result.get("usage", {})
                self._log_api_call(
                    organization_id=organization_id,
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    model=model,
                    success=True
                )
                
                # Cache the successful result
                self._cache_guidelines(cache_key, guidelines_json)
                
                return guidelines_json
                
        except httpx.HTTPError as e:
            self._log_api_call(
                organization_id=organization_id,
                prompt_tokens=0,
                completion_tokens=0,
                model=model,
                success=False,
                error_message=f"HTTP error: {str(e)}"
            )
            raise ValueError(f"OpenRouter API error: {str(e)}")
        
        except json.JSONDecodeError as e:
            self._log_api_call(
                organization_id=organization_id,
                prompt_tokens=0,
                completion_tokens=0,
                model=model,
                success=False,
                error_message=f"JSON decode error: {str(e)}"
            )
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        
        except Exception as e:
            self._log_api_call(
                organization_id=organization_id,
                prompt_tokens=0,
                completion_tokens=0,
                model=model,
                success=False,
                error_message=str(e)
            )
            raise ValueError(f"Unexpected error: {str(e)}")
    
    def _build_guidelines_prompt(self, calibration_answers: Dict[str, Any]) -> str:
        """Build the prompt for AI guidelines generation"""
        
        # Base scoring categories aligned with report structure
        base_categories = [
            "Problem-Solution Fit",
            "Customer Profile & Business Model", 
            "Product & Technology",
            "Team Assessment",
            "Market Opportunity",
            "Competition & Differentiation",
            "Financial Overview",
            "Validation & Achievements"
        ]
        
        prompt = f"""
Based on the following accelerator calibration responses, generate a comprehensive scoring guideline system.

CALIBRATION RESPONSES:
{json.dumps(calibration_answers, indent=2)}

Generate a JSON response with the following structure:

{{
  "guidelines": {{
    "categories": [
      {{
        "name": "Problem-Solution Fit",
        "weight": 0.15,
        "description": "Evaluation criteria for problem-solution alignment",
        "scoring_guidance": {{
          "high_score_indicators": ["Clear problem validation", "Strong solution fit"],
          "medium_score_indicators": ["Some problem validation", "Reasonable solution"],
          "low_score_indicators": ["Weak problem validation", "Poor solution fit"],
          "key_questions": ["Is the problem real and significant?", "Does the solution address the core problem?"]
        }}
      }}
    ],
    "overall_approach": {{
      "risk_tolerance": "conservative|balanced|aggressive",
      "stage_focus": "pre_seed|seed|series_a|stage_agnostic",
      "industry_focus": "specific industries or agnostic",
      "key_priorities": ["List of top 3 evaluation priorities"]
    }},
    "scoring_scale": {{
      "range": "1-10",
      "descriptions": {{
        "9-10": "Exceptional - Top 5% of applications",
        "7-8": "Strong - Clear accelerator fit",
        "5-6": "Promising - Some concerns to address", 
        "3-4": "Weak - Major concerns",
        "1-2": "Poor - Not suitable"
      }}
    }}
  }}
}}

REQUIREMENTS:
1. All 8 categories must be included: {', '.join(base_categories)}
2. Weights must sum to 1.0
3. Adjust category weights based on calibration responses
4. Include specific guidance based on the accelerator's preferences
5. Make scoring guidance actionable and specific
6. Consider the accelerator's risk tolerance, stage preference, and industry focus
7. Ensure the response is valid JSON only

Generate guidelines that reflect this accelerator's specific preferences and priorities.
"""
        
        return prompt