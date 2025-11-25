"""
Configuration settings for MindMate AI
"""

import os
import logging

# Version
VERSION = "1.0.0"
AUTHOR = "Your Name"

# API Configuration
def get_api_key():
    """Get Google API key from environment or Kaggle secrets."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        try:
            from kaggle_secrets import UserSecretsClient
            api_key = UserSecretsClient().get_secret("GOOGLE_API_KEY")
        except:
            pass
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Please set it as an environment variable:\n"
            "  export GOOGLE_API_KEY='your-key-here'\n"
            "Or add it to Kaggle secrets if running on Kaggle."
        )
    
    return api_key

# Model Configuration
GEMINI_MODEL = "gemini-2.5-flash"
MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.3

# File Limits
MAX_FILE_SIZE_MB = 50
MAX_PDF_PAGES = 50
MAX_AUDIO_DURATION_SECONDS = 300

# Supported File Types
SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac']
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.txt']

# Logging Configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("MindMate")

# Gamification Settings
POINTS = {
    "mood_check": 5,
    "game": 10,
    "communication": 15,
    "meal_plan": 25,
    "task_plan": 15,
    "nutrition": 10,
    "summary": 30
}

BADGES = {
    "game_starter": {"threshold": 5, "emoji": "🎮", "name": "Game Starter"},
    "game_master": {"threshold": 20, "emoji": "🎮🎮", "name": "Game Master"},
    "game_legend": {"threshold": 50, "emoji": "🎮🎮🎮", "name": "Game Legend"},
    "knowledge_seeker": {"threshold": 5, "emoji": "📚", "name": "Knowledge Seeker"},
    "research_master": {"threshold": 20, "emoji": "📚📚", "name": "Research Master"}
}

# Agent Configuration
AGENT_NAME = "mindmate"
APP_NAME = "mindmate"
