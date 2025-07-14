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
│   │   │   └── config.py   # App settings
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI app entry point
│   ├── migrations/         # Database migrations
│   ├── scripts/           # Backend scripts
│   ├── tests/             # Backend tests
│   ├── venv/              # Python virtual environment
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
- **app/api/**: API route organization (v1 versioning structure)
- **requirements.txt**: All Python dependencies including FastAPI, SQLAlchemy, Anthropic SDK
- **venv/**: Isolated Python virtual environment
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
1. **Model changes**: TBD
2. **Migration creation**: TBD
3. **Update scripts**: TBD

## Configuration Files
- **Environment variables**: `.env` (development), `.env.example` (template)
- **Database config**: `backend/app/core/config.py` (DATABASE_URL, Redis settings)
- **API settings**: `backend/app/core/config.py` (CORS, JWT, API keys)
- **Build config**: `docker-compose.yml` (development environment)
- **Container config**: `backend/Dockerfile`, `frontend/Dockerfile`

## Key Constants & Utilities
*Will be populated as utilities are created*

---
*This map is updated as the codebase grows - always kept current*