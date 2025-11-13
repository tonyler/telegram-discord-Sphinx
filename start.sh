#!/bin/bash
# Start script for the binding application

echo "Starting Web3 Community Binding App..."
echo "=========================================="

# Activate virtual environment
source venv/bin/activate

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
