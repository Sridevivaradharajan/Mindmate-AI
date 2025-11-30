"""User data model and management."""

from dataclasses import dataclass, field
from typing import List, Dict
import time


@dataclass
class UserJourney:
    """Tracks individual user's wellness journey."""
    user_id: str
    name: str
    total_points: int = 0
    level: int = 1
    badges: List[str] = field(default_factory=list)
    streaks: Dict[str, int] = field(default_factory=dict)
    emotion_history: List[Dict] = field(default_factory=list)
    stress_history: List[int] = field(default_factory=list)
    communication_history: List[Dict] = field(default_factory=list)
    game_scores: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)


# Global user storage
user_journeys: Dict[str, UserJourney] = {}


def get_user(user_id: str) -> UserJourney:
    """Get or create user profile."""
    if user_id not in user_journeys:
        user_journeys[user_id] = UserJourney(
            user_id=user_id,
            name=user_id.split('_')[0].title() if '_' in user_id else user_id.title()
        )
    
    user = user_journeys[user_id]
    user.last_active = time.time()
    
    # Level up logic
    if user.total_points >= 100 and user.level == 1:
        user.level = 2
    elif user.total_points >= 300 and user.level == 2:
        user.level = 3
    
    return user


def get_greeting(user_id: str) -> str:
    """Get personalized greeting based on time and user history."""
    user = get_user(user_id)
    hour = int(time.strftime("%H"))
    
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    return f"{time_greeting}, {user.name}!"


def get_user_stats(user_id: str) -> Dict:
    """Get comprehensive user statistics."""
    user = get_user(user_id)
    
    return {
        "user_id": user.user_id,
        "name": user.name,
        "level": user.level,
        "total_points": user.total_points,
        "badges": user.badges,
        "streaks": user.streaks,
        "total_moods_tracked": len(user.emotion_history),
        "total_games_played": user.game_scores.get("total_played", 0),
        "member_since": time.strftime("%Y-%m-%d", time.localtime(user.created_at))
    }
