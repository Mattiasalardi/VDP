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
2. **Program Management Dashboard**: View all programs with statistics and completion status
3. **Create New Program** (unlimited programs per organization, e.g., "TechEd Accelerator 2024", "Healthcare Innovation Track", "AI/ML Program")
4. **Select Program** → Enter program-specific workspace with independent:
   - Questionnaire Builder (program-scoped, max 50 questions)
   - Calibration Settings (program-specific preferences)
   - AI Guidelines Management (generated per program)
   - Application Management (program-isolated)
   - Reports & Analytics (program-scoped)
5. **Complete Program Setup** per program:
   - Build custom questionnaire for this specific program
   - Complete calibration questions about startup preferences for this program
   - AI generates scoring guidelines based on program-specific calibration
   - Review and modify AI-generated guidelines for this program
   - System generates unique application links for this program

### 2. Startup Application
1. Startup receives unique link (e.g., platform.com/apply/teched-2024/startup-abc123)
2. Fills out questionnaire (text, multiple choice, scale, file uploads)
3. Uploads PDF documents (generous size limit)
4. Submits application
5. System immediately processes application

### 3. AI Processing Pipeline
1. Extracts text from uploaded PDFs
2. Analyzes responses using pre-generated scoring guidelines
3. Generates scores for various criteria
4. Creates comprehensive PDF report
5. Stores everything in database

### 4. Review and Decision Making
1. Staff views generated reports in dashboard
2. Reviews scores, summaries, and highlighted concerns
3. Can override AI scores if needed
4. Ranks startups in sortable table for comparison

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

### Multi-Program Architecture
- **Unlimited Programs**: Each organization can create unlimited programs
- **Complete Program Isolation**: Each program operates independently with:
  - Separate questionnaires (max 50 questions per program)
  - Independent calibration settings and AI guidelines
  - Isolated application pools and reports
  - Program-specific analytics and statistics
- **No Cross-Program Data Sharing**: Programs cannot access each other's data
- **Program-Scoped Features**: All features (questionnaires, guidelines, applications) are program-specific
- No application deadlines (for MVP)
- Unlimited applications per program

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

## AI Prompt Structure

### 1. Guideline Generation Prompt
- **Input**: Calibration answers from accelerator
- **Process**: Start with base scoring template, adapt based on responses
- **Output**: JSON schema with scoring weights and evaluation criteria
- **User Review**: Present to user for modifications

### 2. Analysis Prompt
- **Input**: Questions + Responses + Guidelines + PDF text
- **Output**: Structured analysis with scores and summaries

### 3. Report Generation Prompt
- **Input**: Analysis results
- **Output**: Formatted text for each report section

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

### Multi-Program Architecture Implementation
- **Complete Program Management**: Create, manage, and switch between unlimited programs per organization
- **Program-Centric Workflow**: Each program operates independently with separate questionnaires, calibration, guidelines, and applications
- **Data Isolation**: Complete separation between programs - no cross-program data sharing
- **Program Dashboard**: Individual program workspaces with setup progress tracking and statistics
- **API Integration**: Program-scoped endpoints with proper multi-tenant security
- **Frontend Navigation**: Program selection interface with program-specific feature access

### Technical Implementation Complete
- Backend: Program schemas, service layer, and REST API endpoints (7 endpoints)
- Frontend: Program management UI, program selection, individual program dashboards
- Database: Program-scoped relationships with proper foreign key constraints
- Security: Multi-tenant isolation at organization and program levels
- Testing: Comprehensive test scripts for all program management functionality

## Development Priorities
1. ✅ Set up project structure (FastAPI + Next.js)
2. ✅ Create database schema with multi-program architecture
3. ✅ Implement authentication system
4. ✅ Build organization management with multi-tenant security
5. ✅ Implement questionnaire builder with program isolation
6. ✅ Build complete calibration system (4.1, 4.2, 4.3 Complete)
7. ✅ Create program management system with complete isolation
8. 🔄 Create program-scoped public application forms
9. 🔄 Integrate AI processing pipeline with program context
10. 🔄 Develop program-specific report generation
11. 🔄 Build program-centric staff dashboard

---
*Last updated: 2025-07-21*
*This document serves as the central reference for the VDP application build process.*