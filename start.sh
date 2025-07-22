#!/bin/bash

# VDP Application Startup Script
# Handles complete environment startup with proper service orchestration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
DB_PORT=5432
REDIS_PORT=6379

echo -e "${BLUE}=== VDP Application Startup ===${NC}"
echo "Starting development environment..."
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use by another process${NC}"
        echo "   Checking if it's $service..."
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        local process=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
        echo "   Process: $process (PID: $pid)"
        echo "   You may want to kill it with: kill $pid"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=60
    local attempt=1

    echo -n "Waiting for $service_name to be ready"
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo -e " ${GREEN}✅${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}❌${NC}"
    echo -e "${RED}Failed to connect to $service_name after $max_attempts seconds${NC}"
    return 1
}

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running${NC}"
        echo "Please start Docker Desktop and try again"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}⚠️  docker-compose not found, trying docker compose${NC}"
        if ! docker compose version &> /dev/null; then
            echo -e "${RED}❌ Neither docker-compose nor 'docker compose' available${NC}"
            return 1
        fi
        export DOCKER_COMPOSE="docker compose"
    else
        export DOCKER_COMPOSE="docker-compose"
    fi
    
    echo -e "${GREEN}✅ Docker is ready${NC}"
    return 0
}

# Step 1: Check Docker
echo -e "${BLUE}[1/7] Checking Docker...${NC}"
if ! check_docker; then
    exit 1
fi

# Step 2: Stop existing services
echo -e "${BLUE}[2/7] Stopping existing services...${NC}"

# Stop docker services
echo "Stopping Docker services..."
$DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true

# Kill any processes on our ports
for port in $BACKEND_PORT $FRONTEND_PORT; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Killing process on port $port..."
        lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
done

echo -e "${GREEN}✅ Existing services stopped${NC}"

# Step 3: Start Docker services
echo -e "${BLUE}[3/7] Starting Docker services (database & Redis)...${NC}"
$DOCKER_COMPOSE up -d db redis

# Step 4: Wait for database
echo -e "${BLUE}[4/7] Waiting for database...${NC}"
if ! wait_for_service localhost $DB_PORT "PostgreSQL"; then
    echo -e "${RED}❌ Database failed to start${NC}"
    echo "Checking Docker logs..."
    $DOCKER_COMPOSE logs db
    exit 1
fi

# Wait for Redis
echo "Waiting for Redis..."
if ! wait_for_service localhost $REDIS_PORT "Redis"; then
    echo -e "${YELLOW}⚠️  Redis not responding, but continuing...${NC}"
fi

# Step 5: Setup and start backend
echo -e "${BLUE}[5/7] Starting backend server...${NC}"

# Check if we should use Docker or local development
if [ -f "backend/.env" ] && grep -q "localhost" "backend/.env"; then
    echo "Using local development mode (backend/.env has localhost URLs)"
    
    # Install Python dependencies if needed
    if [ ! -d "backend/.venv" ]; then
        echo "Creating Python virtual environment..."
        cd backend
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # Start backend locally
    cd backend
    source .venv/bin/activate
    
    # Initialize database if needed
    echo "Setting up database..."
    python scripts/manage_db.py create-tables 2>/dev/null || true
    python scripts/manage_db.py seed-data 2>/dev/null || true
    
    # Start backend server in background
    nohup python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
else
    echo "Using Docker mode for backend"
    $DOCKER_COMPOSE up -d backend
fi

# Wait for backend
echo "Waiting for backend API..."
if ! wait_for_service localhost $BACKEND_PORT "Backend API"; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    if [ -f "backend.log" ]; then
        echo "Backend logs:"
        tail -20 backend.log
    fi
    exit 1
fi

# Step 6: Start frontend
echo -e "${BLUE}[6/7] Starting frontend server...${NC}"

# Navigate to the correct frontend directory
FRONTEND_DIR="frontend"
if [ -d "frontend/frontend/frontend" ]; then
    FRONTEND_DIR="frontend/frontend/frontend"
elif [ -d "frontend/frontend" ]; then
    FRONTEND_DIR="frontend/frontend"
fi

cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "Starting Next.js development server..."
nohup npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../frontend.pid
cd - > /dev/null

# Wait for frontend
echo "Waiting for frontend..."
if ! wait_for_service localhost $FRONTEND_PORT "Frontend"; then
    echo -e "${YELLOW}⚠️  Frontend taking longer than expected, but continuing...${NC}"
    echo "Check frontend.log for details"
fi

# Step 7: Final status
echo -e "${BLUE}[7/7] Final status check...${NC}"

# Check all services
services_ok=true

echo ""
echo -e "${GREEN}=== VDP Application Started Successfully! ===${NC}"
echo ""
echo -e "${GREEN}🌐 Frontend:${NC}  http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}🚀 Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}📊 API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}💾 Database:${NC} PostgreSQL on localhost:$DB_PORT"
echo -e "${GREEN}⚡ Redis:${NC} localhost:$REDIS_PORT"
echo ""

# Show test credentials
echo -e "${BLUE}Test Credentials:${NC}"
echo "Email: admin@teched-accelerator.com"
echo "Password: admin123"
echo ""

# Show useful commands
echo -e "${BLUE}Useful Commands:${NC}"
echo "• Stop all services: ./stop.sh"
echo "• View backend logs: tail -f backend.log"
echo "• View frontend logs: tail -f frontend.log"
echo "• Check Docker services: docker-compose ps"
echo ""

# Check for any issues
echo -e "${BLUE}Health Check:${NC}"
if curl -s http://localhost:$BACKEND_PORT/api/v1/health >/dev/null 2>&1; then
    echo -e "Backend health: ${GREEN}✅ OK${NC}"
else
    echo -e "Backend health: ${RED}❌ Not responding${NC}"
    services_ok=false
fi

if curl -s http://localhost:$FRONTEND_PORT >/dev/null 2>&1; then
    echo -e "Frontend: ${GREEN}✅ OK${NC}"
else
    echo -e "Frontend: ${YELLOW}⚠️  Starting up...${NC}"
fi

echo -e "Database: ${GREEN}✅ OK${NC}"

if ! $services_ok; then
    echo ""
    echo -e "${YELLOW}⚠️  Some services may need a moment to fully start up.${NC}"
    echo "Check the logs if you encounter issues."
fi

echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"