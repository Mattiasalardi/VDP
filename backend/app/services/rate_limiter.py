import time
import json
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Redis-based rate limiter for API calls
    Implements sliding window rate limiting
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
            if self.redis_client:
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established for rate limiting")
        except (redis.ConnectionError, redis.RedisError) as e:
            logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
            self.redis_client = None
            # Fallback to in-memory storage (not production-ready for multiple instances)
            self._memory_store: Dict[str, list] = {}
    
    def check_rate_limit(
        self, 
        key: str, 
        limit: int = 10, 
        window_seconds: int = 3600
    ) -> Dict[str, any]:
        """
        Check if the rate limit has been exceeded
        
        Args:
            key: Unique identifier (e.g., f"org_{organization_id}_ai_calls")
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Dict with 'allowed' (bool), 'remaining' (int), 'reset_time' (int)
        """
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        if self.redis_client:
            return self._redis_rate_limit(key, limit, window_seconds, current_time, window_start)
        else:
            return self._memory_rate_limit(key, limit, window_seconds, current_time, window_start)
    
    def _redis_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int, 
        current_time: int, 
        window_start: int
    ) -> Dict[str, any]:
        """Redis-based rate limiting implementation"""
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current entries in the window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration for cleanup
            pipe.expire(key, window_seconds)
            
            results = pipe.execute()
            
            current_count = results[1]  # Count after removing old entries
            
            if current_count < limit:
                remaining = limit - current_count - 1  # -1 for the current request we just added
                reset_time = current_time + window_seconds
                
                return {
                    "allowed": True,
                    "remaining": max(0, remaining),
                    "reset_time": reset_time,
                    "current_count": current_count + 1
                }
            else:
                # Remove the request we just added since it's not allowed
                self.redis_client.zrem(key, str(current_time))
                
                # Find when the oldest request will expire
                oldest_entries = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_time = int(oldest_entries[0][1])
                    reset_time = oldest_time + window_seconds
                else:
                    reset_time = current_time + window_seconds
                
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time,
                    "current_count": current_count
                }
                
        except redis.RedisError as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fall back to allowing the request if Redis fails
            return {
                "allowed": True,
                "remaining": limit - 1,
                "reset_time": current_time + window_seconds,
                "current_count": 1
            }
    
    def _memory_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int, 
        current_time: int, 
        window_start: int
    ) -> Dict[str, any]:
        """In-memory rate limiting fallback (not suitable for production with multiple instances)"""
        
        if key not in self._memory_store:
            self._memory_store[key] = []
        
        # Remove old entries
        self._memory_store[key] = [
            timestamp for timestamp in self._memory_store[key] 
            if timestamp > window_start
        ]
        
        current_count = len(self._memory_store[key])
        
        if current_count < limit:
            self._memory_store[key].append(current_time)
            remaining = limit - current_count - 1
            reset_time = current_time + window_seconds
            
            return {
                "allowed": True,
                "remaining": max(0, remaining),
                "reset_time": reset_time,
                "current_count": current_count + 1
            }
        else:
            # Find reset time based on oldest entry
            if self._memory_store[key]:
                oldest_time = min(self._memory_store[key])
                reset_time = oldest_time + window_seconds
            else:
                reset_time = current_time + window_seconds
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": reset_time,
                "current_count": current_count
            }
    
    def get_current_usage(self, key: str, window_seconds: int = 3600) -> int:
        """Get current usage count for a key"""
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        if self.redis_client:
            try:
                # Remove old entries and count current ones
                self.redis_client.zremrangebyscore(key, 0, window_start)
                return self.redis_client.zcard(key)
            except redis.RedisError as e:
                logger.error(f"Redis usage check error: {e}")
                return 0
        else:
            if key not in self._memory_store:
                return 0
            
            # Remove old entries and count current ones
            self._memory_store[key] = [
                timestamp for timestamp in self._memory_store[key] 
                if timestamp > window_start
            ]
            return len(self._memory_store[key])

# Global rate limiter instance
rate_limiter = RateLimiter()