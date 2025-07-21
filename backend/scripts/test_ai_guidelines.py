#!/usr/bin/env python3
"""
Comprehensive test script for AI guidelines system.
Tests the complete flow from calibration data to guidelines generation,
storage, versioning, and activation workflow.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncio
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "admin@teched-accelerator.com"
TEST_PASSWORD = "admin123"

def print_section(title):
    """Print a test section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step):
    """Print a test step."""
    print(f"\n🔸 {step}")

def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")

class AIGuidelinesTestSuite:
    """Test suite for AI guidelines system."""
    
    def __init__(self):
        """Initialize test suite."""
        self.access_token = None
        self.organization_id = None
        self.program_id = 1  # Assuming test program exists
        
    def login(self):
        """Authenticate and get access token."""
        print_step("Authenticating test user")
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            print_success("Authentication successful")
            return True
        else:
            print_error(f"Authentication failed: {response.status_code} - {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_calibration_data(self):
        """Test calibration data availability."""
        print_step("Checking calibration data")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/calibration/programs/{self.program_id}/status",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("is_complete"):
                print_success(f"Calibration complete: {data.get('completion_percentage', 0):.1f}%")
                return True
            else:
                print_info(f"Calibration incomplete: {data.get('completion_percentage', 0):.1f}%")
                print_info("Creating sample calibration data...")
                return self.create_sample_calibration()
        else:
            print_error(f"Failed to check calibration: {response.status_code}")
            return False
    
    def create_sample_calibration(self):
        """Create sample calibration data."""
        sample_answers = [
            {"question_id": "startup_stage", "answer_value": "early_stage"},
            {"question_id": "risk_tolerance", "answer_value": "high"},
            {"question_id": "innovation_focus", "answer_value": "technology"},
            {"question_id": "team_assessment_priority", "answer_value": "high"},
            {"question_id": "minimum_market_size", "answer_value": "large"},
            {"question_id": "revenue_stage_preference", "answer_value": "flexible"},
            {"question_id": "minimum_validation_level", "answer_value": "strong"}
        ]
        
        for answer in sample_answers:
            response = requests.post(
                f"{BASE_URL}/api/v1/calibration/programs/{self.program_id}/answers",
                headers=self.get_headers(),
                json={
                    "question_key": answer["question_id"],
                    "answer_value": answer["answer_value"]
                }
            )
            
            if response.status_code != 200:
                print_error(f"Failed to create calibration answer: {answer['question_id']}")
                return False
        
        print_success("Sample calibration data created")
        return True
    
    async def test_guidelines_generation(self):
        """Test AI guidelines generation."""
        print_step("Testing guidelines generation")
        
        # Test with different models
        test_models = ["claude-3.5-sonnet", "claude-3-haiku"]
        
        for model in test_models:
            print_info(f"Testing with model: {model}")
            
            response = requests.post(
                f"{BASE_URL}/api/v1/ai-guidelines/generate?program_id={self.program_id}",
                headers=self.get_headers(),
                json={
                    "calibration_data": {},  # Service will fetch from database
                    "model": model
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    guidelines = data.get("guidelines", {})
                    categories = guidelines.get("categories", [])
                    print_success(f"Generated {len(categories)} guideline categories using {model}")
                    
                    # Show sample category
                    if categories:
                        sample = categories[0]
                        print_info(f"Sample category: {sample.get('name')} (weight: {sample.get('weight')})")
                    
                    return guidelines
                else:
                    print_error(f"Generation failed: {data.get('error')}")
            else:
                print_error(f"API call failed: {response.status_code} - {response.text}")
        
        return None
    
    def test_guidelines_saving(self, guidelines):
        """Test guidelines saving and versioning."""
        print_step("Testing guidelines saving and versioning")
        
        if not guidelines:
            print_error("No guidelines to save")
            return False
        
        # Save as draft first
        response = requests.post(
            f"{BASE_URL}/api/v1/ai-guidelines/save?program_id={self.program_id}",
            headers=self.get_headers(),
            json={
                "guidelines": guidelines,
                "is_active": False,
                "notes": "Test draft version"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                saved_guidelines = data.get("guidelines", {})
                version = saved_guidelines.get("version")
                print_success(f"Saved guidelines as draft version {version}")
                
                # Save and activate another version
                response2 = requests.post(
                    f"{BASE_URL}/api/v1/ai-guidelines/save?program_id={self.program_id}",
                    headers=self.get_headers(),
                    json={
                        "guidelines": guidelines,
                        "is_active": True,
                        "notes": "Test active version"
                    }
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get("success"):
                        active_version = data2.get("guidelines", {}).get("version")
                        print_success(f"Saved and activated guidelines version {active_version}")
                        return True
        
        print_error("Failed to save guidelines")
        return False
    
    def test_guidelines_history(self):
        """Test guidelines history retrieval."""
        print_step("Testing guidelines history")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/ai-guidelines/history?program_id={self.program_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                guidelines_list = data.get("guidelines", [])
                active_version = data.get("active_version")
                
                print_success(f"Retrieved {len(guidelines_list)} guideline versions")
                print_info(f"Active version: {active_version}")
                
                for guidelines in guidelines_list:
                    version = guidelines.get("version")
                    is_active = guidelines.get("is_active")
                    categories_count = len(guidelines.get("guidelines", {}).get("categories", []))
                    status = "ACTIVE" if is_active else "INACTIVE"
                    print_info(f"  Version {version}: {categories_count} categories ({status})")
                
                return len(guidelines_list) > 0
        
        print_error("Failed to retrieve guidelines history")
        return False
    
    def test_guidelines_activation(self):
        """Test guidelines version activation."""
        print_step("Testing guidelines activation workflow")
        
        # Get history first to find a version to activate
        response = requests.get(
            f"{BASE_URL}/api/v1/ai-guidelines/history?program_id={self.program_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            guidelines_list = data.get("guidelines", [])
            
            if len(guidelines_list) < 2:
                print_info("Need at least 2 versions to test activation")
                return True
            
            # Find an inactive version to activate
            inactive_version = None
            for guidelines in guidelines_list:
                if not guidelines.get("is_active"):
                    inactive_version = guidelines.get("version")
                    break
            
            if inactive_version:
                print_info(f"Activating version {inactive_version}")
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/ai-guidelines/activate?program_id={self.program_id}",
                    headers=self.get_headers(),
                    json={"version": inactive_version}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        activated_version = data.get("activated_version")
                        print_success(f"Successfully activated version {activated_version}")
                        return True
            
            print_info("No inactive version found to activate")
            return True
        
        print_error("Failed to test activation")
        return False
    
    def test_active_guidelines_retrieval(self):
        """Test active guidelines retrieval."""
        print_step("Testing active guidelines retrieval")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/ai-guidelines/active?program_id={self.program_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            active_guidelines = response.json()
            if active_guidelines:
                version = active_guidelines.get("version")
                categories = active_guidelines.get("guidelines", {}).get("categories", [])
                print_success(f"Retrieved active guidelines version {version} with {len(categories)} categories")
                return True
            else:
                print_info("No active guidelines found")
                return True
        
        print_error("Failed to retrieve active guidelines")
        return False
    
    def test_guidelines_status(self):
        """Test guidelines system status."""
        print_step("Testing guidelines system status")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/ai-guidelines/status?program_id={self.program_id}",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                has_active = data.get("has_active_guidelines")
                active_version = data.get("active_version")
                total_versions = data.get("total_versions")
                cache_stats = data.get("cache_stats", {})
                
                print_success("Guidelines system status:")
                print_info(f"  Has active guidelines: {has_active}")
                print_info(f"  Active version: {active_version}")
                print_info(f"  Total versions: {total_versions}")
                print_info(f"  Cache entries: {cache_stats.get('total_entries', 0)}")
                print_info(f"  Valid cache entries: {cache_stats.get('valid_entries', 0)}")
                
                return True
        
        print_error("Failed to get system status")
        return False
    
    async def run_all_tests(self):
        """Run the complete test suite."""
        print_section("AI GUIDELINES SYSTEM TEST SUITE")
        print_info(f"Testing against: {BASE_URL}")
        print_info(f"Test user: {TEST_EMAIL}")
        print_info(f"Program ID: {self.program_id}")
        
        # Track test results
        tests = []
        
        # Authentication
        tests.append(("Authentication", self.login()))
        
        if not self.access_token:
            print_error("Cannot continue without authentication")
            return
        
        # Calibration data check
        tests.append(("Calibration Data", self.test_calibration_data()))
        
        # Guidelines generation
        guidelines = await self.test_guidelines_generation()
        tests.append(("Guidelines Generation", guidelines is not None))
        
        # Guidelines saving and versioning
        tests.append(("Guidelines Saving", self.test_guidelines_saving(guidelines)))
        
        # Guidelines history
        tests.append(("Guidelines History", self.test_guidelines_history()))
        
        # Guidelines activation
        tests.append(("Guidelines Activation", self.test_guidelines_activation()))
        
        # Active guidelines retrieval
        tests.append(("Active Guidelines Retrieval", self.test_active_guidelines_retrieval()))
        
        # System status
        tests.append(("System Status", self.test_guidelines_status()))
        
        # Test results summary
        print_section("TEST RESULTS SUMMARY")
        
        passed = 0
        failed = 0
        
        for test_name, result in tests:
            if result:
                print_success(f"{test_name}")
                passed += 1
            else:
                print_error(f"{test_name}")
                failed += 1
        
        print(f"\n📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print_success("🎉 ALL TESTS PASSED! AI Guidelines system is working correctly.")
            print_info("✨ Phase 4.3 - Guidelines Management is complete!")
        else:
            print_error("💥 Some tests failed. Please check the errors above.")
        
        return failed == 0

async def main():
    """Main test function."""
    test_suite = AIGuidelinesTestSuite()
    success = await test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    asyncio.run(main())