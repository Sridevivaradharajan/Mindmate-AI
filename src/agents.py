"""
MindMate AI - Agent Functions
All 7 specialized wellness agents
"""

import time
import re
import random
import traceback
from typing import Dict, Optional

from .core import (
    get_user, metric_inc, metric_time, safe_file_read, logger,
    user_journeys
)
from .config import POINTS, BADGES, SUPPORTED_AUDIO_FORMATS


# ============================================================================
# AGENT 1: MOOD AGENT
# ============================================================================

def analyze_mood(user_id: str, message: str, stress_level: int = 5) -> Dict:
    """
    Analyze user's emotional state and provide personalized support.
    
    Parameters:
    - user_id: User identifier
    - message: User's message expressing how they feel
    - stress_level: Self-reported stress (1-10)
    
    Returns: Mood analysis with coping strategies
    """
    start = time.time()
    user = get_user(user_id)
    lower = message.lower()
    
    # Emotion detection
    emotion_map = {
        "distressed": (2, ["depressed", "hopeless", "terrible", "suicidal", "can't go on"]),
        "anxious": (3, ["anxious", "stressed", "worried", "overwhelmed", "panic"]),
        "sad": (4, ["sad", "down", "lonely", "upset", "disappointed"]),
        "neutral": (5, ["okay", "meh", "alright", "so-so"]),
        "stable": (6, ["fine", "decent", "not bad"]),
        "positive": (7, ["good", "better", "nice", "pleased"]),
        "very_positive": (8, ["great", "happy", "amazing", "wonderful", "fantastic"]),
        "excellent": (9, ["excellent", "thrilled", "ecstatic", "best"])
    }
    
    score = 5
    emotion = "neutral"
    
    for emo, (emo_score, keywords) in emotion_map.items():
        if any(w in lower for w in keywords):
            score = emo_score
            emotion = emo
            break
    
    # Adjust for stress level
    score = max(1, min(10, score - (stress_level - 5) // 2))
    
    # Update user history
    user.emotion_history.append({
        "timestamp": time.time(),
        "emotion": emotion,
        "score": score,
        "stress": stress_level
    })
    user.stress_history.append(stress_level)
    
    # Keep last 20 entries
    if len(user.emotion_history) > 20:
        user.emotion_history = user.emotion_history[-20:]
    if len(user.stress_history) > 20:
        user.stress_history = user.stress_history[-20:]
    
    # Generate coping strategy based on score
    if score <= 2:
        coping = f"💙 {user.name}, I hear you're going through a really tough time. Please remember you're not alone. Consider reaching out to a mental health professional or crisis line. Would you like some grounding exercises?"
        assessment = "needs_immediate_support"
    elif score <= 4:
        coping = f"💙 {user.name}, try this: 4-7-8 breathing - inhale 4 seconds, hold 7, exhale 8. Repeat 4 times. Would you like a stress relief game?"
        assessment = "needs_support"
    elif score <= 6:
        coping = f"{user.name}, you're managing okay. A short walk or talking to someone you trust might help lift your mood."
        assessment = "stable"
    else:
        coping = f"Wonderful, {user.name}! Keep doing what's working for you. Gratitude journaling can help maintain this positive state."
        assessment = "thriving"
    
    # Calculate trend
    if len(user.emotion_history) >= 3:
        recent_scores = [e["score"] for e in user.emotion_history[-3:]]
        if recent_scores[-1] > recent_scores[0]:
            trend = "improving 📈"
        elif recent_scores[-1] < recent_scores[0]:
            trend = "declining 📉"
        else:
            trend = "stable ➡️"
    else:
        trend = "not enough data"
    
    # Award points
    user.total_points += POINTS["mood_check"]
    metric_inc("mood_analyses")
    metric_time("mood_agent", time.time() - start)
    
    return {
        "mood_score": score,
        "emotion": emotion,
        "stress_level": stress_level,
        "assessment": assessment,
        "coping_strategy": coping,
        "trend": trend,
        "points_earned": POINTS["mood_check"],
        "total_points": user.total_points
    }


# ============================================================================
# AGENT 2: STRESS BUSTER (GAMES)
# ============================================================================

def play_stress_game(user_id: str, game_type: str = "random") -> Dict:
    """
    Provide fun mental break games for stress relief.
    
    Parameters:
    - user_id: User identifier
    - game_type: "riddle", "trivia", "brain_teaser", "pattern", "detective", "random"
    
    Returns: Game content with question and answer
    """
    start = time.time()
    user = get_user(user_id)
    
    games = {
        "riddle": [
            {"q": f"🤔 {user.name}, I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "a": "An ECHO! 🔊"},
            {"q": f"🤔 {user.name}, what has keys but no locks, space but no room, and you can enter but can't go inside?", "a": "A KEYBOARD! ⌨️"},
            {"q": "🤔 The more you take, the more you leave behind. What am I?", "a": "FOOTSTEPS! 👣"},
        ],
        "trivia": [
            {"q": "🎬 In Stranger Things, what tabletop game do the kids play?", "opts": ["A) Monopoly", "B) Dungeons & Dragons", "C) Risk"], "a": "B) Dungeons & Dragons ✅", "fact": "The Duffer Brothers are huge D&D fans!"},
        ],
        "brain_teaser": [
            {"q": f"🧠 {user.name}, a bus driver goes the wrong way down a one-way street, passes 10 police officers, but doesn't get a ticket. Why?", "a": "He was WALKING! 🚶"},
        ],
        "pattern": [
            {"q": "🔢 What comes next? 2, 4, 8, 16, ?", "a": "32 (each number doubles)"},
        ],
        "detective": [
            {"q": f"🔍 {user.name}, a man is found dead in a locked room with only a puddle of water and broken glass. How did he die?", "hint": "Think about what was IN the glass...", "a": "🎯 He was a fish! The glass was his fishbowl that broke!"},
        ]
    }
    
    # Select game type
    if game_type == "random" or game_type not in games:
        recent = user.game_scores.get("recent_types", [])
        available = [t for t in games.keys() if t not in recent[-2:]]
        game_type = random.choice(available if available else list(games.keys()))
    
    selected = random.choice(games[game_type])
    
    # Build response
    result = {
        "game_type": game_type,
        "question": selected["q"],
        "answer": selected["a"],
        "hint": selected.get("hint"),
        "options": selected.get("opts", []),
        "fun_fact": selected.get("fact"),
    }
    
    # Update user stats
    user.streaks["games"] = user.streaks.get("games", 0) + 1
    user.total_points += POINTS["game"]
    
    if "recent_types" not in user.game_scores:
        user.game_scores["recent_types"] = []
    user.game_scores["recent_types"].append(game_type)
    
    total_played = user.game_scores.get("total_played", 0) + 1
    user.game_scores["total_played"] = total_played
    
    # Award badges
    for badge_key, badge_info in BADGES.items():
        if "game" in badge_key:
            if total_played == badge_info["threshold"] and badge_info["name"] not in user.badges:
                user.badges.append(f"{badge_info['emoji']} {badge_info['name']}")
                result["new_badge"] = f"{badge_info['emoji']} {badge_info['name']}"
    
    result["stats"] = {
        "streak": user.streaks["games"],
        "total_games": total_played,
        "points_earned": POINTS["game"],
        "total_points": user.total_points
    }
    
    metric_inc("games_played")
    metric_time("stress_buster", time.time() - start)
    
    return result
