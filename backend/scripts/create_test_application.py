#!/usr/bin/env python3

import sys
import os
import uuid

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.application import Application
from app.models.program import Program
from app.models.questionnaire import Questionnaire
from app.models.question import Question
from app.models.organization import Organization

def create_test_application():
    """Create a test application with a questionnaire for testing the public form"""
    
    db = SessionLocal()
    
    try:
        print("=== Creating Test Application Data ===")
        
        # Find the test organization (should exist from seed data)
        org = db.query(Organization).filter(Organization.email == "admin@teched-accelerator.com").first()
        if not org:
            print("❌ Test organization not found. Run 'python scripts/manage_db.py seed-data' first")
            return None
        
        print(f"✅ Found organization: {org.name}")
        
        # Find or create a test program
        program = db.query(Program).filter(Program.organization_id == org.id).first()
        if not program:
            program = Program(
                name="Test Accelerator Program 2024",
                description="Test program for public form testing",
                organization_id=org.id,
                is_active=True
            )
            db.add(program)
            db.commit()
            db.refresh(program)
        
        print(f"✅ Using program: {program.name} (ID: {program.id})")
        
        # Find or create a test questionnaire with questions
        questionnaire = db.query(Questionnaire).filter(
            Questionnaire.program_id == program.id
        ).first()
        
        if not questionnaire:
            # Create a questionnaire
            questionnaire = Questionnaire(
                name="Startup Application Form",
                description="Tell us about your startup and why you'd be a great fit for our accelerator program.",
                program_id=program.id,
                is_active=True
            )
            db.add(questionnaire)
            db.commit()
            db.refresh(questionnaire)
            
            # Create some sample questions
            questions_data = [
                {
                    "text": "What is your startup's name and what problem does it solve?",
                    "question_type": "text",
                    "options": {"multiline": True, "max_length": 500, "placeholder": "Describe your startup and the problem you're solving..."},
                    "is_required": True,
                    "order_index": 0
                },
                {
                    "text": "Which stage best describes your startup?",
                    "question_type": "multiple_choice",
                    "options": {
                        "choices": ["Idea stage", "MVP completed", "Early customers", "Scaling", "Series A+"],
                        "multiple_selection": False
                    },
                    "is_required": True,
                    "order_index": 1
                },
                {
                    "text": "How would you rate your team's technical expertise?",
                    "question_type": "scale",
                    "options": {
                        "min_value": 1,
                        "max_value": 10,
                        "step": 1,
                        "min_label": "Beginner",
                        "max_label": "Expert"
                    },
                    "is_required": True,
                    "order_index": 2
                },
                {
                    "text": "Upload your pitch deck (PDF only)",
                    "question_type": "file_upload",
                    "options": {
                        "multiple_files": False,
                        "max_size_mb": 10,
                        "allowed_extensions": [".pdf"]
                    },
                    "is_required": False,
                    "order_index": 3
                }
            ]
            
            for q_data in questions_data:
                question = Question(
                    text=q_data["text"],
                    question_type=q_data["question_type"],
                    options=q_data["options"],
                    is_required=q_data["is_required"],
                    order_index=q_data["order_index"],
                    questionnaire_id=questionnaire.id
                )
                db.add(question)
            
            db.commit()
            print(f"✅ Created questionnaire with {len(questions_data)} questions")
        else:
            print(f"✅ Using existing questionnaire: {questionnaire.name}")
        
        # Create a test application
        unique_id = str(uuid.uuid4())
        
        application = Application(
            unique_id=unique_id,
            startup_name="TechStartup Inc",
            contact_email="founder@techstartup.com",
            is_submitted=False,
            is_processed=False,
            processing_status="pending",
            program_id=program.id,
            questionnaire_id=questionnaire.id
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        print(f"✅ Created test application: {application.unique_id}")
        
        # Generate the public form URL
        public_url = f"http://localhost:3000/apply/{program.id}/{application.unique_id}"
        
        print("\n" + "="*60)
        print("🎉 TEST APPLICATION CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"Program ID: {program.id}")
        print(f"Application ID: {application.unique_id}")
        print(f"Startup Name: {application.startup_name}")
        print(f"Contact Email: {application.contact_email}")
        print("")
        print("🌐 PUBLIC FORM URL:")
        print(f"{public_url}")
        print("")
        print("✅ You can now test the public application form!")
        print("📝 The form has 4 sample questions covering all question types")
        print("="*60)
        
        return {
            "program_id": program.id,
            "application_id": application.unique_id,
            "public_url": public_url
        }
        
    except Exception as e:
        print(f"❌ Error creating test application: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_application()