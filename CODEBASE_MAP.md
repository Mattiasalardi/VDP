# VDP Codebase Map

## Overview
Your GPS for navigating the VDP codebase. Find files, understand structure, and locate functionality quickly.

## Project Structure

```
VDP_app/
├── backend/                 # FastAPI application
│   ├── app/                 # Main application code
│   │   ├── api/            # API routes
│   │   │   ├── deps/       # Dependencies
│   │   │   └── v1/         # API v1 routes
│   │   │       └── endpoints/  # Route handlers
│   │   ├── core/           # Core configuration
│   │   │   ├── config.py   # App settings
│   │   │   ├── database.py # Database connection & session management
│   │   │   └── seed_data.py # Test data generation
│   │   ├── models/         # Database models (SQLAlchemy)
│   │   │   ├── __init__.py # Model exports
│   │   │   ├── base.py     # Base model with timestamps
│   │   │   ├── organization.py # Organization model
│   │   │   ├── program.py  # Program model
│   │   │   ├── questionnaire.py # Questionnaire model
│   │   │   ├── question.py # Question model
│   │   │   ├── calibration_answer.py # Calibration model
│   │   │   ├── ai_guideline.py # AI Guidelines model
│   │   │   ├── application.py # Application model
│   │   │   ├── response.py # Response model
│   │   │   ├── uploaded_file.py # File upload model
│   │   │   ├── report.py   # Report model
│   │   │   └── score.py    # Score model
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI app entry point
│   ├── alembic/            # Database migrations
│   │   ├── versions/       # Migration files
│   │   │   └── 001_initial_schema.py # Initial schema migration
│   │   ├── env.py          # Alembic environment configuration
│   │   └── script.py.mako  # Migration template
│   ├── alembic.ini         # Alembic configuration
│   ├── scripts/           # Backend scripts
│   │   └── manage_db.py   # Database management utility
│   ├── tests/             # Backend tests
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/              # Next.js application
│   ├── src/               # Source code
│   │   └── app/           # App router pages
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── docker-compose.yml     # Development environment
├── .env                   # Environment variables
├── .env.example          # Environment template
└── *.md                  # Documentation files
```

## Key Directories

### Backend (`/backend/`)
- **app/main.py**: FastAPI application entry point with CORS setup
- **app/core/config.py**: Centralized configuration using Pydantic settings
- **app/core/database.py**: Database connection, session management, and helper functions
- **app/core/seed_data.py**: Comprehensive seed data for testing and development
- **app/models/**: Complete SQLAlchemy models for all 9 core tables
- **app/api/**: API route organization (v1 versioning structure)
- **alembic/**: Database migration system with initial schema
- **scripts/manage_db.py**: Database management utility (create, drop, seed, reset)
- **requirements.txt**: All Python dependencies including FastAPI, SQLAlchemy, Anthropic SDK
- **Dockerfile**: Container configuration for backend service

### Frontend (`/frontend/`)
- **src/app/**: Next.js 14 App Router structure
- **src/app/page.tsx**: Main landing page component
- **src/app/layout.tsx**: Root layout with metadata
- **src/app/globals.css**: Global styles with Tailwind CSS
- **package.json**: Node.js dependencies (React, Next.js, TypeScript, Tailwind)
- **Dockerfile**: Container configuration for frontend service

## Where to Find Things

### Authentication & Security
- **Login logic**: TBD
- **JWT handling**: TBD
- **Password hashing**: TBD

### Database
- **Models**: TBD
- **Migrations**: TBD
- **Schema definitions**: TBD

### Questionnaires
- **Builder UI**: TBD
- **Question types**: TBD
- **Form rendering**: TBD

### AI Integration
- **Claude API calls**: TBD
- **Prompt templates**: TBD
- **Response processing**: TBD

### File Processing
- **PDF upload**: TBD
- **Text extraction**: TBD
- **File storage**: TBD

### Report Generation
- **PDF creation**: TBD
- **Report templates**: TBD
- **Score calculation**: TBD

## Common Tasks & File Locations

### Adding a New Endpoint
1. **Route definition**: TBD
2. **Schema/validation**: TBD
3. **Business logic**: TBD
4. **Database operations**: TBD

### Adding a New UI Component
1. **Component files**: TBD
2. **Styling**: TBD
3. **API integration**: TBD

### Modifying Database Schema
1. **Model changes**: Update SQLAlchemy models in `backend/app/models/`
2. **Migration creation**: `python3 -m alembic revision --autogenerate -m "Description"`
3. **Migration application**: `python3 -m alembic upgrade head`
4. **Database reset**: `python backend/scripts/manage_db.py reset-db`

## Configuration Files
- **Environment variables**: `.env` (development), `.env.example` (template)
- **Database config**: `backend/app/core/config.py` (DATABASE_URL, Redis settings)
- **API settings**: `backend/app/core/config.py` (CORS, JWT, API keys)
- **Build config**: `docker-compose.yml` (development environment)
- **Container config**: `backend/Dockerfile`, `frontend/Dockerfile`

## Database Models (Complete)

### Core Tables & Relationships
- **organizations**: Accelerator accounts with authentication (email/password_hash)
- **programs**: Multiple programs per organization with cascading relationships
- **questionnaires**: Question sets for each program (50 question limit)
- **questions**: Individual questions with types (text, multiple_choice, scale, file_upload)
- **calibration_answers**: Accelerator preferences for AI guideline generation
- **ai_guidelines**: Generated scoring guidelines with versioning and templates
- **applications**: Startup applications with unique URLs and processing status
- **responses**: Flexible JSON storage for questionnaire answers
- **uploaded_files**: PDF document references with text extraction status
- **reports**: Generated reports with 10-section scoring structure
- **scores**: Detailed scoring breakdown with override capabilities

### Model Features
- **BaseModel**: Common timestamps (created_at, updated_at) and ID fields
- **Relationships**: Complete foreign key relationships with cascade deletes
- **JSON Fields**: Flexible data storage for options, validation rules, and values
- **Indexing**: Performance optimized with proper database indexes
- **Migration Support**: Alembic-ready with initial schema migration

## Key Constants & Utilities
- **Database Management**: `backend/scripts/manage_db.py` with create/drop/seed/reset commands
- **Seed Data**: Comprehensive test data in `backend/app/core/seed_data.py`
- **Configuration**: Environment-based settings in `backend/app/core/config.py`

---
*This map is updated as the codebase grows - always kept current*
*Last Updated: 2025-07-15 - Database foundation complete*