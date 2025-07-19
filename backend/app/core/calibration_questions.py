# Calibration Questions for Accelerator Preferences
# These questions help the AI understand what each accelerator values most in startup applications
# Questions align with final report structure: Problem-Solution Fit, Customer Profile & Business Model, 
# Product & Technology, Team Assessment, Market Opportunity, Competition & Differentiation, 
# Financial Overview, Validation & Achievements

CALIBRATION_QUESTIONS = [
    {
        "key": "startup_stage_preference",
        "question": "What stage of startups do you prefer to work with?",
        "type": "multiple_choice",
        "options": [
            {"value": "pre_seed", "label": "Pre-seed (Idea stage, pre-revenue)"},
            {"value": "seed", "label": "Seed stage (Early revenue, $100K-$2M raised)"},
            {"value": "series_a", "label": "Series A ready ($2M+ raised, proven traction)"},
            {"value": "stage_agnostic", "label": "Stage agnostic - depends on potential"}
        ],
        "description": "This affects how we evaluate financial metrics, team requirements, and validation expectations."
    },
    {
        "key": "technical_vs_business_innovation",
        "question": "How important is technical innovation vs business model innovation?",
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Business model innovation is key - tech can be simple",
            5: "Equal importance of both technical and business innovation",
            10: "Deep tech innovation is essential - breakthrough technology required"
        },
        "description": "This influences how we score Product & Technology vs Customer Profile & Business Model sections."
    },
    {
        "key": "team_assessment_priority",
        "question": "What's most important in team assessment?",
        "type": "multiple_choice",
        "options": [
            {"value": "solo_founders_ok", "label": "Solo founders with strong vision are acceptable"},
            {"value": "team_preferred", "label": "Team preferred but solo founders considered"},
            {"value": "team_required", "label": "Strong team of 2+ co-founders required"},
            {"value": "domain_expertise", "label": "Domain expertise matters more than team size"}
        ],
        "description": "This guides the Team Assessment section scoring and requirements."
    },
    {
        "key": "risk_tolerance_moonshots",
        "question": "What's your risk tolerance for moonshot ideas?",
        "type": "multiple_choice",
        "options": [
            {"value": "conservative", "label": "Conservative - Prefer proven business models and markets"},
            {"value": "balanced", "label": "Balanced - Mix of proven concepts with some innovation"},
            {"value": "aggressive", "label": "Aggressive - Embrace breakthrough ideas and disruption"}
        ],
        "description": "This affects how we score Problem-Solution Fit and overall risk assessment."
    },
    {
        "key": "industry_focus_preference",
        "question": "What's your industry focus preference?",
        "type": "multiple_choice",
        "options": [
            {"value": "b2b_saas", "label": "B2B SaaS and Enterprise Solutions"},
            {"value": "b2c_consumer", "label": "B2C Consumer and Marketplace"},
            {"value": "deep_tech", "label": "Deep Tech and Hardware Innovation"},
            {"value": "social_impact", "label": "Social Impact and Sustainability"},
            {"value": "fintech_health", "label": "FinTech and HealthTech"},
            {"value": "industry_agnostic", "label": "Industry agnostic - focus on quality"}
        ],
        "description": "This influences Market Opportunity evaluation and sector-specific criteria."
    },
    {
        "key": "revenue_requirements",
        "question": "What are your revenue requirements?",
        "type": "multiple_choice",
        "options": [
            {"value": "pre_revenue_ok", "label": "Pre-revenue is acceptable with strong validation"},
            {"value": "revenue_preferred", "label": "Revenue preferred but not required"},
            {"value": "revenue_required", "label": "Consistent revenue stream required"},
            {"value": "growth_focused", "label": "Focus on revenue growth trajectory over absolute numbers"}
        ],
        "description": "This guides Financial Overview section evaluation and expectations."
    },
    {
        "key": "market_opportunity_size",
        "question": "What market size do you typically target?",
        "type": "multiple_choice",
        "options": [
            {"value": "large_markets", "label": "Large markets ($1B+ TAM) with proven demand"},
            {"value": "emerging_markets", "label": "Emerging markets with high growth potential"},
            {"value": "niche_markets", "label": "Niche markets with strong customer need"},
            {"value": "market_creating", "label": "Market-creating opportunities"}
        ],
        "description": "This affects Market Opportunity scoring and size requirements."
    },
    {
        "key": "competition_differentiation_importance",
        "question": "How important is competitive differentiation?",
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Not critical - Focus on execution over differentiation",
            5: "Important - Need clear competitive advantage",
            10: "Essential - Must have strong moats and unique positioning"
        },
        "description": "This affects Competition & Differentiation section weighting and requirements."
    },
    {
        "key": "validation_achievement_standards",
        "question": "What level of validation and achievements do you expect?",
        "type": "multiple_choice",
        "options": [
            {"value": "hypothesis_validation", "label": "Strong hypothesis with market research"},
            {"value": "customer_validation", "label": "Customer interviews and feedback loops"},
            {"value": "pilot_traction", "label": "Pilot customers and early traction"},
            {"value": "proven_traction", "label": "Proven traction with paying customers"}
        ],
        "description": "This guides Validation & Achievements section evaluation standards."
    },
    {
        "key": "problem_solution_fit_priority",
        "question": "How do you prioritize problem-solution fit evaluation?",
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Focus on solution quality - problem can be validated later",
            5: "Equal weight on problem validation and solution strength",
            10: "Problem validation is critical - solution can be iterated"
        },
        "description": "This influences Problem-Solution Fit section weighting and evaluation approach."
    },
    {
        "key": "customer_business_model_focus",
        "question": "What's most important in customer profile and business model?",
        "type": "multiple_choice",
        "options": [
            {"value": "customer_discovery", "label": "Deep customer discovery and understanding"},
            {"value": "business_model", "label": "Proven and scalable business model"},
            {"value": "market_fit", "label": "Product-market fit evidence"},
            {"value": "unit_economics", "label": "Clear unit economics and profitability path"}
        ],
        "description": "This affects Customer Profile & Business Model section emphasis."
    }
]

# Categories for organizing the calibration process - aligned with final report structure
CALIBRATION_CATEGORIES = {
    "general_preferences": {
        "title": "General Investment Preferences",
        "description": "Your overall investment approach and risk tolerance",
        "questions": ["startup_stage_preference", "risk_tolerance_moonshots", "industry_focus_preference"]
    },
    "problem_solution_evaluation": {
        "title": "Problem-Solution Fit Evaluation", 
        "description": "Your approach to evaluating problem-solution alignment",
        "questions": ["problem_solution_fit_priority", "technical_vs_business_innovation"]
    },
    "team_assessment": {
        "title": "Team Assessment Criteria",
        "description": "Your standards for evaluating founding teams",
        "questions": ["team_assessment_priority"]
    },
    "market_and_business": {
        "title": "Market & Business Model",
        "description": "Your criteria for market opportunity and business models",
        "questions": ["market_opportunity_size", "customer_business_model_focus", "revenue_requirements"]
    },
    "competition_and_validation": {
        "title": "Competition & Validation Standards",
        "description": "Your expectations for competitive positioning and validation",
        "questions": ["competition_differentiation_importance", "validation_achievement_standards"]
    }
}

def get_question_by_key(question_key: str):
    """Get a specific calibration question by its key"""
    for question in CALIBRATION_QUESTIONS:
        if question["key"] == question_key:
            return question
    return None

def get_questions_by_category(category_key: str):
    """Get all questions for a specific category"""
    if category_key not in CALIBRATION_CATEGORIES:
        return []
    
    category = CALIBRATION_CATEGORIES[category_key]
    questions = []
    
    for question_key in category["questions"]:
        question = get_question_by_key(question_key)
        if question:
            questions.append(question)
    
    return questions

def get_all_questions_organized():
    """Get all questions organized by category"""
    organized = {}
    
    for category_key, category_info in CALIBRATION_CATEGORIES.items():
        organized[category_key] = {
            "info": category_info,
            "questions": get_questions_by_category(category_key)
        }
    
    return organized