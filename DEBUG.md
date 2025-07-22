# VDP Debug Log

## Purpose
This file tracks common issues encountered during development and their solutions. It serves as a quick reference to avoid re-solving the same problems.

## How to Use
- **Search first**: Before debugging, search this file for similar issues
- **Add entries**: When we solve a problem, immediately document it here
- **Keep it concise**: Brief problem description + working solution
- **Tag by category**: Use clear categories for easy searching

## Categories
- **Setup & Environment**: Project initialization, dependencies, configuration
- **Database**: Schema issues, migrations, connection problems  
- **API & Backend**: FastAPI, authentication, endpoint issues
- **Frontend**: Next.js, React components, UI problems
- **AI Integration**: Claude API, prompt issues, processing failures
- **File Processing**: PDF handling, uploads, storage issues
- **Performance**: Optimization, caching, speed improvements
- **Deployment**: Production issues, environment variables

## Format
```
### [Category] Issue Title
**Problem**: Brief description of what went wrong
**Solution**: Exact steps/code that fixed it
**Context**: When this typically happens
---
```

---

## Development Environment Startup Troubleshooting

### [Setup & Environment] Development Server Won't Start
**Problem**: After closing and reopening the project, localhost won't load or services fail to start
**Solution**: Use the provided startup scripts
```bash
# Proper startup sequence
./start.sh    # Starts all services with proper orchestration
./stop.sh     # Properly shuts down all services
```
**Context**: Common when switching between Docker and local development, or after system restarts

### [Setup & Environment] Port Conflicts
**Problem**: "Port already in use" errors when starting services
**Solution**: 
```bash
# Check what's using the ports
lsof -i :3000    # Frontend
lsof -i :8000    # Backend  
lsof -i :5432    # PostgreSQL
lsof -i :6379    # Redis

# Kill specific processes
kill -9 <PID>

# Or use the stop script which handles this automatically
./stop.sh
```
**Context**: Happens when previous services didn't shut down cleanly

### [Setup & Environment] Docker Not Running
**Problem**: "Cannot connect to Docker daemon" or similar Docker errors
**Solution**:
1. Start Docker Desktop application
2. Wait for Docker to fully initialize (green icon)
3. Verify with: `docker info`
4. Then run: `./start.sh`
**Context**: Docker Desktop needs to be running before starting services

### [Database] Database Connection Refused
**Problem**: Backend can't connect to database, "connection refused" errors
**Solution**: Check database URL configuration
```bash
# In backend/.env, ensure URLs match your setup:
# For local development:
DATABASE_URL=postgresql://postgres:password@localhost:5432/vdp_db

# For Docker development:  
DATABASE_URL=postgresql://vdp_user:vdp_password@db:5432/vdp_db
```
**Context**: Mismatch between .env config and actual database location

### [Database] Database Tables Don't Exist
**Problem**: "relation does not exist" errors in backend logs
**Solution**: Initialize the database
```bash
cd backend
source .venv/bin/activate
python scripts/manage_db.py create-tables
python scripts/manage_db.py seed-data
```
**Context**: First-time setup or after database reset

### [Frontend] Frontend Build Failures or Module Errors
**Problem**: Next.js fails to start, TypeScript errors, or missing dependencies
**Solution**: 
```bash
# Navigate to correct frontend directory
cd frontend/frontend/frontend  # May vary based on nesting

# Clean and reinstall
rm -rf node_modules package-lock.json
npm install

# Start development server
npm run dev
```
**Context**: After dependency updates or when node_modules get corrupted

### [Setup & Environment] Services Start But Don't Respond
**Problem**: Ports appear open but services return connection errors
**Solution**: Check service health and logs
```bash
# Check service status
docker-compose ps

# View logs
tail -f backend.log
tail -f frontend.log
docker-compose logs db
docker-compose logs redis

# Test API health
curl http://localhost:8000/api/v1/health
```
**Context**: Services may be starting but not fully initialized

### [Setup & Environment] Nuclear Reset Option
**Problem**: Everything is broken and nothing works
**Solution**: Complete environment reset
```bash
# Stop everything
./stop.sh

# Clean Docker completely
docker-compose down -v --remove-orphans
docker system prune -f
docker volume prune -f

# Clean local files
rm -rf backend/.venv
rm -f *.log *.pid

# Restart Docker Desktop, then:
./start.sh
```
**Context**: Use this as last resort when normal troubleshooting fails

### [Setup & Environment] Quick Diagnostic Commands
**Problem**: Need to quickly diagnose what's wrong
**Solution**: Run these diagnostic commands
```bash
# Check running services
docker-compose ps
lsof -i :3000 -i :8000 -i :5432 -i :6379

# Check Docker
docker info
docker-compose version

# Check Python environment
cd backend && source .venv/bin/activate && python --version

# Check Node environment  
cd frontend/frontend/frontend && node --version && npm --version

# Test database connection
psql -h localhost -U vdp_user -d vdp_db -c "SELECT 1;"
```
**Context**: Use these commands to identify where the problem is

### [Setup & Environment] WORKING LOCAL STARTUP SEQUENCE (NO DOCKER)
**Problem**: Need to start localhost when Docker is not available  
**Solution**: EXACT steps that work on this system:
```bash
# 1. Create PostgreSQL user and database (ONLY NEEDED ONCE)
psql -h localhost -p 5432 -U postgres -c "CREATE USER vdp_user WITH ENCRYPTED PASSWORD 'vdp_password';"
psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE vdp_db OWNER vdp_user;"
psql -h localhost -p 5432 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vdp_db TO vdp_user;"
psql -h localhost -p 5432 -U postgres -d vdp_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vdp_user;"
psql -h localhost -p 5432 -U postgres -d vdp_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vdp_user;"

# 2. Setup backend environment (from project root)
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Initialize database (from backend directory)
python scripts/manage_db.py create-tables
# Note: seed-data may fail if data exists, that's OK

# 4. Start backend server (from backend directory)
nohup python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
echo $! > ../backend.pid

# 5. Wait and test backend
sleep 3
curl http://localhost:8000/health
# Should return: {"status":"healthy","database":"connected"}

# 6. Setup and start frontend (from project root)
cd frontend/frontend/frontend
npm install
nohup npm run dev > ../../../frontend.log 2>&1 &
echo $! > ../../../frontend.pid

# 7. Check frontend port (may use 3001 if 3000 is busy)
tail -5 frontend.log
# Look for: "- Local: http://localhost:3001"

# FINAL URLs:
# Frontend: http://localhost:3001 (or 3000)
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# 
# Test Login: admin@teched-accelerator.com / admin123
```
**Context**: These exact steps worked on 2025-07-22. Backend runs on port 8000, frontend auto-detects available port (3000 or 3001). PostgreSQL must be running locally.

### [Setup & Environment] Stop Local Development Servers
**Problem**: Need to cleanly stop all local development servers
**Solution**: Kill processes by PID files or ports
```bash
# Stop by PID files (recommended)
if [ -f backend.pid ]; then kill $(cat backend.pid) && rm backend.pid; fi
if [ -f frontend.pid ]; then kill $(cat frontend.pid) && rm frontend.pid; fi

# Or stop by ports (backup method)
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend (port 3000)
lsof -ti :3001 | xargs kill -9  # Frontend (port 3001)

# Or use the stop script
./stop.sh
```
**Context**: Always stop cleanly to avoid port conflicts on restart

---
*Debug entries will be added as we encounter and solve issues during development.*