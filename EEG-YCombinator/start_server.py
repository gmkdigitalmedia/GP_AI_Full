#!/usr/bin/env python3
"""
Simple server starter with better error handling
"""
import sys
import traceback

def start_server():
    try:
        print("Loading dependencies...")
        import uvicorn
        import socket
        from main import app
        
        print("Dependencies loaded successfully")
        
        # Find an available port
        def find_free_port():
            for port in range(8000, 8010):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return port
                except OSError:
                    continue
            return 8000  # fallback
        
        port = find_free_port()
        print(f"Starting server on http://localhost:{port}")
        print(f"API documentation available at: http://localhost:{port}/docs")
        
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Try: pip3 install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_server()