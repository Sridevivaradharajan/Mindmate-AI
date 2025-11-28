"""
Core data structures and user management for Mindmate AI.

This module defines user journeys, conversation contexts, and global state management.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

from .config import logger


# ============================================================================
# METRICS TRACKING
# ============================================================================

metrics = defaultdict(int)
latencies = defaultdict(list)


def metric_inc(name: str, amt: int = 1):
    """Increment a metric counter."""
    metrics[name] += amt


def metric_time(name: str, duration: float):
    """Record latency for an operation."""
    latencies[name].append(duration)


# ============================================================================
# USER DATA STRUCTURES
# ============================================================================

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
    """Tracks conversation context for multi-turn dialogues."""
    user_id: str
    session_id: str
    history: List[Dict] = field(default_factory=list)
    emotional_state: Dict = field(default_factory=dict)
    recent_topics: List[str] = field(default_factory=list)
    last_agent: str = ""


# ============================================================================
# GLOBAL STATE MANAGEMENT
# ============================================================================

# In-memory stores (could be replaced with database in production)
user_journeys: Dict[str, UserJourney] = {}
conversation_contexts: Dict[str, ConversationContext] = {}


def get_user(user_id: str, name: str = "Friend") -> UserJourney:
    """
    Get or create user journey.
    
    Args:
        user_id: Unique user identifier
        name: User's display name
        
    Returns:
        UserJourney: User's journey object
    """
    if user_id not in user_journeys:
        user_journeys[user_id] = UserJourney(user_id=user_id, name=name)
        metric_inc("new_users")
        logger.info(f"New user created: {user_id}")
    return user_journeys[user_id]


def get_context(user_id: str, session_id: str = "default") -> ConversationContext:
    """
    Get or create conversation context.
    
    Args:
        user_id: Unique user identifier
        session_id: Session identifier
        
    Returns:
        ConversationContext: Conversation context object
    """
    key = f"{user_id}_{session_id}"
    if key not in conversation_contexts:
        conversation_contexts[key] = ConversationContext(
            user_id=user_id, 
            session_id=session_id
        )
    return conversation_contexts[key]


def get_greeting(user_id: str) -> str:
    """
    Generate personalized greeting based on time and user history.
    
    Args:
        user_id: Unique user identifier
        
    Returns:
        str: Personalized greeting message
    """
    user = get_user(user_id)
    hour = datetime.now().hour
    
    # Time-based greeting
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


def get_system_status() -> Dict:
    """
    Get complete system status and metrics.
    
    Returns:
        dict: System status including metrics and user stats
    """
    return {
        "status": "operational",
        "version": "1.0",
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
