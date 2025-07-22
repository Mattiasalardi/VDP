# VDP (Venture Development Platform) - Project Context

## Project Overview
AI-powered application management platform designed for startup accelerators. Automates evaluation of hundreds of startup applications through customizable questionnaires and AI-generated assessment reports.

## Core Problem & Solution

### Problem
- Accelerators receive hundreds of applications per program
- Manual review is time-consuming and inconsistent
- Lack of standardized evaluation criteria

### Solution
- Automated initial screening through AI analysis
- Customizable questionnaires for data collection
- Standardized scoring and comprehensive reports
- Ranking system for easy comparison

## Key User Flows

### 1. Program Management & Setup (Multi-program per organization)
1. Staff logs into platform (single shared login per organization)
2. **Main Dashboard** → **"Manage Programs"** (program selection is mandatory - no direct feature access)
3. **Program Management Dashboard**: View all programs with statistics and completion status
4. **Create New Program** (unlimited programs per organization, e.g., "TechEd Accelerator 2024", "Healthcare Innovation Track", "AI/ML Program")
5. **Select Program** → **Individual Program Dashboard** → Enter program-specific workspace with complete isolation:
   - Program-Scoped Questionnaire Builder (`/dashboard/programs/{id}/questionnaires`)
   - Program-Specific Calibration Settings (`/dashboard/programs/{id}/calibration`)
   - Program-Isolated AI Guidelines Management (`/dashboard/programs/{id}/guidelines`)
   - Program-Exclusive Application Management (`/dashboard/programs/{id}/applications`)
   - Program-Dedicated Reports & Analytics (future)
6. **Complete Program Setup** per program (enforced program-centric workflow with mandatory onboarding):
   - Navigate to program dashboard first
   - **MANDATORY ONBOARDING STEP**: Complete calibration questions (determines accelerator's values for this program)
     * Calibration answers are PERMANENT and persistent (unless user explicitly changes them)
     * Questions cover importance weights: revenue stage, team experience, innovation, etc.
     * These answers feed into AI Guidelines generation (AI #1)
   - Build custom questionnaires for this specific program (sent to startup applicants)
   - AI generates persistent scoring guidelines based on program-specific calibration (AI #1)
   - Review and modify AI-generated guidelines for this program (remains same unless changed)
   - Set up applicant management system for tracking startup applications

### 2. Startup Application (Program-Specific)
1. Startup receives unique program-specific link (e.g., platform.com/apply/program-123/startup-abc456)
2. Fills out questionnaire designed specifically for that program (text, multiple choice, scale, file uploads)
3. Uploads PDF documents (generous size limit) - stored with program context
4. Submits application to specific program only
5. System immediately processes application using that program's AI guidelines only

### 3. AI Processing Pipeline (Program-Isolated)
1. Extracts text from uploaded PDFs with program context
2. Analyzes responses using program-specific scoring guidelines only
3. Generates scores based on that program's criteria only
4. Creates comprehensive PDF report using program's template
5. Stores everything in database with program isolation

### 4. Applicant Management & Tracking (Program-Scoped)
1. Staff navigates to program dashboard → Applications page (spreadsheet-like interface)
2. **Create Application Entries**: Manually add startup applications with:
   - Startup name
   - Contact email (where questionnaire will be sent)
   - Select which questionnaire to send (from program's created questionnaires)
3. **Track Application Activity** in real-time:
   - Status tracking: "Not Sent", "Sent", "Completed", "Processing", "Report Ready"
   - Submitted date and time
   - Link to generated report (when ready)
   - **Total ranking score** with color coding (0=red, 10=green, gradient in between)
4. **Sorting & Management Capabilities**:
   - Sort by startup name, application date, total score
   - Filter by completion status
   - Quick toggle between completed vs pending applications
   - Export data functionality

### 5. Review and Decision Making (Program-Scoped)
1. Staff uses applicant management interface to review all applications for that program
2. Views AI-generated reports with scores and summaries using program-specific criteria
3. Can override AI scores within program context
4. Ranks startups only against others in the same program using color-coded scoring

## Technical Architecture

### Backend Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Caching**: Redis
- **File Storage**: AWS S3 or local storage
- **Authentication**: JWT tokens

### Frontend Stack
- **Staff Dashboard**: React/Next.js
- **Public Forms**: Next.js (mobile-responsive)

### AI Integration
- **Primary AI**: OpenRouter API with developer-configurable models (Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, GPT-4 variants)
- **Document Processing**: PyPDF2/pdfplumber
- **Prompt Storage**: Configurable templates in database
- **Rate Limiting**: 10 requests per organization per hour
- **Caching**: Redis-based 24-hour TTL for guidelines generation

### Key Libraries
- **PDF Generation**: ReportLab or Puppeteer
- **File Upload**: Multer
- **API Client**: Anthropic Python SDK

## Database Schema (Core Tables)

```sql
organizations          -- Accelerator accounts
programs               -- Different accelerator programs
questionnaires         -- Question sets per program
questions              -- Individual questions with types
calibration_answers    -- Accelerator preferences
ai_guidelines          -- Generated scoring guidelines
applications           -- Startup applications with unique IDs
responses              -- Answers to questionnaire questions
uploaded_files         -- PDF document references
reports                -- Generated PDF reports with scores
scores                 -- Detailed scoring breakdown
```

## MVP Features (Priority Order)

### 1. Questionnaire Builder
- Text (short/long), multiple choice, scale (1-10), file upload questions
- Drag-and-drop question ordering
- Question preview functionality
- 50 question limit per questionnaire

### 2. Calibration System
- Pre-defined calibration questions for accelerators
- Questions about importance weights and preferences
- AI generates base scoring template and adapts based on responses
- User can modify/add/remove AI-generated guidelines

### 3. Public Application Form
- Clean, mobile-responsive design
- Progress indicator
- File upload with progress bars (PDF only)
- Unique URL per applicant (non-guessable)

### 4. AI Processing
- Immediate processing upon form submission
- PDF text extraction
- Response analysis based on guidelines
- Score generation and summaries
- PDF report creation

### 5. Report Generation
- Fixed template structure:
  - Overall score and summary
  - Problem-Solution Fit
  - Ideal Customer Profile
  - Product & Technology
  - Team Structure
  - Market Opportunity
  - Financial Overview
  - Key Challenges
  - Validation & Achievements
  - Areas for investigation
- 1-10 scale scores with justifications
- Exportable as PDF

### 6. Dashboard
- List view of all applications
- Sortable by various scores
- Quick stats (total applications, average scores)
- Download individual or bulk reports

## Business Rules & Constraints

### Authentication & Access
- Single user login per organization (shared credentials for accelerator staff)
- JWT-based authentication for staff access
- Organization-level security with complete data isolation

### Multi-Program Architecture & UX Logic
- **Unlimited Programs**: Each organization can create unlimited programs (e.g., "Tech Industry Worldwide", "Education Startups UK")
- **Complete Program Isolation**: Each program operates independently with:
  - Separate questionnaires (max 50 questions per program)
  - Independent calibration settings and AI guidelines (permanent unless changed)
  - Isolated application pools and reports
  - Program-specific applicant management and tracking
- **Enforced Program-Centric Workflow**: 
  - Main dashboard only allows program selection or settings access
  - No direct feature access without selecting a program first
  - All features accessed through program-specific routes
- **Mandatory Onboarding Flow**: Each program requires calibration completion before full functionality
- **No Cross-Program Data Sharing**: Programs cannot access each other's data
- **Program-Scoped Features**: All features (questionnaires, guidelines, applications) are program-specific
- No application deadlines (for MVP)
- Unlimited applications per program

### Applicant Management Rules
- Manual application entry by accelerator staff (startup name, email, questionnaire selection)
- Real-time activity tracking and status updates
- Color-coded scoring system (0-10 scale with visual indicators)
- Sortable and filterable applicant lists per program
- One-to-one relationship: each application tied to specific program and questionnaire

### File Management
- PDF uploads only
- Generous size limit to prevent misuse
- Secure file upload with virus scanning

### Data Management
- All data stored indefinitely
- GDPR compliance required
- Proper database indexing for performance

### Branding
- Platform branding only (no custom accelerator branding for MVP)

## AI Processing Architecture (Two-Stage System)

### AI #1: Guidelines Generation (Calibration → Guidelines)
- **Purpose**: Convert accelerator preferences into scoring guidelines
- **Input**: Program-specific calibration answers (permanent unless changed)
- **Process**: Analyze importance weights (e.g., 5/10 revenue stage, 10/10 team experience, 1/10 innovation)
- **Output**: Persistent scoring guidelines with weights for each evaluation category
- **Frequency**: Generated once per calibration set, remains same unless user changes calibration

### AI #2: Application Processing (Questionnaire → Report)
- **Purpose**: Analyze each startup application against program guidelines
- **Input**: 
  - All questionnaire questions and startup answers
  - Uploaded PDF documents (text extracted)
  - Program-specific AI guidelines (from AI #1)
- **Process**: 
  - Read and analyze all responses
  - Apply importance weighting system from guidelines
  - Generate scores for each report section
- **Output**: 
  - Comprehensive PDF report with 10 sections
  - Overall score (0-10) sent back to applicant management dashboard
  - Detailed section scores with justifications

### Report Structure (Fixed Template)
- Overall score and executive summary
- Problem-Solution Fit analysis
- Ideal Customer Profile assessment
- Product & Technology evaluation
- Team Structure and experience
- Market Opportunity analysis
- Financial Overview assessment
- Key Challenges identification
- Validation & Achievements review
- Areas for investigation and follow-up

## Performance Requirements

### Speed
- Report generation within 30 seconds
- Handle 100+ concurrent applications
- Fast page loads with CDN for static assets

### Caching Strategy
- Cache AI guidelines to reduce API calls
- Redis for temporary data storage
- Background job processing for heavy tasks

### Security
- Rate limiting on public forms
- Secure file upload validation
- Non-guessable application URLs

## Environment Variables
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
OPENROUTER_API_KEY=sk-...
OPENAI_API_KEY=sk-... (optional for PDF extraction)
AWS_ACCESS_KEY_ID=... (if using S3)
AWS_SECRET_ACCESS_KEY=...
JWT_SECRET=...
APP_DOMAIN=http://localhost:3000 (for rate limiting)
```

## Success Metrics
- Report generation < 30 seconds
- Handle 100+ concurrent applications
- 90%+ reports require no manual adjustment
- 80% reduction in accelerator review time

## Future Features (Post-MVP)
- Modify calibration and regenerate guidelines
- Multiple interview rounds tracking
- Email notifications
- Template sharing between programs
- Advanced analytics and insights
- API for external integrations
- Custom accelerator branding

## Current Status
- **Phase 1 Complete**: FastAPI foundation with authentication, database schema, and organization management
- **Phase 2 Complete**: Authentication system and multi-tenant organization management  
- **Phase 3 Complete**: Questionnaire Builder System with all 4 question types and frontend interface
- **Phase 4.1 Complete**: Calibration Questions System with comprehensive accelerator preferences
- **Phase 4.2 Complete**: AI Guidelines Generation with OpenRouter API integration and Redis caching
- **Phase 4.3 Complete**: Program Management System with multi-program architecture
- **Architecture Fix Complete**: Program-centric navigation and complete data isolation enforcement

### Multi-Program Architecture Implementation
- **Complete Program Management**: Create, manage, and switch between unlimited programs per organization
- **Enforced Program-Centric Workflow**: Users MUST select program first - no direct feature access from main dashboard
- **Complete Data Isolation**: Programs operate in complete isolation with no cross-program data sharing or access
- **Program-Scoped Navigation**: All features accessible only through program-specific routes (`/programs/{id}/feature`)
- **Individual Program Dashboards**: Dedicated workspaces with setup progress tracking and program-specific statistics
- **Program-Isolated API Integration**: All endpoints properly scoped to program context with multi-tenant security
- **Mandatory Program Context**: Frontend enforces program selection before accessing any features

### Technical Implementation Complete
- **Backend**: Program schemas, service layer, and REST API endpoints (7 endpoints) with complete program isolation
- **Frontend**: Program management UI, enforced program selection, individual program dashboards, program-scoped feature routes
- **Navigation Architecture**: Program-centric route structure (`/dashboard/programs/{id}/{feature}`) replacing global feature access
- **Database**: Program-scoped relationships with proper foreign key constraints ensuring complete data isolation
- **Security**: Multi-tenant isolation at organization and program levels with mandatory program context validation
- **User Experience**: Enforced program-centric workflow preventing access to features without program selection
- **Testing**: Comprehensive test scripts for all program management functionality and data isolation

## Development Priorities
1. ✅ Set up project structure (FastAPI + Next.js)
2. ✅ Create database schema with multi-program architecture
3. ✅ Implement authentication system
4. ✅ Build organization management with multi-tenant security
5. ✅ Implement questionnaire builder with program isolation
6. ✅ Build complete calibration system (4.1, 4.2, 4.3 Complete)
7. ✅ Create program management system with complete isolation
8. ✅ **ARCHITECTURE FIX**: Enforce program-centric navigation and data isolation
9. 🔄 **PHASE 5**: Create program-scoped public application forms
10. 🔄 Integrate AI processing pipeline with program context
11. 🔄 Develop program-specific report generation
12. 🔄 Build program-centric staff dashboard

## Ready for Phase 5
**Foundation Status**: ✅ **COMPLETE** - Multi-program architecture with enforced data isolation and program-centric workflow
**Next Step**: Phase 5 - Program-Scoped Public Application Forms

---
*Last updated: 2025-07-21*
*This document serves as the central reference for the VDP application build process.*