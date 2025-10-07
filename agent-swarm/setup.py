#!/usr/bin/env python3
"""
Easy Setup Script for GP Agent Swarm
=====================================

This script helps you get started with the Agent Swarm system quickly.
It will install dependencies, verify the configuration, and test the system.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success!")
            return True
        else:
            print(f"❌ {description} - Failed!")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {str(e)}")
        return False

def check_env_file():
    """Check if .env file exists with OpenAI API key."""
    print("🔧 Checking .env file...")
    env_file = Path(".env")

    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False

    with open(env_file, 'r') as f:
        content = f.read()
        if "OPENAI_API_KEY=" in content and "sk-" in content:
            print("✅ .env file found with API key!")
            return True
        else:
            print("❌ .env file exists but no valid OpenAI API key found!")
            print("Please add your OpenAI API key to the .env file:")
            print("OPENAI_API_KEY=your_api_key_here")
            return False

def main():
    """Main setup function."""
    print("🚀 GP Agent Swarm Setup")
    print("=" * 50)

    # Step 1: Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Setup failed at dependency installation!")
        return False

    # Step 2: Check .env file
    if not check_env_file():
        print("❌ Setup failed at .env file check!")
        return False

    # Step 3: Test basic functionality
    test_command = '''python3 -c "
from swarm_orchestrator import SwarmOrchestrator
import asyncio

async def test():
    orchestrator = SwarmOrchestrator()
    await orchestrator.load_agents_from_config('configs')
    print(f'Loaded {len(orchestrator.agents)} agents successfully!')

asyncio.run(test())
"'''

    if not run_command(test_command, "Testing agent loading"):
        print("❌ Setup failed at agent loading test!")
        return False

    # Step 4: Test API connectivity
    api_test_command = '''python3 -c "
from swarm_orchestrator import SwarmOrchestrator
from agent_base import TaskConfig
import asyncio

async def test_api():
    orchestrator = SwarmOrchestrator()
    await orchestrator.load_agents_from_config('configs')

    task = TaskConfig(
        name='Setup Test',
        description='Test OpenAI API connectivity',
        assigned_agents=['content_writer'],
        workflow=[{
            'agent': 'content_writer',
            'description': 'API test',
            'instruction': 'Say hello and confirm the system is working'
        }],
        expected_output='Confirmation message'
    )

    results = await orchestrator.execute_task(task)
    success = all(r.success for r in results.values())
    result_text = 'SUCCESS' if success else 'FAILED'
    print(f'API test: {result_text}')

asyncio.run(test_api())
"'''

    if not run_command(api_test_command, "Testing OpenAI API connectivity"):
        print("❌ Setup failed at API connectivity test!")
        print("Please check your OpenAI API key and internet connection.")
        return False

    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Your Agent Swarm system is ready to use!")
    print("\nNext steps:")
    print("1. Run the demo: python3 demo.py")
    print("2. Start web interface: python3 run_web.py")
    print("3. Check the README.md for more examples")
    print("\nHappy swarming! 🤖✨")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)