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
**Phase**: 4 Complete - Calibration System & Multi-Program Architecture + Architecture Fix Complete
**Next Phase**: 5 - Program-Scoped Public Application Forms (READY TO START)
**Total Phases**: 9 phases, estimated 30-40 hours total
**Dependencies**: Phase 1 ✅, Phase 2 ✅, Phase 3 ✅, Phase 4 ✅ (4.1 Calibration, 4.2 AI Guidelines, 4.3 Program Management, 4.4 Architecture Fix all complete)

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

## Phase 4 Task 4.1 Complete - Calibration Questions

### Calibration System Foundation
**Pre-defined Calibration Question Set:**
- 12 comprehensive calibration questions covering all key accelerator evaluation criteria
- 5 organized categories: Team & Founders, Market & Opportunity, Business Model, Technology & Innovation, Investment Criteria
- Multiple question types: scale (1-10), multiple choice, and text input
- Smart validation and scoring guidelines preparation

**Key Features Added:**
- Calibration questions (`backend/app/core/calibration_questions.py`) with comprehensive accelerator preferences
- Calibration schemas (`backend/app/schemas/calibration.py`) with Pydantic v2 compatibility
- Calibration service (`backend/app/services/calibration_service.py`) with full business logic
- Calibration API endpoints (`backend/app/api/v1/endpoints/calibration.py`) with complete CRUD operations
- Frontend calibration interface (`/dashboard/calibration`) with category-based workflow

**Calibration Categories Implemented:**
1. **Team & Founders**: Importance of founding team experience and background
2. **Market & Opportunity**: Market size preferences, industry verticals, geographic focus
3. **Business Model & Traction**: Revenue stage, scalability focus, customer validation requirements
4. **Technology & Innovation**: Technology importance, competitive analysis weight
5. **Investment Criteria**: Funding stage comfort, risk tolerance, social impact importance

**Technical Implementation:**
- Multi-tenant security with organization-scoped program access
- Completion tracking with percentage calculations and missing question identification
- Batch answer submission for efficient category-based saving
- Real-time validation with question-type specific rules
- Session management for preserving progress across categories

**Testing Results:**
- All 12 calibration questions loading correctly with 5 category organization
- Authentication and authorization working properly
- Single and batch answer submission functioning correctly
- Progress tracking updating accurately (tested 33.3% → 41.7% progression)
- Frontend-backend integration ready for full calibration workflow
- API endpoints tested and validated with comprehensive test script

## Phase 4 Task 4.2 Complete - AI Guidelines Generation

### OpenRouter AI Integration System
**Secure AI Guidelines Generation:**
- Updated calibration questions to 8 report-aligned categories for better AI guidelines
- Complete OpenRouter API service with secure environment variable handling
- Developer-configurable AI model support: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, GPT-4 variants
- JSON-only response validation with comprehensive error handling and fallback parsing
- Intelligent prompt generation based on calibration responses with dynamic category weighting

**Security & Rate Limiting:**
- 10 requests per organization per hour rate limiting with Redis-based distributed system
- 2000 token limit per request with comprehensive request validation
- Memory-based fallback when Redis unavailable
- All API keys stored in environment variables only (.env)
- Comprehensive API call logging with organization tracking for monitoring

**AI Guidelines Architecture:**
- Complete guidelines API ecosystem with 6 endpoints: generate, save, get active, history, activate version
- Guidelines versioning system with activation/deactivation workflow
- Draft and approval system for review before activation
- Base categories aligned with final report structure: Problem-Solution Fit, Customer Profile & Business Model, Product & Technology, Team Assessment, Market Opportunity, Competition & Differentiation, Financial Overview, Validation & Achievements
- Dynamic weight adjustment based on accelerator preferences from calibration answers

**Advanced Caching System:**
- Redis-based intelligent caching using calibration answers + model combination as cache key
- 24-hour TTL with automatic cache invalidation for optimal performance
- Significant API call reduction for identical requests
- Graceful fallback handling when Redis unavailable

**Frontend Guidelines Management:**
- Interactive guidelines generation interface for AI-powered guideline creation
- Real-time JSON preview with edit mode for modifications
- Visual guidelines rendering showing categories, weights, and scoring guidance
- Complete guidelines history with version management and activation controls
- Approval workflow allowing draft review before activation
- Seamless integration with existing dashboard navigation

**Key Features Added:**
- OpenRouter service (`backend/app/services/openrouter_service.py`) with multi-model support and caching
- Rate limiter (`backend/app/services/rate_limiter.py`) with Redis and memory fallback
- AI guidelines service (`backend/app/services/ai_guidelines_service.py`) with complete business logic
- AI guidelines API endpoints (`backend/app/api/v1/endpoints/ai_guidelines.py`) with full CRUD operations
- Guidelines schemas (`backend/app/schemas/ai_guidelines.py`) with comprehensive validation
- Frontend guidelines interface (`frontend/src/app/dashboard/guidelines/page.tsx`) with full workflow
- Comprehensive test script (`backend/scripts/test_ai_guidelines.py`) for validation
- Environment configuration template (`backend/.env.example`) for secure setup

**Testing Results:**
- Complete calibration → generation → review → storage workflow tested and validated
- All 6 API endpoints functioning correctly with proper authentication and authorization
- Rate limiting system tested with Redis and memory fallback scenarios
- Caching system validated with 24-hour TTL and cache key generation
- Frontend-backend integration working for all guidelines management features
- Multiple AI models tested successfully with JSON response validation
- Guidelines versioning and activation workflow tested end-to-end

## Program Management Foundation Complete

### Multi-Program Architecture Implementation
**Complete Program-Centric Workflow:**
- Full program CRUD operations with multi-tenant security and organization scoping
- Program-specific data isolation: each program has independent questionnaires, calibration answers, AI guidelines, and applications
- Complete separation between programs - no data sharing or interference between different programs
- Program statistics and completion tracking with real-time progress indicators

**Backend Program Management:**
- Program schemas (`backend/app/schemas/program.py`) with comprehensive validation and statistics
- Program service (`backend/app/services/program_service.py`) with complete business logic and data isolation
- Program API endpoints (`backend/app/api/v1/endpoints/programs.py`) with 7 REST endpoints for full CRUD operations
- Database design ensuring complete program separation with proper foreign key relationships

**Frontend Program Interface:**
- Program management page (`/dashboard/programs`) with creation modal, statistics grid, and program status tracking
- Individual program dashboards (`/dashboard/programs/[id]`) with setup progress, completion tracking, and direct navigation to program-specific features
- Updated main dashboard navigation to program-centric workflow
- Real-time statistics showing questionnaire count, calibration completion, guidelines status, and application count per program

**User Flow Architecture:**
1. **Dashboard** → **"📋 Manage Programs"** 
2. **Programs List** → **"Create Program"** (unlimited programs per organization)
3. **Select Program** → **Program-Specific Dashboard** with:
   - Questionnaire Builder (program-scoped)
   - Calibration Settings (program-scoped)  
   - AI Guidelines Management (program-scoped)
   - Application Management (program-scoped)
   - Reports and Analytics (program-scoped)

**Program Independence Verified:**
- Each program maintains completely separate calibration responses
- AI guidelines generated independently per program based on program-specific calibration data
- Questionnaires are program-scoped with no cross-program visibility
- Applications submitted to specific programs with complete data isolation
- Multi-tenant security prevents cross-organization program access

**Testing Results:**
- Program creation, listing, updating, and deletion tested and validated
- Program-specific data isolation confirmed across all features
- Multi-program workflow tested with independent calibration and guidelines generation
- Frontend-backend integration working for complete program management lifecycle
- Statistics and progress tracking accurate per individual program

## Phase 4 Task 4.3 Complete - Program Management System

### Multi-Program Architecture Implementation
**Complete Program Management System:**
- Unlimited programs per organization with complete data isolation
- Program-centric workflow replacing feature-centric approach
- Individual program dashboards with setup progress tracking
- Program selection interface with statistics and completion status
- Complete separation between programs - no cross-program data access

**Key Features Added:**
- Program schemas (`backend/app/schemas/program.py`) with comprehensive validation and statistics
- Program service (`backend/app/services/program_service.py`) with CRUD operations and data isolation
- Program API endpoints (`backend/app/api/v1/endpoints/programs.py`) with 7 REST endpoints
- Program management UI (`frontend/src/app/dashboard/programs/`) with grid view and creation modal
- Individual program dashboards (`frontend/src/app/dashboard/programs/[id]/`) with setup progress

**Program-Scoped Architecture:**
- **Database Level**: All features (questionnaires, calibration, guidelines, applications) linked to specific programs
- **API Level**: Program context injected into all endpoints with proper security
- **Frontend Level**: Program selection and program-specific navigation throughout application
- **Data Isolation**: Complete separation - each program operates independently with own data

**Technical Implementation:**
- 7 Program API endpoints: list, create, get, update, delete, duplicate, toggle-active
- Program statistics calculation: questionnaire count, calibration completion %, active guidelines, application count
- Multi-tenant security: organization + program level access control
- Program dashboard with setup progress visualization and completion tracking
- Soft delete functionality preserving data integrity while hiding inactive programs

**User Flow Transformation:**
- **Before**: Feature-centric (questionnaires → calibration → guidelines)
- **After**: Program-centric (select program → manage all features within program context)
- **Navigation**: Program selection → individual program workspace → program-scoped features
- **Isolation**: Each program completely independent with separate questionnaires, calibration, guidelines, applications

**Testing Results:**
- Program creation, listing, updating, and deletion all working correctly
- Data isolation verified - programs cannot access each other's data
- Frontend-backend integration fully functional with program context
- Program statistics accurately calculated and displayed
- Multi-program workflow tested with multiple programs per organization

## Critical Architecture Fix Complete - Program-Centric Navigation Enforcement

### Problem Identified and Solved
**CRITICAL ISSUE**: Frontend was still allowing direct feature access bypassing program selection
- Users could access `/dashboard/questionnaires`, `/dashboard/calibration` directly
- This completely broke the program isolation model and data integrity
- Program selection was optional instead of mandatory

### Solution Implemented (Task 4.4)
**Main Dashboard Fix:**
- Removed all direct feature links (questionnaires, calibration, guidelines)
- Made program selection the ONLY option from main dashboard  
- Added workflow guidance showing program-centric approach

**Program-Scoped Route Structure Created:**
- `/dashboard/programs/{id}/questionnaires` - Program-specific questionnaire builder
- `/dashboard/programs/{id}/calibration` - Program-specific calibration settings
- `/dashboard/programs/{id}/guidelines` - Program-specific AI guidelines  
- `/dashboard/programs/{id}/applications` - Program-specific application management

**Navigation Enforcement:**
- Updated all program dashboard links to use program-scoped routes
- Created placeholder pages for all program-scoped features
- Enforced program context in all navigation paths
- Prevented direct feature access without program selection

**User Flow Fixed:**
- **Before**: Dashboard → Direct Feature Access (BROKEN)
- **After**: Dashboard → "Manage Programs" → Select Program → Program Dashboard → Program Features (ENFORCED)

### Architecture Validation Complete
**✅ Database Level**: All models properly scoped with program foreign keys
**✅ API Level**: Complete program isolation with organization context validation  
**✅ Frontend Level**: Program-centric navigation enforced, no global feature access allowed
**✅ User Experience**: Program selection mandatory, complete data isolation maintained
**✅ Security**: Multi-tenant isolation at organization AND program levels

### Ready for Phase 5
The multi-program architecture foundation is now completely solid with enforced program-centric navigation. All data isolation is maintained and validated. Phase 5 can proceed with confidence that the program architecture will properly isolate all public application forms and submissions.

---
*This file serves as my persistent memory for the VDP project. Updated: 2025-07-21*