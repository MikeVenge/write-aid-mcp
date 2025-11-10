#!/bin/bash
# Start script for AI Checker with Backend

echo "=========================================="
echo "AI Checker - Starting Backend & Frontend"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠ Flask not found. Installing dependencies..."
    pip3 install flask flask-cors requests
fi

# Start backend server in background
echo "🚀 Starting backend server on port 5001..."
python3 backend_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Check if backend is running
if curl -s http://localhost:5001/health > /dev/null; then
    echo "✓ Backend server is running"
else
    echo "⚠ Backend server may not be ready yet"
fi

# Start frontend server
echo "🚀 Starting frontend server on port 8000..."
cd "$(dirname "$0")"
python3 -m http.server 8000 &
FRONTEND_PID=$!

sleep 1

# Open browser
echo "🌐 Opening browser..."
open http://localhost:8000/ai_checker.html

echo ""
echo "=========================================="
echo "Servers are running:"
echo "  Backend:  http://localhost:5001"
echo "  Frontend: http://localhost:8000/ai_checker.html"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=========================================="

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait


