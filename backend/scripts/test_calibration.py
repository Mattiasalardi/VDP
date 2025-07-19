#!/usr/bin/env python3
"""
Test script for calibration functionality
"""
import requests
import json
from typing import Dict, Any

API_BASE = "http://localhost:8000/api/v1"

def test_calibration_workflow():
    """Test the complete calibration workflow"""
    
    print("🧪 Testing Calibration Workflow")
    print("=" * 50)
    
    # Step 1: Login to get authentication token
    print("\n1. Logging in...")
    login_data = {
        "username": "admin@teched-accelerator.com",  # OAuth2 form uses 'username' not 'email'
        "password": "admin123"
    }
    
    login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)  # Use form data, not JSON
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Get calibration questions
    print("\n2. Fetching calibration questions...")
    questions_response = requests.get(f"{API_BASE}/calibration/questions", headers=headers)
    if questions_response.status_code != 200:
        print(f"❌ Failed to fetch questions: {questions_response.text}")
        return False
    
    questions_data = questions_response.json()
    print(f"✅ Loaded {questions_data['total_questions']} calibration questions")
    print(f"   Categories: {list(questions_data['categories'].keys())}")
    
    # Step 3: Check calibration status for program 1
    program_id = 1
    print(f"\n3. Checking calibration status for program {program_id}...")
    status_response = requests.get(f"{API_BASE}/calibration/programs/{program_id}/status", headers=headers)
    if status_response.status_code != 200:
        print(f"❌ Failed to fetch status: {status_response.text}")
        return False
    
    status_data = status_response.json()
    print(f"✅ Status: {status_data['answered_questions']}/{status_data['total_questions']} answered ({status_data['completion_percentage']:.1f}%)")
    
    # Step 4: Submit a sample calibration answer
    print("\n4. Submitting a sample calibration answer...")
    sample_answer = {
        "question_key": "team_importance",
        "answer_value": {"scale_value": 8},
        "answer_text": "Team experience is very important"
    }
    
    answer_response = requests.post(
        f"{API_BASE}/calibration/programs/{program_id}/answers", 
        headers=headers,
        json=sample_answer
    )
    if answer_response.status_code != 200:
        print(f"❌ Failed to submit answer: {answer_response.text}")
        return False
    
    answer_data = answer_response.json()
    print(f"✅ Submitted answer for {answer_data['question_key']}")
    
    # Step 5: Submit batch answers
    print("\n5. Submitting batch calibration answers...")
    batch_answers = {
        "answers": [
            {
                "question_key": "market_size_preference",
                "answer_value": {"choice_value": "large_existing"},
                "answer_text": "Large existing markets with proven demand"
            },
            {
                "question_key": "technology_innovation",
                "answer_value": {"scale_value": 6},
                "answer_text": "Moderately important tech innovation"
            }
        ]
    }
    
    batch_response = requests.post(
        f"{API_BASE}/calibration/programs/{program_id}/answers/batch",
        headers=headers,
        json=batch_answers
    )
    if batch_response.status_code != 200:
        print(f"❌ Failed to submit batch answers: {batch_response.text}")
        return False
    
    batch_data = batch_response.json()
    print(f"✅ Submitted {len(batch_data)} batch answers")
    
    # Step 6: Check updated status
    print("\n6. Checking updated calibration status...")
    updated_status_response = requests.get(f"{API_BASE}/calibration/programs/{program_id}/status", headers=headers)
    if updated_status_response.status_code == 200:
        updated_status = updated_status_response.json()
        print(f"✅ Updated status: {updated_status['answered_questions']}/{updated_status['total_questions']} answered ({updated_status['completion_percentage']:.1f}%)")
    
    # Step 7: Get calibration session data
    print("\n7. Fetching complete calibration session...")
    session_response = requests.get(f"{API_BASE}/calibration/programs/{program_id}/session", headers=headers)
    if session_response.status_code == 200:
        session_data = session_response.json()
        print(f"✅ Session data: {len(session_data['answers'])} answers loaded")
        print(f"   Missing questions: {len(session_data['missing_questions'])}")
    
    print("\n🎉 Calibration workflow test completed successfully!")
    return True

if __name__ == "__main__":
    test_calibration_workflow()