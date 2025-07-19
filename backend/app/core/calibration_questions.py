# Calibration Questions for Accelerator Preferences
# These questions help the AI understand what each accelerator values most in startup applications

CALIBRATION_QUESTIONS = [
    {
        "key": "team_importance",
        "question": "How important is the founding team's experience and background?",
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Not important - Great ideas matter more than experience",
            5: "Moderately important - Good balance of idea and team",
            10: "Extremely important - Team experience is the top factor"
        },
        "description": "This helps us understand how much weight to give to team credentials, previous startup experience, domain expertise, and educational background."
    },
    {
        "key": "market_size_preference", 
        "question": "What type of market opportunity do you prefer?",
        "type": "multiple_choice",
        "options": [
            {"value": "large_existing", "label": "Large existing markets with proven demand"},
            {"value": "emerging_high_growth", "label": "Emerging markets with high growth potential"},
            {"value": "niche_specialized", "label": "Niche markets with specialized needs"},
            {"value": "disruptive_new", "label": "Completely new markets being created"}
        ],
        "description": "This influences how we evaluate market opportunity and size in applications."
    },
    {
        "key": "revenue_stage_preference",
        "question": "What revenue stage do you prefer startups to be in?",
        "type": "multiple_choice", 
        "options": [
            {"value": "pre_revenue", "label": "Pre-revenue with strong validation"},
            {"value": "early_revenue", "label": "Early revenue ($1K-$50K monthly)"},
            {"value": "growing_revenue", "label": "Growing revenue ($50K+ monthly)"},
            {"value": "any_stage", "label": "Any stage with strong potential"}
        ],
        "description": "This helps us properly evaluate financial metrics and revenue projections."
    },
    {
        "key": "technology_innovation",
        "question": "How important is technological innovation and IP?",
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Not important - Business model innovation matters more",
            5: "Moderately important - Some tech advantage helpful",
            10: "Extremely important - Deep tech and patents essential"
        },
        "description": "This affects how we score technology sections and intellectual property."
    },
    {
        "key": "scalability_focus",
        "question": "What type of scalability do you value most?",
        "type": "multiple_choice",
        "options": [
            {"value": "rapid_user_growth", "label": "Rapid user/customer acquisition"},
            {"value": "revenue_scalability", "label": "Revenue scalability and unit economics"},
            {"value": "geographic_expansion", "label": "Geographic expansion potential"},
            {"value": "operational_efficiency", "label": "Operational efficiency and automation"}
        ],
        "description": "This influences how we evaluate business model scalability."
    },
    {
        "key": "funding_stage_comfort",
        "question": "What funding stage are you most comfortable with?",
        "type": "multiple_choice",
        "options": [
            {"value": "bootstrap_pre_seed", "label": "Bootstrapped or pre-seed"},
            {"value": "seed_stage", "label": "Seed stage ($100K-$2M raised)"},
            {"value": "series_a_ready", "label": "Series A ready ($2M+ raised)"},
            {"value": "any_stage", "label": "Any stage depending on potential"}
        ],
        "description": "This helps us evaluate funding history and future needs appropriately."
    },
    {
        "key": "industry_vertical_preference",
        "question": "Do you have industry vertical preferences?",
        "type": "text",
        "placeholder": "e.g., 'We prefer B2B SaaS, FinTech, and HealthTech but are open to exceptional opportunities in other sectors'",
        "description": "This helps us understand your sector focus and adjust evaluation criteria accordingly."
    },
    {
        "key": "competition_analysis_weight",
        "question": "How important is detailed competitive analysis?", 
        "type": "scale",
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Not critical - Unique value prop matters more",
            5: "Important - Should understand competitive landscape", 
            10: "Essential - Detailed competitive strategy required"
        },
        "description": "This affects how we score competitive analysis and differentiation sections."
    },
    {
        "key": "social_impact_importance",
        "question": "How important is social impact or ESG considerations?",
        "type": "scale", 
        "scale_min": 1,
        "scale_max": 10,
        "scale_labels": {
            1: "Not a factor - Pure commercial focus",
            5: "Nice to have - Positive impact is a plus",
            10: "Essential - Social impact is a key criteria"
        },
        "description": "This influences how we weight social impact and sustainability factors."
    },
    {
        "key": "customer_validation_requirements",
        "question": "What level of customer validation do you require?",
        "type": "multiple_choice",
        "options": [
            {"value": "strong_hypothesis", "label": "Strong hypothesis with market research"},
            {"value": "customer_interviews", "label": "Customer interviews and feedback"},
            {"value": "pilot_customers", "label": "Pilot customers or LOIs"},
            {"value": "paying_customers", "label": "Paying customers and retention data"}
        ],
        "description": "This helps us properly evaluate validation and traction sections."
    },
    {
        "key": "risk_tolerance",
        "question": "What's your risk tolerance for early-stage investments?",
        "type": "scale",
        "scale_min": 1, 
        "scale_max": 10,
        "scale_labels": {
            1: "Conservative - Prefer proven models",
            5: "Balanced - Calculated risks acceptable",
            10: "High risk - Breakthrough potential worth big risks"
        },
        "description": "This affects our overall scoring approach and how we weigh different risk factors."
    },
    {
        "key": "geographic_preference",
        "question": "Do you have geographic preferences for startups?",
        "type": "text",
        "placeholder": "e.g., 'Prefer US and Canada, but open to exceptional international opportunities'",
        "description": "This helps us understand location-based evaluation criteria."
    }
]

# Categories for organizing the calibration process
CALIBRATION_CATEGORIES = {
    "team_and_founders": {
        "title": "Team & Founders",
        "description": "Your preferences for evaluating founding teams",
        "questions": ["team_importance"]
    },
    "market_and_opportunity": {
        "title": "Market & Opportunity", 
        "description": "Your approach to market evaluation",
        "questions": ["market_size_preference", "industry_vertical_preference", "geographic_preference"]
    },
    "business_model": {
        "title": "Business Model & Traction",
        "description": "Your criteria for business models and validation",
        "questions": ["revenue_stage_preference", "scalability_focus", "customer_validation_requirements"]
    },
    "technology_and_innovation": {
        "title": "Technology & Innovation",
        "description": "Your approach to technology evaluation", 
        "questions": ["technology_innovation", "competition_analysis_weight"]
    },
    "investment_criteria": {
        "title": "Investment Criteria",
        "description": "Your investment approach and risk tolerance",
        "questions": ["funding_stage_comfort", "risk_tolerance", "social_impact_importance"]
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