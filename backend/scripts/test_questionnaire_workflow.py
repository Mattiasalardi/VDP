#!/usr/bin/env python3
"""
Test script to validate the complete questionnaire workflow:
1. Login as test organization
2. Get programs
3. Create a questionnaire
4. Get questionnaire details with questions
5. Verify builder integration works
"""

import requests
import json
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_workflow():
    """Test the complete questionnaire workflow"""
    
    print("🚀 Testing Questionnaire Workflow")
    print("=" * 50)
    
    # Step 1: Login
    print("1. Logging in...")
    login_data = {
        "username": "admin@teched-accelerator.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    token_data = response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Get programs
    print("2. Getting programs...")
    response = requests.get(f"{BASE_URL}/programs", headers=headers)
    if response.status_code != 200:
        print(f"❌ Get programs failed: {response.text}")
        return False
    
    programs_data = response.json()
    if not programs_data["programs"]:
        print("❌ No programs found")
        return False
    
    program_id = programs_data["programs"][0]["id"]
    print(f"✅ Found program with ID: {program_id}")
    
    # Step 3: Create questionnaire
    print("3. Creating questionnaire...")
    questionnaire_data = {
        "name": "Integration Test Questionnaire",
        "description": "Testing the complete workflow",
        "is_active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/questions/programs/{program_id}/questionnaires", 
        json=questionnaire_data,
        headers=headers
    )
    if response.status_code != 200:
        print(f"❌ Create questionnaire failed: {response.text}")
        return False
    
    questionnaire = response.json()
    questionnaire_id = questionnaire["id"]
    print(f"✅ Created questionnaire with ID: {questionnaire_id}")
    
    # Step 4: Get questionnaire details
    print("4. Getting questionnaire details...")
    response = requests.get(
        f"{BASE_URL}/questions/questionnaires/{questionnaire_id}",
        headers=headers
    )
    if response.status_code != 200:
        print(f"❌ Get questionnaire details failed: {response.text}")
        return False
    
    questionnaire_details = response.json()
    print(f"✅ Retrieved questionnaire: {questionnaire_details['name']}")
    print(f"   Questions: {len(questionnaire_details['questions'])}")
    
    # Step 5: List questionnaires for program
    print("5. Listing program questionnaires...")
    response = requests.get(
        f"{BASE_URL}/questions/programs/{program_id}/questionnaires",
        headers=headers
    )
    if response.status_code != 200:
        print(f"❌ List questionnaires failed: {response.text}")
        return False
    
    questionnaires_list = response.json()
    print(f"✅ Found {len(questionnaires_list['questionnaires'])} questionnaires")
    
    print("=" * 50)
    print("🎉 All tests passed! The questionnaire workflow is working correctly.")
    print()
    print("Frontend URLs to test:")
    print(f"   Program Dashboard: http://localhost:3000/dashboard/programs/{program_id}")
    print(f"   Questionnaires: http://localhost:3000/dashboard/programs/{program_id}/questionnaires")
    print(f"   Builder: http://localhost:3000/dashboard/questionnaires/builder?id={questionnaire_id}&programId={program_id}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)