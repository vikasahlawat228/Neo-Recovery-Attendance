#!/usr/bin/env python3
"""
Simple HTTP server for local testing of Neo Recovery Attendance app.
This avoids CORS issues when testing locally.

Usage:
    python3 server.py

Then open: http://localhost:8000
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 8080

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"Starting Neo Recovery Attendance local server...")
    print(f"Serving files from: {script_dir}")
    print(f"Open your browser to: http://localhost:{PORT}")
    print(f"Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Try closing other applications or use a different port.")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
