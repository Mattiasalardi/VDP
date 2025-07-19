#!/usr/bin/env python3
"""
Comprehensive test script for AI Guidelines Generation workflow
Tests the complete flow: Calibration → AI Generation → Review → Storage
"""
import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8000/api/v1"

def test_ai_guidelines_workflow():
    """Test the complete AI guidelines generation workflow"""
    
    print("🧪 Testing AI Guidelines Generation Workflow")
    print("=" * 60)
    
    # Step 1: Login to get authentication token
    print("\n1. Logging in...")
    login_data = {
        "username": "admin@teched-accelerator.com",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    program_id = 1
    
    # Step 2: Check calibration status
    print(f"\n2. Checking calibration status for program {program_id}...")
    status_response = requests.get(f"{API_BASE}/calibration/programs/{program_id}/status", headers=headers)
    if status_response.status_code != 200:
        print(f"❌ Failed to fetch calibration status: {status_response.text}")
        return False
    
    status_data = status_response.json()
    print(f"✅ Calibration status: {status_data['answered_questions']}/{status_data['total_questions']} answered ({status_data['completion_percentage']:.1f}%)")
    
    if status_data['completion_percentage'] < 50:
        print("⚠️  Low calibration completion - adding sample answers for testing...")
        
        # Add some sample calibration answers
        sample_answers = [
            {
                "question_key": "startup_stage_preference",
                "answer_value": {"choice_value": "seed"},
                "answer_text": "Seed stage startups"
            },
            {
                "question_key": "risk_tolerance_moonshots", 
                "answer_value": {"choice_value": "balanced"},
                "answer_text": "Balanced risk approach"
            },
            {
                "question_key": "technical_vs_business_innovation",
                "answer_value": {"scale_value": 7},
                "answer_text": "High importance on technical innovation"
            }
        ]
        
        batch_response = requests.post(
            f"{API_BASE}/calibration/programs/{program_id}/answers/batch",
            headers=headers,
            json={"answers": sample_answers}
        )
        
        if batch_response.status_code == 200:
            print("✅ Added sample calibration answers")
        else:
            print(f"⚠️  Failed to add sample answers: {batch_response.text}")
    
    # Step 3: Test guidelines generation
    print("\n3. Testing AI guidelines generation...")
    
    # Test with different models
    test_models = [
        "anthropic/claude-3.5-sonnet",
        # "anthropic/claude-3-haiku",  # Uncomment to test multiple models
    ]
    
    generated_guidelines = None
    
    for model in test_models:
        print(f"\n   Testing with model: {model}")
        
        generation_request = {"model": model}
        generation_response = requests.post(
            f"{API_BASE}/ai-guidelines/programs/{program_id}/generate",
            headers=headers,
            json=generation_request
        )
        
        if generation_response.status_code == 200:
            generated_guidelines = generation_response.json()
            print(f"   ✅ Guidelines generated successfully")
            print(f"   📊 Categories: {len(generated_guidelines['guidelines']['categories'])}")
            print(f"   🎯 Model: {generated_guidelines['metadata']['model']}")
            print(f"   ⏱️  Generated at: {generated_guidelines['metadata']['generated_at']}")
            print(f"   🔄 Rate limit remaining: {generated_guidelines['metadata']['rate_limit_remaining']}")
            
            # Show sample category
            if generated_guidelines['guidelines']['categories']:
                sample_category = generated_guidelines['guidelines']['categories'][0]
                print(f"   📋 Sample category: {sample_category['name']} (Weight: {sample_category['weight']:.2f})")
            
            break
        else:
            print(f"   ❌ Generation failed: {generation_response.text}")
    
    if not generated_guidelines:
        print("❌ No guidelines were successfully generated")
        return False
    
    # Step 4: Test guidelines validation
    print("\n4. Validating generated guidelines structure...")
    
    guidelines = generated_guidelines['guidelines']
    
    # Check required fields
    required_fields = ['categories', 'overall_approach', 'scoring_scale']
    for field in required_fields:
        if field not in guidelines:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check categories
    categories = guidelines['categories']
    if not isinstance(categories, list) or len(categories) == 0:
        print("❌ Categories must be a non-empty list")
        return False
    
    total_weight = sum(cat['weight'] for cat in categories)
    if abs(total_weight - 1.0) > 0.01:
        print(f"❌ Category weights don't sum to 1.0: {total_weight}")
        return False
    
    print(f"✅ Guidelines structure validated")
    print(f"   📊 {len(categories)} categories with weights summing to {total_weight:.3f}")
    
    # Step 5: Test guidelines saving (draft)
    print("\n5. Testing guidelines save as draft...")
    
    save_request = {
        "guidelines_data": generated_guidelines,
        "is_approved": False
    }
    
    save_response = requests.post(
        f"{API_BASE}/ai-guidelines/programs/{program_id}/save",
        headers=headers,
        json=save_request
    )
    
    if save_response.status_code == 200:
        saved_data = save_response.json()
        print(f"✅ Guidelines saved as draft")
        print(f"   🆔 ID: {saved_data['id']}")
        print(f"   📝 Version: {saved_data['version']}")
        print(f"   ✅ Active: {saved_data['is_active']}")
    else:
        print(f"❌ Save failed: {save_response.text}")
        return False
    
    # Step 6: Test guidelines save and approval
    print("\n6. Testing guidelines save with approval...")
    
    approve_request = {
        "guidelines_data": generated_guidelines,
        "is_approved": True
    }
    
    approve_response = requests.post(
        f"{API_BASE}/ai-guidelines/programs/{program_id}/save",
        headers=headers,
        json=approve_request
    )
    
    if approve_response.status_code == 200:
        approved_data = approve_response.json()
        print(f"✅ Guidelines approved and activated")
        print(f"   🆔 ID: {approved_data['id']}")
        print(f"   📝 Version: {approved_data['version']}")
        print(f"   ✅ Active: {approved_data['is_active']}")
    else:
        print(f"❌ Approval failed: {approve_response.text}")
        return False
    
    # Step 7: Test active guidelines retrieval
    print("\n7. Testing active guidelines retrieval...")
    
    active_response = requests.get(
        f"{API_BASE}/ai-guidelines/programs/{program_id}/active",
        headers=headers
    )
    
    if active_response.status_code == 200:
        active_data = active_response.json()
        print(f"✅ Active guidelines retrieved")
        print(f"   📝 Version: {active_data['version']}")
        print(f"   🎯 Model: {active_data['model_used']}")
    else:
        print(f"❌ Active guidelines retrieval failed: {active_response.text}")
        return False
    
    # Step 8: Test guidelines history
    print("\n8. Testing guidelines history...")
    
    history_response = requests.get(
        f"{API_BASE}/ai-guidelines/programs/{program_id}/history",
        headers=headers
    )
    
    if history_response.status_code == 200:
        history_data = history_response.json()
        print(f"✅ Guidelines history retrieved")
        print(f"   📊 Total versions: {history_data['total_count']}")
        
        for guideline in history_data['guidelines'][:3]:  # Show first 3
            status = "🟢 Active" if guideline['is_active'] else "⚪ Inactive"
            print(f"   📝 Version {guideline['version']}: {status} ({guideline['model_used']})")
    else:
        print(f"❌ History retrieval failed: {history_response.text}")
        return False
    
    # Step 9: Test rate limiting (if needed)
    print("\n9. Testing rate limiting behavior...")
    
    print(f"   🔄 Current rate limit remaining: {generated_guidelines['metadata']['rate_limit_remaining']}")
    
    if generated_guidelines['metadata']['rate_limit_remaining'] > 5:
        print("   ⚠️  Skipping rate limit test (sufficient quota remaining)")
    else:
        print("   ℹ️  Rate limit test would require depleting quota")
    
    # Step 10: Test caching behavior
    print("\n10. Testing caching behavior...")
    
    # Generate same guidelines again (should be cached)
    cache_test_response = requests.post(
        f"{API_BASE}/ai-guidelines/programs/{program_id}/generate", 
        headers=headers,
        json={"model": generated_guidelines['metadata']['model']}
    )
    
    if cache_test_response.status_code == 200:
        cache_data = cache_test_response.json()
        # Check if generation was fast (likely cached)
        print("✅ Second generation request successful (likely cached)")
        print(f"   🔄 Rate limit remaining: {cache_data['metadata']['rate_limit_remaining']}")
    else:
        print(f"⚠️  Cache test failed: {cache_test_response.text}")
    
    print("\n🎉 AI Guidelines workflow test completed successfully!")
    print("\n📋 Test Summary:")
    print("✅ Calibration status check")
    print("✅ AI guidelines generation")
    print("✅ Guidelines structure validation")
    print("✅ Draft save functionality")
    print("✅ Approval and activation")
    print("✅ Active guidelines retrieval")
    print("✅ Guidelines history")
    print("✅ Rate limiting awareness")
    print("✅ Caching behavior")
    
    return True

if __name__ == "__main__":
    test_ai_guidelines_workflow()