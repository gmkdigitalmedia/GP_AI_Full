#!/bin/bash

echo "Neural Monitoring System - Quick Demo Setup"
echo "=========================================="

# Update dependencies to resolve conflicts
echo "Installing/updating dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Starting API server..."
echo "Note: Server will auto-select an available port (8000-8009)"

# Start server in background
python3 main.py &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 3

# Run the demo
echo ""
echo "Running client demonstration..."
python3 client_demo.py

echo ""
echo "Demo completed! Server is still running."
echo "You can:"
echo "1. Run integration tests: python3 test_integration.py"
echo "2. View API docs at the URL shown above"
echo "3. Kill server with: kill $SERVER_PID"
echo ""
echo "Server PID: $SERVER_PID"