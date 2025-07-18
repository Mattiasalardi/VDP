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

### 1. Accelerator Setup (One-time per program)
1. Staff logs into platform (single shared login per accelerator)
2. Creates new program (e.g., "TechEd Accelerator 2024")
3. Builds custom questionnaire (max 50 questions)
4. Completes calibration questions about startup preferences
5. AI generates scoring guidelines based on calibration responses
6. User reviews and modifies AI-generated guidelines
7. System generates unique application links

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
- **Primary AI**: Claude API (Anthropic)
- **Document Processing**: PyPDF2/pdfplumber
- **Prompt Storage**: Configurable templates in database

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
- Single user login per accelerator (shared credentials)
- JWT-based authentication for staff access

### Multi-tenancy
- Accelerators can run multiple programs simultaneously
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
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-... (optional for PDF extraction)
AWS_ACCESS_KEY_ID=... (if using S3)
AWS_SECRET_ACCESS_KEY=...
JWT_SECRET=...
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
- Phase 3 Task 3.1 Complete: Question Types & Models
- Complete question system with all 4 question types (text, multiple choice, scale, file upload)
- Comprehensive validation rules and ordering system
- Full CRUD API endpoints with multi-tenant security
- Ready for Phase 3 Task 3.2: Questionnaire Builder UI

## Development Priorities
1. ✅ Set up project structure (FastAPI + Next.js)
2. ✅ Create database schema
3. ✅ Implement authentication system
4. ✅ Build organization management
5. 🔄 Implement questionnaire builder (Task 3.1 Complete)
6. 🔄 Build calibration system
7. 🔄 Create public application forms
8. 🔄 Integrate AI processing pipeline
9. 🔄 Develop report generation
10. 🔄 Build staff dashboard

---
*Last updated: 2025-07-18*
*This document serves as the central reference for the VDP application build process.*