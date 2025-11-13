#!/bin/bash

cd /home/tony/Desktop/binding

echo "Starting Sphinx Binding App (Development Mode)"
echo "App will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
