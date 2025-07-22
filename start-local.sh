#!/bin/bash

# Quick Local Startup (No Docker)
# Based on working solution from 2025-07-22

set -e

echo "🚀 Starting VDP Local Development (No Docker)"

# Check PostgreSQL
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL is not running. Start it first."
    exit 1
fi

# Start backend
echo "Starting backend..."
cd backend
source .venv/bin/activate
nohup python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
echo $! > ../backend.pid
cd ..

# Wait for backend
sleep 3
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Backend running: http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend  
echo "Starting frontend..."
cd frontend/frontend/frontend
nohup npm run dev > ../../../frontend.log 2>&1 &
echo $! > ../../../frontend.pid
cd ../../..

# Check frontend port
sleep 5
FRONTEND_PORT=3000
if grep -q "Port 3000 is in use" frontend.log 2>/dev/null; then
    FRONTEND_PORT=3001
fi

echo ""
echo "🎉 VDP Application Started!"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Backend:  http://localhost:8000" 
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Login: admin@teched-accelerator.com / admin123"
echo "Stop:  ./stop.sh"