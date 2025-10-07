#!/usr/bin/env python3
"""
Simple CLI for MLOps Checker Agent
Usage: python3 cli.py /path/to/your/project
"""

import sys
import os
from pathlib import Path
from agents.mlops_checker import MLOpsChecker

def print_banner():
    print(" MLOps Checking Agent")
    print("=" * 50)

def print_results(results):
    print(f" Directory: {results['directory']}")
    print(f" Deployment Readiness: {results['deployment_readiness']}/100")
    print(f"  Issues Found: {len(results['issues'])}")

    if results['issues']:
        print(f"\n Issues Details:")
        severity_colors = {"critical": "🔴", "warning": "🟡", "info": "🔵"}

        for issue in results['issues']:
            emoji = severity_colors.get(issue['severity'], '⚪')
            print(f"  {emoji} [{issue['category'].upper()}] {issue['message']}")
            if issue['file_path']:
                location = issue['file_path']
                if issue['line_number']:
                    location += f":{issue['line_number']}"
                print(f"    📍 {location}")

    if results['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")

    # Display AI insights if available
    if results.get('ai_insights'):
        print(f"\n🤖 AI Insights:")
        for insight in results['ai_insights']:
            print(f"  {insight}")

    # Display AI fix plan if available
    if results.get('fix_plan'):
        print(f"\n🛠️ AI-Generated Fix Plan:")
        for step in results['fix_plan']:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(step.get('priority', 'low'), '⚪')
            print(f"  {priority_emoji} Step {step.get('step', '?')}: {step.get('action', 'Unknown action')}")
            if step.get('files_affected'):
                print(f"    📁 Files: {', '.join(step['files_affected'])}")
            if step.get('estimated_minutes'):
                print(f"    ⏱️ Estimated time: {step['estimated_minutes']} minutes")

    print(f"\n{'✅ Ready to deploy!' if results['deployment_readiness'] >= 80 else '⚠️  Needs attention before deployment'}")

def main():
    print_banner()

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 cli.py <directory_path> [--ai]")
        print("Example: python3 cli.py ../toyota_interview")
        print("Example: python3 cli.py ../toyota_interview --ai  # Enable AI analysis")
        sys.exit(1)

    directory_path = sys.argv[1]
    use_ai = len(sys.argv) == 3 and sys.argv[2] == "--ai"

    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        sys.exit(1)

    print(f"🔍 Analyzing: {directory_path}")
    if use_ai:
        print("🤖 AI analysis enabled")
    print("⏳ Running checks...")

    try:
        checker = MLOpsChecker(directory_path, use_ai=use_ai)
        results = checker.run_checks(["all"])
        print()
        print_results(results)

    except Exception as e:
        print(f"❌ Check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()