#!/usr/bin/env python3
"""
Test script for Program Management system.
Tests program creation, listing, updating, and deletion.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@teched-accelerator.com"
TEST_PASSWORD = "admin123"

def test_programs():
    print("🧪 Testing Program Management System")
    print("="*50)
    
    # Authenticate
    print("🔐 Authenticating...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Authentication successful")
    
    # Test 1: Get existing programs
    print("\n📋 Testing program list...")
    response = requests.get(f"{BASE_URL}/api/v1/programs", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data.get('programs', []))} existing programs")
        for program in data.get('programs', []):
            print(f"   - {program['name']} (ID: {program['id']})")
    else:
        print(f"❌ Failed to get programs: {response.status_code}")
    
    # Test 2: Create new program
    print("\n➕ Testing program creation...")
    new_program = {
        "name": "AI Innovation Track 2024",
        "description": "Specialized program for AI and machine learning startups",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/programs", 
                           headers=headers, json=new_program)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            created_program = data['program']
            program_id = created_program['id']
            print(f"✅ Created program: {created_program['name']} (ID: {program_id})")
            
            # Test 3: Get specific program
            print(f"\n🔍 Testing program details (ID: {program_id})...")
            response = requests.get(f"{BASE_URL}/api/v1/programs/{program_id}", headers=headers)
            if response.status_code == 200:
                program_data = response.json()
                if program_data.get('success'):
                    program = program_data['program']
                    print(f"✅ Retrieved program details:")
                    print(f"   Name: {program['name']}")
                    print(f"   Questionnaires: {program['questionnaire_count']}")
                    print(f"   Calibration: {program['calibration_completion']:.1f}%")
                    print(f"   Guidelines: {program['has_active_guidelines']}")
                    print(f"   Applications: {program['application_count']}")
                else:
                    print(f"❌ Failed to get program details: {program_data.get('error')}")
            else:
                print(f"❌ Failed to get program details: {response.status_code}")
            
            # Test 4: Update program
            print(f"\n✏️  Testing program update...")
            update_data = {
                "description": "Updated: AI and ML startups with focus on enterprise solutions"
            }
            response = requests.put(f"{BASE_URL}/api/v1/programs/{program_id}",
                                  headers=headers, json=update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Program updated successfully")
                else:
                    print(f"❌ Failed to update program: {data.get('error')}")
            else:
                print(f"❌ Failed to update program: {response.status_code}")
            
            # Test 5: Soft delete program  
            print(f"\n🗑️  Testing program deletion...")
            response = requests.delete(f"{BASE_URL}/api/v1/programs/{program_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Program soft-deleted successfully")
                else:
                    print(f"❌ Failed to delete program: {data.get('error')}")
            else:
                print(f"❌ Failed to delete program: {response.status_code}")
        else:
            print(f"❌ Program creation failed: {data.get('error')}")
    else:
        print(f"❌ Program creation failed: {response.status_code} - {response.text}")
    
    print(f"\n🎉 Program management tests completed!")

if __name__ == "__main__":
    test_programs()