#!/usr/bin/env python3
"""
Quick test script for the MLOps Checker Agent
"""

import requests
import json
import os

def test_checker():
    # Test the toyota_interview directory
    toyota_path = os.path.abspath("../toyota_interview")

    payload = {
        "directory_path": toyota_path,
        "checks": ["all"]
    }

    try:
        response = requests.post("http://localhost:8000/check", json=payload)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Check completed for: {result['directory']}")
            print(f"🎯 Deployment Readiness Score: {result['deployment_readiness']}/100")
            print(f"⚠️  Found {len(result['issues'])} issues")
            print(f"💡 {len(result['recommendations'])} recommendations")

            print("\n🔍 Issues found:")
            for issue in result['issues']:
                severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
                print(f"  {severity_emoji.get(issue['severity'], '⚪')} [{issue['category'].upper()}] {issue['message']}")
                if issue['file_path']:
                    location = f"{issue['file_path']}"
                    if issue['line_number']:
                        location += f":{issue['line_number']}"
                    print(f"    📍 {location}")

            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")

        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the MLOps Checker Agent")
        print("Make sure the server is running with: python main.py")

if __name__ == "__main__":
    test_checker()