"""
MindMate AI - Multi-Agent Wellness Companion
Built with Google Agent Development Kit
"""

__version__ = "1.0.0"
__author__ = "Sridevi"

from .core import UserJourney, ConversationContext, get_user, get_context, get_greeting
from .agents import (
    analyze_mood,
    play_stress_game,
    analyze_interpersonal,
    plan_meals,
    plan_tasks,
    get_nutrition_advice,
    summarize_content
)
from .orchestrator import mindmate_agent, runner, session_service

__all__ = [
    "UserJourney",
    "ConversationContext",
    "get_user",
    "get_context",
    "get_greeting",
    "analyze_mood",
    "play_stress_game",
    "analyze_interpersonal",
    "plan_meals",
    "plan_tasks",
    "get_nutrition_advice",
    "summarize_content",
    "mindmate_agent",
    "runner",
    "session_service"
]
