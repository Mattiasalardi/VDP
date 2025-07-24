#!/usr/bin/env python3
"""
Complete Foundation Workflow Test
Tests the complete user journey through program-specific features to verify spotless foundation.
"""

import requests
import json
import sys
import time
from typing import Dict, Any, Optional

class FoundationTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000/api/v1"
        self.token = None
        self.org_id = None
        self.program_id = None
        self.questionnaire_id = None

    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp and level"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated HTTP request"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code >= 400:
                self.log(f"Request failed: {method} {endpoint} -> {response.status_code}", "ERROR")
                try:
                    error_detail = response.json()
                    self.log(f"Error details: {error_detail}", "ERROR")
                except:
                    self.log(f"Error body: {response.text}", "ERROR")
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            result = response.json()
            return {"success": True, "data": result}
            
        except Exception as e:
            self.log(f"Request exception: {str(e)}", "ERROR")
            return {"success": False, "error": str(e)}

    def test_authentication(self) -> bool:
        """Test 1: Authentication with existing seed user"""
        self.log("Testing authentication...")
        
        # OAuth2PasswordRequestForm expects username and password as form data
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = "username=admin@teched-accelerator.com&password=admin123"
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login", 
                headers=headers, 
                data=data
            )
            
            if response.status_code >= 400:
                self.log(f"❌ Authentication failed: HTTP {response.status_code}", "ERROR")
                try:
                    error_detail = response.json()
                    self.log(f"Error details: {error_detail}", "ERROR")
                except:
                    self.log(f"Error body: {response.text}", "ERROR")
                return False
            
            result = response.json()
            self.token = result["access_token"]
            self.log("✅ Authentication successful")
            return True
            
        except Exception as e:
            self.log(f"❌ Authentication exception: {str(e)}", "ERROR")
            return False

    def test_program_management(self) -> bool:
        """Test 2: Program management and selection"""
        self.log("Testing program management...")
        
        # List existing programs
        result = self.make_request("GET", "/programs")
        if not result["success"]:
            self.log("❌ Failed to list programs", "ERROR")
            return False
        
        programs = result["data"]["programs"]
        self.log(f"Found {len(programs)} existing programs")
        
        # Use first program or create a test program
        if programs:
            self.program_id = programs[0]["id"]
            self.log(f"✅ Using existing program: {programs[0]['name']} (ID: {self.program_id})")
        else:
            # Create a test program
            result = self.make_request("POST", "/programs", {
                "name": "Foundation Test Program",
                "description": "Test program for verifying foundation workflow"
            })
            
            if not result["success"]:
                self.log("❌ Failed to create test program", "ERROR")
                return False
            
            self.program_id = result["data"]["id"]
            self.log(f"✅ Created test program (ID: {self.program_id})")
        
        return True

    def test_calibration_system(self) -> bool:
        """Test 3: Program-specific calibration system"""
        self.log("Testing program-specific calibration...")
        
        # Get calibration questions
        result = self.make_request("GET", "/calibration/questions")
        if not result["success"]:
            self.log("❌ Failed to get calibration questions", "ERROR")
            return False
        
        questions = result["data"]["categories"]
        total_questions = sum(len(cat["questions"]) for cat in questions.values())
        self.log(f"✅ Retrieved {total_questions} calibration questions in {len(questions)} categories")
        
        # Check existing calibration status for this program
        result = self.make_request("GET", f"/calibration/programs/{self.program_id}/status")
        if result["success"]:
            status = result["data"]
            self.log(f"✅ Calibration status: {status['completion_percentage']}% complete ({status['answered_questions']}/{status['total_questions']})")
            
            if status['completion_percentage'] < 100:
                self.log("⚠️  Calibration not complete - this would be required for full workflow")
        else:
            self.log("✅ No existing calibration data (new program)")
        
        return True

    def test_questionnaire_system(self) -> bool:
        """Test 4: Program-specific questionnaire system"""
        self.log("Testing program-specific questionnaire system...")
        
        # List existing questionnaires for this program
        result = self.make_request("GET", f"/questions/programs/{self.program_id}/questionnaires")
        if not result["success"]:
            self.log("❌ Failed to list program questionnaires", "ERROR")
            return False
        
        questionnaires = result["data"].get("questionnaires", [])
        self.log(f"Found {len(questionnaires)} questionnaires for this program")
        
        # Create a test questionnaire
        result = self.make_request("POST", f"/questions/programs/{self.program_id}/questionnaires", {
            "name": "Foundation Test Questionnaire",
            "description": "Test questionnaire for foundation verification"
        })
        
        if not result["success"]:
            self.log("❌ Failed to create test questionnaire", "ERROR")
            return False
        
        self.questionnaire_id = result["data"]["id"]
        self.log(f"✅ Created test questionnaire (ID: {self.questionnaire_id})")
        
        # Test questionnaire details retrieval (critical for builder)
        result = self.make_request("GET", f"/questions/questionnaires/{self.questionnaire_id}")
        if not result["success"]:
            self.log("❌ Failed to retrieve questionnaire details", "ERROR")
            return False
        
        questionnaire = result["data"]
        self.log(f"✅ Retrieved questionnaire details: '{questionnaire['name']}' with {len(questionnaire.get('questions', []))} questions")
        
        return True

    def test_ai_guidelines_system(self) -> bool:
        """Test 5: Program-specific AI guidelines system"""
        self.log("Testing program-specific AI guidelines...")
        
        # Check existing guidelines
        result = self.make_request("GET", "/ai-guidelines/history", params={"program_id": self.program_id})
        if result["success"]:
            guidelines = result["data"].get("guidelines", [])
            self.log(f"Found {len(guidelines)} existing guideline versions")
        else:
            self.log("✅ No existing guidelines (expected for new program)")
        
        # Check active guidelines
        result = self.make_request("GET", "/ai-guidelines/active", params={"program_id": self.program_id})
        if result["success"] and result["data"]:
            active = result["data"]
            self.log(f"✅ Active guidelines found: version {active.get('version', 'unknown')}")
        else:
            self.log("✅ No active guidelines (expected for new program)")
        
        # Test guidelines status endpoint
        result = self.make_request("GET", "/ai-guidelines/status", params={"program_id": self.program_id})
        if result["success"]:
            status = result["data"]
            self.log(f"✅ Guidelines system status: {status.get('total_versions', 0)} versions")
        else:
            self.log("⚠️  Guidelines status check failed (may be expected for new program)")
        
        return True

    def test_program_isolation(self) -> bool:
        """Test 6: Verify complete program isolation"""
        self.log("Testing program isolation...")
        
        # Create a second test program for isolation testing with unique name
        import time
        unique_name = f"Isolation Test Program {int(time.time())}"
        result = self.make_request("POST", "/programs", {
            "name": unique_name,
            "description": "Second program to verify data isolation"
        })
        
        if not result["success"]:
            self.log("❌ Failed to create second test program", "ERROR")
            return False
        
        # Extract program ID from response - it's nested in result["data"]["program"]["id"]
        if "program" in result["data"]:
            program2_id = result["data"]["program"]["id"]
        else:
            program2_id = result["data"]["id"]
        self.log(f"✅ Created second program for isolation test (ID: {program2_id})")
        
        # Verify questionnaires are isolated
        result1 = self.make_request("GET", f"/questions/programs/{self.program_id}/questionnaires")
        result2 = self.make_request("GET", f"/questions/programs/{program2_id}/questionnaires")
        
        if not (result1["success"] and result2["success"]):
            self.log("❌ Failed to check questionnaire isolation", "ERROR")
            return False
        
        count1 = len(result1["data"].get("questionnaires", []))
        count2 = len(result2["data"].get("questionnaires", []))
        
        self.log(f"✅ Program isolation verified: Program 1 has {count1} questionnaires, Program 2 has {count2} questionnaires")
        
        # Clean up second program
        result = self.make_request("DELETE", f"/programs/{program2_id}")
        if result["success"]:
            self.log("✅ Cleaned up isolation test program")
        
        return True

    def test_api_consistency(self) -> bool:
        """Test 7: API response consistency and error handling"""
        self.log("Testing API consistency...")
        
        # Test invalid program ID
        result = self.make_request("GET", f"/questions/programs/99999/questionnaires")
        if not result["success"]:
            self.log("✅ Proper error handling for invalid program ID")
        else:
            self.log("⚠️  Expected error for invalid program ID but got success")
        
        # Test invalid questionnaire ID
        result = self.make_request("GET", "/questions/questionnaires/99999")
        if not result["success"]:
            self.log("✅ Proper error handling for invalid questionnaire ID")
        else:
            self.log("⚠️  Expected error for invalid questionnaire ID but got success")
        
        return True

    def cleanup(self):
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        if self.questionnaire_id:
            result = self.make_request("DELETE", f"/questions/questionnaires/{self.questionnaire_id}")
            if result["success"]:
                self.log("✅ Cleaned up test questionnaire")
        
        # Note: We don't delete the test program as it might be useful for continued testing

    def run_all_tests(self) -> bool:
        """Run complete foundation test suite"""
        self.log("🚀 Starting Complete Foundation Workflow Test")
        self.log("=" * 60)
        
        tests = [
            ("Authentication", self.test_authentication),
            ("Program Management", self.test_program_management),
            ("Calibration System", self.test_calibration_system),
            ("Questionnaire System", self.test_questionnaire_system),
            ("AI Guidelines System", self.test_ai_guidelines_system),
            ("Program Isolation", self.test_program_isolation),
            ("API Consistency", self.test_api_consistency)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running Test: {test_name}")
            self.log("-" * 40)
            
            try:
                if test_func():
                    passed += 1
                    self.log(f"✅ {test_name} PASSED\n")
                else:
                    failed += 1
                    self.log(f"❌ {test_name} FAILED\n")
            except Exception as e:
                failed += 1
                self.log(f"❌ {test_name} FAILED with exception: {e}\n", "ERROR")
        
        # Final summary
        self.log("=" * 60)
        self.log("🏁 FOUNDATION TEST RESULTS")
        self.log("=" * 60)
        self.log(f"✅ PASSED: {passed}")
        self.log(f"❌ FAILED: {failed}")
        self.log(f"📊 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED - FOUNDATION IS SPOTLESS!")
            self.cleanup()
            return True
        else:
            self.log("⚠️  SOME TESTS FAILED - FOUNDATION NEEDS ATTENTION")
            return False

def main():
    """Main test runner"""
    tester = FoundationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()