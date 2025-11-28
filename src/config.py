"""
Configuration management for Mindmate AI.

This module handles API keys, logging, and global settings.
"""

import os
import logging
from typing import Optional

# ============================================================================
# API CONFIGURATION
# ============================================================================

def get_api_key() -> str:
    """
    Get Google API key from environment variable.
    
    Returns:
        str: Google API key
        
    Raises:
        ValueError: If API key is not set
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set. "
            "Get your key from: https://aistudio.google.com/apikey"
        )
    return api_key


# Set API key for Google Generative AI
GOOGLE_API_KEY = get_api_key()
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for Mindmate AI.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("Mindmate")


# Global logger instance
logger = setup_logging()


# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

class Settings:
    """Global application settings."""
    
    # Model configuration
    MODEL_NAME = "gemini-2.5-flash"
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7
    
    # File upload limits
    MAX_FILE_SIZE_MB = 50
    MAX_AUDIO_DURATION_SEC = 300  # 5 minutes
    MAX_PDF_PAGES = 50
    
    # Supported file formats
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    SUPPORTED_AUDIO_FORMATS = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac']
    SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.txt']
    
    # Gamification
    POINTS_PER_MOOD_ANALYSIS = 5
    POINTS_PER_GAME = 10
    POINTS_PER_COMMUNICATION_ANALYSIS = 15
    POINTS_PER_MEAL_PLAN = 25
    POINTS_PER_TASK_PLAN = 15
    POINTS_PER_NUTRITION_ADVICE = 10
    POINTS_PER_SUMMARY = 30
    
    # User data retention
    MAX_EMOTION_HISTORY = 20
    MAX_STRESS_HISTORY = 20


settings = Settings()
