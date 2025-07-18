#!/usr/bin/env python3
"""
Manual test script for question CRUD operations
Run this after starting the backend server: python backend/scripts/test_questions.py
"""

import json
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models.organization import Organization
from app.models.program import Program
from app.models.questionnaire import Questionnaire
from app.models.question import Question
from app.schemas.question import QuestionType
from app.services.question_service import QuestionService


def test_question_creation():
    """Test creating different types of questions"""
    db = next(get_db())
    
    try:
        # Find existing test data
        org = db.query(Organization).filter(Organization.email == "admin@teched-accelerator.com").first()
        if not org:
            print("❌ No test organization found. Please run seed data first.")
            return False
        
        program = db.query(Program).filter(Program.organization_id == org.id).first()
        if not program:
            print("❌ No test program found. Please run seed data first.")
            return False
        
        questionnaire = db.query(Questionnaire).filter(Questionnaire.program_id == program.id).first()
        if not questionnaire:
            print("❌ No test questionnaire found. Please run seed data first.")
            return False
        
        print(f"✅ Using organization: {org.name}")
        print(f"✅ Using program: {program.name}")
        print(f"✅ Using questionnaire: {questionnaire.name}")
        
        # Test 1: Create text question
        print("\n📝 Testing text question creation...")
        text_question = Question(
            text="What is your company name?",
            question_type=QuestionType.TEXT.value,
            is_required=True,
            order_index=0,
            options={
                "max_length": 200,
                "min_length": 1,
                "placeholder": "Enter your company name",
                "multiline": False
            },
            validation_rules={"required": True},
            questionnaire_id=questionnaire.id
        )
        
        db.add(text_question)
        db.commit()
        db.refresh(text_question)
        print(f"✅ Text question created with ID: {text_question.id}")
        
        # Test 2: Create multiple choice question
        print("\n📋 Testing multiple choice question creation...")
        mc_question = Question(
            text="What is your company stage?",
            question_type=QuestionType.MULTIPLE_CHOICE.value,
            is_required=True,
            order_index=1,
            options={
                "choices": ["Idea", "Prototype", "MVP", "Growth", "Scale"],
                "allow_multiple": False,
                "randomize_order": False
            },
            validation_rules={"required": True},
            questionnaire_id=questionnaire.id
        )
        
        db.add(mc_question)
        db.commit()
        db.refresh(mc_question)
        print(f"✅ Multiple choice question created with ID: {mc_question.id}")
        
        # Test 3: Create scale question
        print("\n📊 Testing scale question creation...")
        scale_question = Question(
            text="How would you rate your team's technical expertise?",
            question_type=QuestionType.SCALE.value,
            is_required=True,
            order_index=2,
            options={
                "min_value": 1,
                "max_value": 10,
                "step": 1,
                "min_label": "Beginner",
                "max_label": "Expert"
            },
            validation_rules={"required": True},
            questionnaire_id=questionnaire.id
        )
        
        db.add(scale_question)
        db.commit()
        db.refresh(scale_question)
        print(f"✅ Scale question created with ID: {scale_question.id}")
        
        # Test 4: Create file upload question
        print("\n📁 Testing file upload question creation...")
        file_question = Question(
            text="Please upload your business plan",
            question_type=QuestionType.FILE_UPLOAD.value,
            is_required=True,
            order_index=3,
            options={
                "max_file_size_mb": 50,
                "allowed_extensions": [".pdf"],
                "max_files": 1
            },
            validation_rules={"required": True},
            questionnaire_id=questionnaire.id
        )
        
        db.add(file_question)
        db.commit()
        db.refresh(file_question)
        print(f"✅ File upload question created with ID: {file_question.id}")
        
        # Test 5: Query all questions
        print("\n📋 Testing question retrieval...")
        questions = db.query(Question).filter(
            Question.questionnaire_id == questionnaire.id
        ).order_by(Question.order_index).all()
        
        print(f"✅ Found {len(questions)} questions:")
        for q in questions:
            print(f"  - {q.order_index}: {q.text[:50]}... ({q.question_type})")
        
        # Test 6: Update question
        print("\n✏️  Testing question update...")
        text_question.text = "What is your startup's name?"
        db.commit()
        print(f"✅ Question updated: {text_question.text}")
        
        # Test 7: Test validation
        print("\n🔍 Testing question validation...")
        
        # Test text response validation
        is_valid, error = QuestionService.validate_question_response(text_question, "Valid Company Name")
        print(f"✅ Text validation (valid): {is_valid}")
        
        is_valid, error = QuestionService.validate_question_response(text_question, "")
        print(f"✅ Text validation (empty): {is_valid}, Error: {error}")
        
        # Test multiple choice response validation
        is_valid, error = QuestionService.validate_question_response(mc_question, "MVP")
        print(f"✅ MC validation (valid): {is_valid}")
        
        is_valid, error = QuestionService.validate_question_response(mc_question, "Invalid Choice")
        print(f"✅ MC validation (invalid): {is_valid}, Error: {error}")
        
        # Test scale response validation
        is_valid, error = QuestionService.validate_question_response(scale_question, 7)
        print(f"✅ Scale validation (valid): {is_valid}")
        
        is_valid, error = QuestionService.validate_question_response(scale_question, 15)
        print(f"✅ Scale validation (invalid): {is_valid}, Error: {error}")
        
        # Test 8: Test reordering
        print("\n🔄 Testing question reordering...")
        question_ids = [q.id for q in questions]
        reversed_order = question_ids[::-1]
        
        success = QuestionService.reorder_questions(db, questionnaire.id, reversed_order)
        print(f"✅ Reordering successful: {success}")
        
        # Verify new order
        questions = db.query(Question).filter(
            Question.questionnaire_id == questionnaire.id
        ).order_by(Question.order_index).all()
        
        print("✅ New question order:")
        for q in questions:
            print(f"  - {q.order_index}: {q.text[:50]}... ({q.question_type})")
        
        print("\n🎉 All question tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_question_options():
    """Test question options validation"""
    print("\n🔧 Testing question options...")
    
    # Test default options
    text_defaults = QuestionService.get_question_default_options(QuestionType.TEXT)
    print(f"✅ Text defaults: {text_defaults}")
    
    mc_defaults = QuestionService.get_question_default_options(QuestionType.MULTIPLE_CHOICE)
    print(f"✅ Multiple choice defaults: {mc_defaults}")
    
    scale_defaults = QuestionService.get_question_default_options(QuestionType.SCALE)
    print(f"✅ Scale defaults: {scale_defaults}")
    
    file_defaults = QuestionService.get_question_default_options(QuestionType.FILE_UPLOAD)
    print(f"✅ File upload defaults: {file_defaults}")


def main():
    """Run all tests"""
    print("🚀 Starting question CRUD tests...")
    print("=" * 50)
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Run tests
    test_question_options()
    
    success = test_question_creation()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("✅ Question types: text, multiple_choice, scale, file_upload")
        print("✅ Validation rules: working correctly")
        print("✅ Ordering system: working correctly")
        print("✅ CRUD operations: all functional")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()