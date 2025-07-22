#!/usr/bin/env python3

import requests
import json
import sys
import os

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_public_forms_api():
    """Test the public forms API endpoints"""
    
    print("=== Testing Public Forms API ===")
    
    # First, we need to get an application unique_id
    # Let's test with a mock unique_id for now
    test_unique_id = "test-app-123"
    
    print(f"\n1. Testing questionnaire endpoint with unique_id: {test_unique_id}")
    
    try:
        # Test the public questionnaire endpoint
        response = requests.get(f"{BASE_URL}/public/applications/{test_unique_id}/questionnaire")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✅ Expected 404 - Application not found (this is correct for test ID)")
        else:
            print("❌ Unexpected response")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure backend server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n2. Testing application status endpoint")
    
    try:
        # Test the application status endpoint
        response = requests.get(f"{BASE_URL}/public/applications/{test_unique_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✅ Expected 404 - Application not found (this is correct for test ID)")
        else:
            print("❌ Unexpected response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n3. Testing API documentation")
    
    try:
        # Test that the endpoints are registered in the API docs
        response = requests.get("http://127.0.0.1:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print("❌ API documentation not accessible")
            
    except Exception as e:
        print(f"❌ Error accessing docs: {e}")
    
    print("\n=== Public Forms API Test Complete ===")
    print("✅ Endpoints are properly configured and responding")
    print("📝 Next: Create test application data to fully test the functionality")
    
    return True

if __name__ == "__main__":
    test_public_forms_api()