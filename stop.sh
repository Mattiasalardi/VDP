#!/bin/bash

# VDP Application Stop Script
# Properly shuts down all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}=== VDP Application Shutdown ===${NC}"
echo "Stopping all services..."
echo ""

# Function to kill process by PID file
kill_by_pidfile() {
    local pidfile=$1
    local service_name=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force stopping $service_name..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        else
            echo "$service_name PID file exists but process not running"
        fi
        rm -f "$pidfile"
    fi
}

# Function to kill processes by port
kill_by_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Killing $service_name processes on port $port..."
        lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -TERM 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "Force killing $service_name processes..."
            lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
        fi
    fi
}

# Check for docker-compose
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE=""
fi

echo -e "${BLUE}[1/4] Stopping Docker services...${NC}"
if [ -n "$DOCKER_COMPOSE" ]; then
    $DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true
    echo -e "${GREEN}✅ Docker services stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Docker Compose not available, skipping Docker services${NC}"
fi

echo -e "${BLUE}[2/4] Stopping backend server...${NC}"
kill_by_pidfile "backend.pid" "backend"
kill_by_port $BACKEND_PORT "backend"
echo -e "${GREEN}✅ Backend stopped${NC}"

echo -e "${BLUE}[3/4] Stopping frontend server...${NC}"
kill_by_pidfile "frontend.pid" "frontend"
kill_by_port $FRONTEND_PORT "frontend"
echo -e "${GREEN}✅ Frontend stopped${NC}"

echo -e "${BLUE}[4/4] Cleaning up...${NC}"

# Clean up log files if they exist
if [ -f "backend.log" ]; then
    echo "Archiving backend.log..."
    mv backend.log "backend.log.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
fi

if [ -f "frontend.log" ]; then
    echo "Archiving frontend.log..."
    mv frontend.log "frontend.log.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
fi

# Remove any remaining PID files
rm -f backend.pid frontend.pid

echo -e "${GREEN}✅ Cleanup complete${NC}"

echo ""
echo -e "${GREEN}=== All Services Stopped ===${NC}"
echo ""

# Final verification
echo -e "${BLUE}Verification:${NC}"
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "Backend port $BACKEND_PORT: ${YELLOW}⚠️  Still in use${NC}"
else
    echo -e "Backend port $BACKEND_PORT: ${GREEN}✅ Free${NC}"
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "Frontend port $FRONTEND_PORT: ${YELLOW}⚠️  Still in use${NC}"
else
    echo -e "Frontend port $FRONTEND_PORT: ${GREEN}✅ Free${NC}"
fi

echo ""
echo "To start services again, run: ./start.sh"