"""
Core data structures and utilities for MindMate AI
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from .config import setup_logging, POINTS

# Setup logging
logger = setup_logging()

# Global metrics storage
metrics = defaultdict(int)
latencies = defaultdict(list)

# Global user storage
user_journeys: Dict[str, 'UserJourney'] = {}
conversation_contexts: Dict[str, 'ConversationContext'] = {}


@dataclass
class UserJourney:
    """Tracks user's complete journey through MindMate."""
    user_id: str
    name: str
    created_at: float = field(default_factory=time.time)
    emotion_history: List[Dict] = field(default_factory=list)
    stress_history: List[int] = field(default_factory=list)
    streaks: Dict[str, int] = field(default_factory=lambda: {
        "nutrition": 0, "tasks": 0, "games": 0, 
        "meditation": 0, "communication": 0
    })
    badges: List[str] = field(default_factory=list)
    total_points: int = 0
    last_interaction: float = 0.0
    game_scores: Dict = field(default_factory=dict)
    communication_history: List[Dict] = field(default_factory=list)
    meal_preferences: Dict = field(default_factory=dict)


@dataclass  
class ConversationContext:
    """Tracks conversation context."""
    user_id: str
    session_id: str
    history: List[Dict] = field(default_factory=list)
    emotional_state: Dict = field(default_factory=dict)
    recent_topics: List[str] = field(default_factory=list)
    last_agent: str = ""


def get_user(user_id: str, name: str = "Friend") -> UserJourney:
    """Get or create user journey."""
    if user_id not in user_journeys:
        user_journeys[user_id] = UserJourney(user_id=user_id, name=name)
        metric_inc("new_users")
        logger.info(f"New user created: {user_id}")
    return user_journeys[user_id]


def get_context(user_id: str, session_id: str = "default") -> ConversationContext:
    """Get or create conversation context."""
    key = f"{user_id}_{session_id}"
    if key not in conversation_contexts:
        conversation_contexts[key] = ConversationContext(user_id=user_id, session_id=session_id)
    return conversation_contexts[key]


def get_greeting(user_id: str) -> str:
    """Generate personalized greeting."""
    user = get_user(user_id)
    hour = datetime.now().hour
    
    if hour < 12:
        time_greet = "Good morning"
    elif hour < 17:
        time_greet = "Good afternoon"
    else:
        time_greet = "Good evening"
    
    # Check if returning user
    if user.last_interaction > 0:
        time_since = time.time() - user.last_interaction
        if time_since > 86400:  # More than a day
            greeting = f"{time_greet}, {user.name}! Welcome back 💙"
        else:
            greeting = f"{time_greet}, {user.name}!"
    else:
        greeting = f"{time_greet}, {user.name}! I'm MindMate, your wellness companion 💙"
    
    user.last_interaction = time.time()
    return greeting


def metric_inc(name: str, amt: int = 1):
    """Increment a metric counter."""
    metrics[name] += amt


def metric_time(name: str, duration: float):
    """Record a latency measurement."""
    latencies[name].append(duration)


def safe_file_read(file_path: str, expected_extensions: list = None) -> Dict:
    """
    Safely validate and read file with comprehensive error handling.
    
    Returns: {"status": "success/error", "path": str, "error": str}
    """
    import os
    
    try:
        # Check if path exists
        if not file_path or not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}",
                "path": None
            }
        
        # Check if it's a file
        if not os.path.isfile(file_path):
            return {
                "status": "error", 
                "error": f"Path is not a file: {file_path}",
                "path": None
            }
        
        # Check extension if specified
        if expected_extensions:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in expected_extensions:
                return {
                    "status": "error",
                    "error": f"Invalid file type {ext}. Expected: {expected_extensions}",
                    "path": None
                }
        
        # Check file size (limit to 50MB)
        size = os.path.getsize(file_path)
        if size > 50 * 1024 * 1024:
            return {
                "status": "error",
                "error": f"File too large: {size / (1024*1024):.1f}MB (max 50MB)",
                "path": None
            }
        
        if size == 0:
            return {
                "status": "error",
                "error": "File is empty",
                "path": None
            }
        
        return {"status": "success", "path": file_path, "error": None}
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"File validation error: {str(e)}",
            "path": None
        }


def get_system_status() -> Dict:
    """Get complete system status."""
    return {
        "status": "🟢 OPERATIONAL",
        "version": "1.0.0",
        "agents": {
            "1": "Mood Agent - Emotional support",
            "2": "Stress Buster - Fun games",
            "3": "Interpersonal Coach - Text + Audio analysis",
            "4": "Meal Planner - Recipes + Image detection",
            "5": "Task Planner - Organization",
            "6": "Nutrition Advisor - Dietary guidance",
            "7": "Summarizer - Text/URL/PDF only"
        },
        "features": {
            "mood_tracking": "✅ Emotion history & trends",
            "stress_relief": "✅ Immediate game triggers",
            "communication_coaching": "✅ Text + Audio file analysis",
            "meal_planning": "✅ Text ingredients + Image detection",
            "task_management": "✅ Priority & time estimates",
            "nutrition_guidance": "✅ Goal-based advice",
            "content_summarization": "✅ Text, URL, PDF"
        },
        "metrics": {
            "total_users": len(user_journeys),
            "total_requests": metrics.get("total_requests", 0),
            "mood_analyses": metrics.get("mood_analyses", 0),
            "games_played": metrics.get("games_played", 0),
            "communication_analyses": metrics.get("communication_analyses", 0),
            "meal_plans": metrics.get("meal_plans", 0),
            "tasks_planned": metrics.get("tasks_planned", 0),
            "nutrition_advice": metrics.get("nutrition_advice", 0),
            "summaries": metrics.get("summaries", 0)
        },
        "gamification": {
            "total_points_awarded": sum(u.total_points for u in user_journeys.values()),
            "total_badges": sum(len(u.badges) for u in user_journeys.values())
        }
    }
