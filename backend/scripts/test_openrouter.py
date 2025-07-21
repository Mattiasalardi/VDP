#!/usr/bin/env python3
"""
Test script for OpenRouter API integration.
Verifies that the API key is working and can make requests.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import httpx
from app.core.config import settings

async def test_openrouter_connection():
    """Test basic OpenRouter API connectivity."""
    
    print("🔧 Testing OpenRouter API Integration")
    print("="*50)
    
    # Check if API key is configured
    if not settings.OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return False
    
    # Mask API key for logging (show first 6 chars and last 4 chars)
    masked_key = f"{settings.OPENROUTER_API_KEY[:6]}...{settings.OPENROUTER_API_KEY[-4:]}"
    print(f"✅ API Key configured: {masked_key}")
    
    # Test API connection with a simple request
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.APP_DOMAIN,
        "X-Title": "VDP Application Platform"
    }
    
    # Simple test payload
    test_payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {"role": "user", "content": "Hello, please respond with just 'API connection successful'"}
        ],
        "max_tokens": 50
    }
    
    try:
        print("🔄 Testing API connection...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ API Connection Successful!")
                print(f"📝 Response: {message}")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting OpenRouter API Test\n")
    
    success = await test_openrouter_connection()
    
    if success:
        print("\n🎉 All tests passed! OpenRouter integration is working.")
    else:
        print("\n🚨 Tests failed. Please check your API key and network connection.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())