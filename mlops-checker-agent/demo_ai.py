#!/usr/bin/env python3
"""
Demo script showing AI agent capabilities
Run this to see how the AI agent works (requires OpenAI API key)
"""

from agents.mlops_checker import MLOpsChecker
import os

def demo_ai_agent():
    print("🤖 MLOps Checking Agent - AI Demo")
    print("=" * 50)

    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in environment.")
        print("Set OPENAI_API_KEY environment variable to test AI features.")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return

    directory_path = "../toyota_interview"

    if not os.path.exists(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return

    print(f"🔍 Analyzing: {directory_path}")
    print("🤖 Running AI-powered analysis...")
    print("⏳ This may take 10-30 seconds...\n")

    try:
        # Create AI-enabled checker
        checker = MLOpsChecker(directory_path, use_ai=True)
        results = checker.run_checks(["all"])

        print("📊 RESULTS:")
        print(f"🎯 Deployment Readiness: {results['deployment_readiness']}/100")
        print(f"⚠️  Issues Found: {len(results['issues'])}")

        # Show regular issues
        if results['issues']:
            print(f"\n🔍 Issues:")
            for issue in results['issues']:
                print(f"  • [{issue['category'].upper()}] {issue['message']}")

        # Show AI insights
        if results.get('ai_insights'):
            print(f"\n🤖 AI INSIGHTS:")
            for insight in results['ai_insights']:
                print(f"  {insight}\n")

        # Show AI fix plan
        if results.get('fix_plan'):
            print(f"🛠️ AI-GENERATED FIX PLAN:")
            for step in results['fix_plan']:
                priority = step.get('priority', 'unknown')
                action = step.get('action', 'Unknown action')
                print(f"  {step.get('step', '?')}. [{priority.upper()}] {action}")
                if step.get('estimated_minutes'):
                    print(f"     ⏱️  Estimated time: {step['estimated_minutes']} minutes")
                print()

        print("✅ AI Analysis Complete!")

    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        print("Make sure your OpenAI API key is valid and has credits.")

if __name__ == "__main__":
    demo_ai_agent()