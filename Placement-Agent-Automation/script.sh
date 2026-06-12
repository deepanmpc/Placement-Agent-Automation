#!/bin/bash

echo "Starting Backend API on port 8000..."
cd backend
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

echo "Starting Frontend on port 5173..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "================================================="
echo "Application started!"
echo "Frontend URL: http://localhost:5173"
echo "Backend API:  http://localhost:8000"
echo "================================================="
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C (SIGINT) to kill background processes
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT

# Wait for background processes to keep script running
wait
