# Claude Memory - VDP Application Build

## Project Summary
Building an AI-powered application management platform for startup accelerators. The platform automates evaluation of startup applications through customizable questionnaires and AI-generated assessment reports.

## Key Context
- **Full Details**: All comprehensive project information is stored in `PROJECT_CONTEXT.md`
- **Development Plan**: Detailed 9-phase roadmap in `DEVELOPMENT_ROADMAP.md`
- **Debug Solutions**: Common issues and fixes tracked in `DEBUG.md`
- **Tech Stack**: FastAPI (Python) backend, Next.js frontend, PostgreSQL database, Claude AI integration
- **MVP Focus**: Questionnaire builder, calibration system, public forms, AI processing, report generation, dashboard
- **Current Status**: Ready to start Phase 1 - no existing codebase yet

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
*Will be populated as project structure is established*

## Current Development Status
**Phase**: 1 (Foundation & Infrastructure) - Not Started
**Next Task**: 1.1 - Initialize FastAPI backend project with proper directory structure
**Total Phases**: 9 phases, estimated 25-35 hours total
**Dependencies**: None for Phase 1

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

---
*This file serves as my persistent memory for the VDP project. Updated: 2025-07-11*