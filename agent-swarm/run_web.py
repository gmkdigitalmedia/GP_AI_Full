#!/usr/bin/env python3
"""
GP Swarm Web Launcher

Easy launcher script for the GP Swarm web interface.
Run this to start the web visualization of AI agent swarms.
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the GP Swarm web interface."""

    # Check if we're in the right directory
    current_dir = Path.cwd()
    web_dir = current_dir / 'web'

    if not web_dir.exists():
        print("Error: 'web' directory not found!")
        print("Please run this script from the agent-swarm directory")
        return 1

    # Check if .env exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        print("Warning: .env file not found!")
        print("Please create a .env file with your OPENAI_API_KEY")
        print("Example: OPENAI_API_KEY=your_key_here")
        print()

    # Check if configs directory exists
    configs_dir = current_dir / 'configs'
    if not configs_dir.exists():
        print("Warning: 'configs' directory not found!")
        print("Agent configuration files are missing")
        return 1

    # Add web directory to Python path
    sys.path.insert(0, str(web_dir))

    # Change to web directory
    os.chdir(web_dir)

    try:
        # Import and run the web app
        from app import GPSwarmWeb

        print("="*60)
        print("🤖 GP SWARM - AI Agent Visualization")
        print("="*60)
        print()
        print("Starting web interface...")
        print("Open your browser to: http://localhost:5000")
        print()
        print("Features:")
        print("• Real-time agent workflow visualization")
        print("• Interactive task control panel")
        print("• Live agent status monitoring")
        print("• Task history and results")
        print()
        print("Press Ctrl+C to stop the server")
        print("="*60)
        print()

        # Create and run the web app
        app = GPSwarmWeb()
        app.run(host='0.0.0.0', port=5000, debug=False)

    except ImportError as e:
        print(f"Error importing web app: {e}")
        print("Please install required dependencies:")
        print("pip install flask flask-socketio eventlet")
        return 1
    except KeyboardInterrupt:
        print("\n\nShutting down GP Swarm...")
        return 0
    except Exception as e:
        print(f"Error starting web app: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())