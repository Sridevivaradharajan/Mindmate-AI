"""
MindMate AI - Wellness Companion with 7 Specialized Agents
"""

__version__ = "1.0.0"
__author__ = "Sridevi V"

# Import key components for easy access
from .Orchestrator import mindmate_agent, runner, session_service
from .config import logger
from .user_model import get_user, get_greeting
from .agents import (
    analyze_mood,
    play_stress_game,
    analyze_interpersonal,
    plan_meals,
    plan_tasks,
    get_nutrition_advice,
    summarize_content,
)

__all__ = [
    # Main agent
    "mindmate_agent",
    "runner",
    "session_service",
    
    # Utilities
    "logger",
    "get_user",
    "get_greeting",
    
    # Individual agents
    "analyze_mood",
    "play_stress_game",
    "analyze_interpersonal",
    "plan_meals",
    "plan_tasks",
    "get_nutrition_advice",
    "summarize_content",
]
