"""
Mindmate AI - Personal Wellness Companion

A multi-agent AI system for emotional support, stress relief, communication coaching,
meal planning, task management, nutrition advice, and content summarization.

Author: Sridevi V
Version: 1.0
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Import main components for easy access
from .config import logger, settings, GOOGLE_API_KEY
from .core import (
    UserJourney,
    ConversationContext,
    get_user,
    get_context,
    get_greeting,
    get_system_status,
)
from .utils import safe_file_read, safe_tool_wrapper

__all__ = [
    # Config
    "logger",
    "settings",
    "GOOGLE_API_KEY",
    
    # Core
    "UserJourney",
    "ConversationContext",
    "get_user",
    "get_context",
    "get_greeting",
    "get_system_status",
    
    # Utils
    "safe_file_read",
    "safe_tool_wrapper",
]
