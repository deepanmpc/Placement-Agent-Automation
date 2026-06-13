#!/bin/bash

# Setup Java 21 for Spring Boot
export JAVA_HOME=$(/usr/libexec/java_home -v 21)

echo "Starting Java Spring Boot Backend on port 9090..."
cd spring-backend
mvn spring-boot:run &
JAVA_BACKEND_PID=$!
cd ..

echo "Starting Python AI API on port 8000..."
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
export PYTHONPATH=.
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload &
PYTHON_BACKEND_PID=$!

echo "Starting Frontend on port 5173..."
cd frontend
npm install
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo "================================================="
echo "Application started!"
echo "Frontend URL:          http://localhost:5173"
echo "Python AI API:         http://localhost:8000"
echo "Java Spring Boot API:  http://localhost:9090"
echo "================================================="
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C (SIGINT) to kill background processes
trap "echo 'Stopping services...'; kill $JAVA_BACKEND_PID $PYTHON_BACKEND_PID $FRONTEND_PID; exit 0" SIGINT

# Wait for background processes to keep script running
wait
