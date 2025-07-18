# Claude Memory - VDP Application Build

## Project Summary
Building an AI-powered application management platform for startup accelerators. The platform automates evaluation of startup applications through customizable questionnaires and AI-generated assessment reports.

## Key Context
- **Full Details**: All comprehensive project information is stored in `PROJECT_CONTEXT.md`
- **Development Plan**: Detailed 9-phase roadmap in `DEVELOPMENT_ROADMAP.md`
- **Debug Solutions**: Common issues and fixes tracked in `DEBUG.md`
- **Tech Stack**: FastAPI (Python) backend, Next.js frontend, PostgreSQL database, Claude AI integration
- **MVP Focus**: Questionnaire builder, calibration system, public forms, AI processing, report generation, dashboard
- **Current Status**: Phase 1 Complete - FastAPI foundation with authentication ready

## Development Workflow
1. **Always check PROJECT_CONTEXT.md** before starting any implementation
2. **Follow DEVELOPMENT_ROADMAP.md** for structured task progression
3. **Use TodoWrite tool** to track all development tasks within each phase
4. **Auto-update DEBUG.md** when solving any non-trivial problems
5. **Run tests and linting** after code changes (when available)
6. **Follow existing code conventions** when they exist
7. **Never commit** unless explicitly asked by user

## Key Business Rules
- Single user login per accelerator (shared credentials)
- PDF uploads only with generous size limits
- 50 question limit per questionnaire
- Unlimited applications per program
- All data stored indefinitely
- Platform branding only (no custom branding for MVP)

## AI Integration Details
- **Primary AI**: Claude API for analysis and report generation
- **Process**: Calibration → AI guidelines → User review/modification → Application processing
- **Report Structure**: Fixed template with 10 sections, 1-10 scoring scale

## Database Schema Priority
Core tables: organizations, programs, questionnaires, questions, calibration_answers, ai_guidelines, applications, responses, uploaded_files, reports, scores

## Success Metrics 
- Report generation < 30 seconds
- Handle 100+ concurrent applications
- 90%+ reports need no manual adjustment

## Commands to Remember
**Database Management:**
- `python backend/scripts/manage_db.py create-tables` - Create all database tables
- `python backend/scripts/manage_db.py seed-data` - Create seed data for testing
- `python backend/scripts/manage_db.py reset-db` - Drop, create, and seed database
- `python3 -m alembic upgrade head` - Run database migrations

**Development:**
- `pip install -r backend/requirements.txt` - Install Python dependencies
- `cd backend && python3 -m uvicorn app.main:app --reload` - Start development server
- `python3 scripts/manage_db.py create-tables` - Create database tables (if needed)
- `python3 scripts/manage_db.py seed-data` - Create seed data with test credentials

## Current Development Status
**Phase**: 3 (Questionnaire Builder) - Task 3.2 Complete
**Next Task**: 4.1 - Calibration Questions (pre-defined calibration question set)
**Total Phases**: 9 phases, estimated 25-35 hours total
**Dependencies**: Phase 1 foundation complete ✅, Phase 2 complete ✅, Phase 3 complete ✅

## File Structure Created
- `PROJECT_CONTEXT.md` - Complete project requirements and architecture
- `DEVELOPMENT_ROADMAP.md` - 9-phase structured development plan
- `DEBUG.md` - Issue tracking and solutions (empty, ready for use)
- `CLAUDE.md` - This memory file

## Working Methodology
- **Phase-by-phase**: Work through DEVELOPMENT_ROADMAP.md systematically
- **Task-specific prompts**: User gives focused tasks like "Work on Phase 1, Task 1.1"
- **Progress tracking**: Update roadmap checkboxes and this memory file
- **Context preservation**: Always update this file with progress and learnings

## Important Notes
- Always reference PROJECT_CONTEXT.md for complete details
- User may start new Claude sessions - this file must contain full context
- Focus on MVP features first, avoid feature creep
- Performance is critical (30-second report generation target)
- Automatically document solutions in DEBUG.md when encountered

## Debugging Workflow
- Remember to automatically add debugging entries to the DEBUG.md files

## Phase 1 Complete - Foundation & Infrastructure
**Database Implementation Complete:**
- All 9 core tables implemented: organizations, programs, questionnaires, questions, calibration_answers, ai_guidelines, applications, responses, uploaded_files, reports, scores
- Complete SQLAlchemy models with relationships and proper indexing
- Alembic migration system with initial schema
- Comprehensive seed data for testing (credentials: admin@teched-accelerator.com / admin123)
- Database management scripts for easy setup

**FastAPI Foundation Complete:**
- Production-ready FastAPI application with CORS and middleware
- Comprehensive JWT authentication system with password hashing
- Authentication endpoints: `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me`
- Health check endpoint with database connectivity testing
- Global exception handling with proper error responses
- Structured logging for debugging and monitoring
- API versioning structure ready for expansion

**Testing & Validation:**
- All authentication functions tested and working
- Database connectivity verified
- JWT token creation and verification working
- Password hashing and verification working
- Health check endpoint operational
- Seed data with test organization credentials ready
- Frontend login form integration tested and working
- Protected dashboard routes functioning correctly

## Phase 2 Complete - Authentication & Organization Management
**Phase 2 Task 2.1 Complete - Frontend Authentication:**
- Responsive login page (`/login`) with form validation and error handling
- Protected dashboard page (`/dashboard`) with organization details and logout functionality
- Automatic route protection and redirect logic based on authentication state
- JWT token storage and management in localStorage with proper cleanup
- Seamless authentication flow: login → token storage → dashboard redirect

**Phase 2 Task 2.2 Complete - Organization Management:**
- Organization registration endpoint (`/api/v1/auth/register`) with validation
- Organization-specific API routes with proper multi-tenant context
- Enhanced dashboard with organization settings and management features
- Multi-tenant data isolation tested and verified working correctly

**Key Features Added:**
- Registration page (`/register`) with complete organization onboarding
- Settings page (`/dashboard/settings`) for organization profile management
- Organization context dependency for API route scoping
- Multi-tenant data isolation preventing cross-organization data access
- Organization-specific endpoints (`/api/v1/organizations/me`, `/api/v1/organizations/programs`)

**Testing Results:**
- Registration endpoint tested with new organization creation
- Multi-tenant isolation verified: different organizations see only their own data
- Organization context properly scoped in all API routes
- Frontend-backend integration working for all organization management features

## Phase 3 Complete - Questionnaire Builder System

### Phase 3 Task 3.1 Complete - Question Types & Models
**Complete Question System Implementation:**
- All 4 question types implemented: text, multiple choice, scale, file upload
- Comprehensive Pydantic schemas with validation for each question type
- Full CRUD API endpoints with multi-tenant security
- Question ordering system with drag-and-drop reordering support
- Comprehensive validation rules and response validation
- Security measures including input sanitization and XSS prevention
- 50 question limit per questionnaire enforcement

**Key Features Added:**
- Question schemas (`backend/app/schemas/question.py`) with type-safe validation
- Question API endpoints (`backend/app/api/v1/endpoints/questions.py`) with full CRUD operations
- Question service (`backend/app/services/question_service.py`) with business logic and validation
- Question validators (`backend/app/utils/question_validators.py`) with security checks
- Test scripts for verification of all functionality

### Phase 3 Task 3.2 Complete - Questionnaire Builder UI
**Complete Frontend Questionnaire Builder:**
- Full questionnaire management interface with listing and creation
- Interactive question builder with all 4 question types
- Drag-and-drop question reordering with visual feedback
- Real-time preview mode showing user-facing form
- Comprehensive validation and 50-question limit enforcement
- API integration layer ready for backend questionnaire endpoints

**Key Features Added:**
- Questionnaire pages (`/dashboard/questionnaires`, `/dashboard/questionnaires/builder`)
- Question type builders for text, multiple choice, scale, and file upload
- Question preview component with realistic form rendering
- Drag-and-drop functionality using HTML5 APIs
- API service layer (`src/services/api.ts`) with error handling
- Navigation integration from dashboard

**Testing Results:**
- All question types creating and configuring correctly
- Drag-and-drop reordering working smoothly
- Preview mode showing accurate form representation
- Form validation preventing invalid submissions
- API integration layer ready for backend connection
- Multi-tenant security maintained throughout UI

---
*This file serves as my persistent memory for the VDP project. Updated: 2025-07-18*