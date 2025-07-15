"""
Seed data for testing and development
"""
from sqlalchemy.orm import Session
from app.models import *
from app.core.database import SessionLocal
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_seed_data():
    """Create initial seed data for development and testing"""
    db = SessionLocal()
    
    try:
        # Create a sample organization
        org = Organization(
            name="TechEd Accelerator",
            email="admin@teched-accelerator.com",
            password_hash=pwd_context.hash("admin123"),
            description="Leading technology accelerator focused on early-stage startups",
            website="https://teched-accelerator.com",
            is_active=True
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create a sample program
        program = Program(
            name="TechEd Accelerator 2024",
            description="Our flagship program for 2024 focusing on AI and fintech startups",
            is_active=True,
            organization_id=org.id
        )
        db.add(program)
        db.commit()
        db.refresh(program)
        
        # Create a sample questionnaire
        questionnaire = Questionnaire(
            name="Startup Application Form",
            description="Standard application form for startup evaluation",
            is_active=True,
            program_id=program.id
        )
        db.add(questionnaire)
        db.commit()
        db.refresh(questionnaire)
        
        # Create sample questions
        questions = [
            Question(
                text="What problem does your startup solve?",
                question_type="text",
                is_required=True,
                order_index=1,
                validation_rules={"min_length": 50, "max_length": 500},
                questionnaire_id=questionnaire.id
            ),
            Question(
                text="What is your startup's stage?",
                question_type="multiple_choice",
                is_required=True,
                order_index=2,
                options={"choices": ["Idea", "MVP", "Early Revenue", "Growth", "Scale"]},
                questionnaire_id=questionnaire.id
            ),
            Question(
                text="How would you rate your team's technical expertise?",
                question_type="scale",
                is_required=True,
                order_index=3,
                options={"min": 1, "max": 10, "step": 1},
                questionnaire_id=questionnaire.id
            ),
            Question(
                text="Upload your pitch deck (PDF only)",
                question_type="file_upload",
                is_required=True,
                order_index=4,
                validation_rules={"allowed_types": ["pdf"], "max_size": 10485760},  # 10MB
                questionnaire_id=questionnaire.id
            ),
            Question(
                text="Describe your target market",
                question_type="text",
                is_required=True,
                order_index=5,
                validation_rules={"min_length": 100, "max_length": 1000},
                questionnaire_id=questionnaire.id
            )
        ]
        
        for question in questions:
            db.add(question)
        db.commit()
        
        # Create sample calibration answers
        calibration_answers = [
            CalibrationAnswer(
                question_key="team_importance",
                answer_value={"weight": 9, "reasoning": "Team is crucial for execution"},
                answer_text="Team experience and composition is extremely important (9/10)",
                program_id=program.id
            ),
            CalibrationAnswer(
                question_key="market_size_preference",
                answer_value={"min_size": 1000000000, "preference": "large_addressable_market"},
                answer_text="Prefer startups targeting markets with at least $1B potential",
                program_id=program.id
            ),
            CalibrationAnswer(
                question_key="stage_preference",
                answer_value={"preferred_stages": ["MVP", "Early Revenue"], "avoid": ["Idea"]},
                answer_text="Focus on startups with MVP or early revenue, avoid idea-stage",
                program_id=program.id
            ),
            CalibrationAnswer(
                question_key="sector_focus",
                answer_value={"sectors": ["AI/ML", "Fintech", "Healthcare", "SaaS"]},
                answer_text="Primary focus on AI/ML, Fintech, Healthcare, and SaaS startups",
                program_id=program.id
            )
        ]
        
        for answer in calibration_answers:
            db.add(answer)
        db.commit()
        
        # Create sample AI guidelines
        ai_guidelines = [
            AIGuideline(
                section="team_structure",
                weight=9,
                criteria={
                    "key_factors": ["experience", "complementary_skills", "commitment"],
                    "red_flags": ["single_founder", "no_technical_founder", "part_time_commitment"],
                    "scoring_guide": {
                        "8-10": "Experienced team with complementary skills",
                        "6-7": "Good team with some gaps",
                        "4-5": "Average team with significant gaps",
                        "1-3": "Weak team or major red flags"
                    }
                },
                prompt_template="Evaluate the team structure based on experience, skills complementarity, and commitment level...",
                is_active=True,
                version=1,
                program_id=program.id
            ),
            AIGuideline(
                section="market_opportunity",
                weight=8,
                criteria={
                    "key_factors": ["market_size", "growth_potential", "competition"],
                    "red_flags": ["declining_market", "oversaturated", "no_clear_market"],
                    "scoring_guide": {
                        "8-10": "Large, growing market with clear opportunity",
                        "6-7": "Good market with some competition",
                        "4-5": "Moderate market opportunity",
                        "1-3": "Small or declining market"
                    }
                },
                prompt_template="Assess the market opportunity considering size, growth, and competitive landscape...",
                is_active=True,
                version=1,
                program_id=program.id
            ),
            AIGuideline(
                section="problem_solution",
                weight=8,
                criteria={
                    "key_factors": ["problem_clarity", "solution_fit", "validation"],
                    "red_flags": ["unclear_problem", "solution_mismatch", "no_validation"],
                    "scoring_guide": {
                        "8-10": "Clear problem with validated solution",
                        "6-7": "Good problem-solution fit",
                        "4-5": "Moderate alignment",
                        "1-3": "Poor problem-solution fit"
                    }
                },
                prompt_template="Evaluate how well the solution addresses the identified problem...",
                is_active=True,
                version=1,
                program_id=program.id
            )
        ]
        
        for guideline in ai_guidelines:
            db.add(guideline)
        db.commit()
        
        # Create a sample application
        application = Application(
            unique_id=str(uuid.uuid4()),
            startup_name="AI-Powered Analytics Co",
            contact_email="founder@aianalytics.com",
            is_submitted=False,
            is_processed=False,
            processing_status="pending",
            program_id=program.id,
            questionnaire_id=questionnaire.id
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        
        print("✅ Seed data created successfully!")
        print(f"Organization: {org.name}")
        print(f"Program: {program.name}")
        print(f"Questionnaire: {questionnaire.name}")
        print(f"Questions: {len(questions)} created")
        print(f"Calibration answers: {len(calibration_answers)} created")
        print(f"AI guidelines: {len(ai_guidelines)} created")
        print(f"Sample application: {application.unique_id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating seed data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()