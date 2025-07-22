from fastapi import APIRouter

from app.api.v1.endpoints import auth, organizations, questions, calibration, ai_guidelines, programs, public_forms

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(calibration.router, prefix="/calibration", tags=["calibration"])
api_router.include_router(ai_guidelines.router, prefix="/ai-guidelines", tags=["ai-guidelines"])
api_router.include_router(public_forms.router, prefix="/public", tags=["public-forms"])