#!/bin/bash
# Restart script for the binding application

echo "Stopping existing app..."
pkill -f "uvicorn app.main:app" || echo "No running app found"

echo "Waiting for processes to stop..."
sleep 2

echo "Starting app..."
./start.sh
