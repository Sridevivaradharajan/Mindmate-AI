#!/usr/bin/env python3
"""
MindMate AI - Command Line Interface
Main entry point for running the agent
"""

import asyncio
import argparse
import sys

from src.config import get_api_key, setup_logging
from src.core import get_user, get_system_status
from src.orchestrator import mindmate_agent, runner, session_service
from src.agents import (
    analyze_mood, play_stress_game, analyze_interpersonal,
    plan_meals, plan_tasks, get_nutrition_advice, summarize_content
)

# Setup
logger = setup_logging()

# Configure API
try:
    import os
    import google.generativeai as genai
    
    api_key = get_api_key()
    os.environ["GOOGLE_API_KEY"] = api_key
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
    genai.configure(api_key=api_key)
    logger.info("✅ API configured")
except Exception as e:
    logger.error(f"❌ API configuration failed: {e}")
    sys.exit(1)


async def chat(message: str, user_name: str = "Friend"):
    """Interactive chat with MindMate."""
    user_id = f"cli_{user_name.lower().replace(' ', '_')}"
    user = get_user(user_id, user_name)
    
    print(f"\n💙 MindMate: Hello, {user_name}!")
    print(f"📝 You: {message}\n")
    
    # Create session
    session = await session_service.create_session(app_name="mindmate", user_id=user_id)
    
    # Run agent
    response = await runner.run(user_id=user_id, session_id=session.id, new_message=message)
    
    # Extract response
    if hasattr(response, 'content'):
        result = response.content
    elif isinstance(response, list) and response:
        result = response[-1]
    else:
        result = str(response)
    
    print(f"🤖 MindMate: {result}\n")
    print(f"{'─'*50}")
    print(f"📊 Stats: {user.total_points} points | {len(user.badges)} badges")
    if user.badges:
        print(f"🏆 Badges: {', '.join(user.badges[-3:])}")
    print()


async def run_tests():
    """Run comprehensive tests."""
    print("\n" + "="*70)
    print("🧪 RUNNING TESTS")
    print("="*70)
    
    tests = [
        ("Mood", "I'm feeling stressed about work", analyze_mood, ["test_user", "I'm feeling stressed", 7]),
        ("Game", "Random game", play_stress_game, ["test_user"]),
        ("Task", "Tasks: call client, finish report", plan_tasks, ["test_user", "call client, finish report"]),
    ]
    
    for name, desc, func, args in tests:
        print(f"\n[TEST] {name}: {desc}")
        try:
            result = func(*args)
            print(f"  ✅ PASS - Status: {result.get('status', 'N/A')}")
        except Exception as e:
            print(f"  ❌ FAIL - {e}")
    
    print("\n" + "="*70)


def show_status():
    """Display system status."""
    status = get_system_status()
    
    print("\n" + "="*70)
    print("📊 MINDMATE AI - SYSTEM STATUS")
    print("="*70)
    print(f"\n{status['status']} Version: {status['version']}")
    print(f"👥 Total Users: {status['metrics']['total_users']}")
    
    print(f"\n🤖 AGENTS ({len(status['agents'])}):")
    for num, desc in status['agents'].items():
        print(f"   {num}. {desc}")
    
    print(f"\n📈 METRICS:")
    for metric, count in status['metrics'].items():
        if metric != 'total_users' and count > 0:
            print(f"   {metric.replace('_', ' ').title()}: {count}")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='MindMate AI - Your wellness companion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mindmate_ai.py --chat "I need a break"
  python mindmate_ai.py --test
  python mindmate_ai.py --status
        """
    )
    
    parser.add_argument('--chat', type=str, help='Chat message to send')
    parser.add_argument('--name', type=str, default='Friend', help='Your name')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.test:
        asyncio.run(run_tests())
    elif args.chat:
        asyncio.run(chat(args.chat, args.name))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
