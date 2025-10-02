#!/bin/bash
echo "Starting Neo Recovery Local Development Environment..."
echo ""
echo "This will start both the web server and the secure backend server."
echo ""
echo "Web Server: http://localhost:8080"
echo "Backend Server: http://localhost:8081"
echo ""
echo "Your apps are available at:"
echo "  - Kiosk: http://localhost:8080/index-backend.html"
echo "  - Admin: http://localhost:8080/admin-backend.html"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $WEB_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the web server in background
python3 server.py &
WEB_PID=$!

# Start the backend server in background
python3 backend.py &
BACKEND_PID=$!

echo "Servers started successfully!"
echo "Web server PID: $WEB_PID"
echo "Backend server PID: $BACKEND_PID"
echo ""

# Wait for user to stop
wait
