#!/bin/bash
"""
Development startup script for Reddit Content Platform
"""

echo "🚀 Starting Reddit Content Platform Development Server..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Check if dependencies are installed
if [ ! -f ".venv/lib/python3.12/site-packages/fastapi/__init__.py" ]; then
    echo "📦 Installing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi

# Set environment variables
export PYTHONPATH=.

# Start the development server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation available at http://localhost:8000/docs"
echo "🔍 Health check at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload