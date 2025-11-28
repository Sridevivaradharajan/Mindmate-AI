"""
Utility functions for Mindmate AI.

This module provides file validation, error handling, and helper functions.
"""

import os
import traceback
from typing import Dict, List, Callable
from functools import wraps

from .config import logger, settings


# ============================================================================
# FILE VALIDATION
# ============================================================================

def safe_file_read(file_path: str, expected_extensions: List[str] = None) -> Dict:
    """
    Safely validate and read file with comprehensive error handling.
    
    Args:
        file_path: Path to file
        expected_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
        
    Returns:
        dict: {"status": "success/error", "path": str, "error": str}
    """
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
        
        # Check file size (limit from settings)
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        size = os.path.getsize(file_path)
        if size > max_size:
            return {
                "status": "error",
                "error": f"File too large: {size / (1024*1024):.1f}MB (max {settings.MAX_FILE_SIZE_MB}MB)",
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


# ============================================================================
# ERROR HANDLING
# ============================================================================

def safe_tool_wrapper(func: Callable) -> Callable:
    """
    Decorator to wrap tool functions with comprehensive error handling.
    
    This ensures that agent functions never crash and always return
    user-friendly error messages.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Check if result is an error dict
            if isinstance(result, dict) and result.get("status") == "error":
                # Make error message more user-friendly
                user_message = result.get("message", "An error occurred")
                return {
                    "status": "error",
                    "message": f"I encountered an issue: {user_message}. "
                               "Please try again or use a different format.",
                    "original_error": user_message
                }
            return result
            
        except Exception as e:
            logger.error(f"Tool {func.__name__} error: {e}\n{traceback.format_exc()}")
            return {
                "status": "error",
                "message": "I'm sorry, something went wrong while processing your request. "
                          "Please try again.",
                "function": func.__name__,
                "error_type": type(e).__name__
            }
    
    return wrapper


# ============================================================================
# AUDIO PROCESSING UTILITIES
# ============================================================================

def convert_audio_to_wav(audio_path: str) -> Dict:
    """
    Convert various audio formats to WAV for processing.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        dict: {"status": "success/error", "wav_path": str, "message": str}
    """
    try:
        from pydub import AudioSegment
        import tempfile
        
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        # Already WAV
        if file_ext == '.wav':
            return {"status": "success", "wav_path": audio_path}
        
        logger.info(f"Converting audio file: {audio_path} ({file_ext})")
        
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Create temporary wav file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            wav_path = tmp.name
        
        # Export to WAV format
        audio.export(wav_path, format="wav")
        
        logger.info(f"Audio converted successfully to: {wav_path}")
        return {"status": "success", "wav_path": wav_path}
        
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}\n{traceback.format_exc()}")
        
        # Provide helpful error message
        if "ffmpeg" in str(e).lower() or "avconv" in str(e).lower():
            return {
                "status": "error", 
                "message": f"Could not convert {file_ext} audio. FFmpeg is required. "
                          "Please upload WAV format instead, or ensure FFmpeg is installed."
            }
        else:
            return {
                "status": "error", 
                "message": f"Audio conversion failed: {str(e)}. "
                          "Please try uploading a WAV file instead."
            }


# ============================================================================
# TEXT PROCESSING UTILITIES
# ============================================================================

def clean_json_response(text: str) -> str:
    """
    Clean JSON from markdown code blocks.
    
    Args:
        text: Raw text potentially containing markdown
        
    Returns:
        str: Cleaned JSON string
    """
    # Remove markdown code blocks
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]
    
    return text.strip()


def truncate_text(text: str, max_length: int = 15000) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum character length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_stress_level(level: int) -> int:
    """
    Validate and clamp stress level to 1-10 range.
    
    Args:
        level: Stress level input
        
    Returns:
        int: Clamped stress level (1-10)
    """
    return max(1, min(10, level))


def validate_days(days: int) -> int:
    """
    Validate and clamp meal planning days to 1-7 range.
    
    Args:
        days: Number of days
        
    Returns:
        int: Clamped days (1-7)
    """
    return max(1, min(7, days))
