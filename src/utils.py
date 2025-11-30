"""Utility functions for Mindmate AI."""

import os
import functools
import traceback
from typing import Callable, Dict, Any, List
from .config import logger

# Simple metrics storage
metrics = {
    "counters": {},
    "timers": {}
}


def metric_inc(name: str, value: int = 1):
    """Increment a counter metric."""
    if name not in metrics["counters"]:
        metrics["counters"][name] = 0
    metrics["counters"][name] += value


def metric_time(name: str, duration: float):
    """Record a timing metric."""
    if name not in metrics["timers"]:
        metrics["timers"][name] = []
    metrics["timers"][name].append(duration)


def get_metrics() -> Dict:
    """Get all collected metrics."""
    return {
        "counters": metrics["counters"],
        "timers": {
            k: {
                "count": len(v),
                "avg": sum(v) / len(v) if v else 0,
                "total": sum(v)
            }
            for k, v in metrics["timers"].items()
        }
    }


def safe_file_read(file_path: str, allowed_extensions: List[str]) -> Dict:
    """
    Safely validate and read a file.
    
    Parameters:
    - file_path: Path to the file
    - allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.jpg'])
    
    Returns: Dict with status and error message if failed
    """
    try:
        # Check extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in allowed_extensions:
            return {
                "status": "error",
                "error": f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error": f"File not found: {file_path}"
            }
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            return {
                "status": "error",
                "error": "File is empty"
            }
        
        # Check file size (50MB limit)
        max_size = 50 * 1024 * 1024
        if os.path.getsize(file_path) > max_size:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return {
                "status": "error",
                "error": f"File too large ({size_mb:.1f}MB). Maximum: 50MB"
            }
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return {
            "status": "error",
            "error": f"File validation failed: {str(e)}"
        }


def safe_tool_wrapper(func: Callable) -> Callable:
    """
    Wraps agent functions with error handling.
    
    Usage:
        wrapped_function = safe_tool_wrapper(original_function)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            return {
                "status": "error",
                "agent": func.__name__,
                "error_message": str(e),
                "user_message": f"Sorry, I encountered an issue with {func.__name__.replace('_', ' ')}. Please try again or rephrase your request."
            }
    
    return wrapper


def format_response(data: Dict) -> str:
    """
    Format agent response data into readable text.
    
    Parameters:
    - data: Response dictionary from any agent
    
    Returns: Formatted string for display
    """
    if data.get("status") == "error":
        return f"❌ Error: {data.get('error_message', 'Unknown error')}\n{data.get('user_message', '')}"
    
    # Handle different agent responses
    if "mood_score" in data:
        # Mood Agent
        return f"""
{data.get('greeting', '')}

**Mood Analysis:**
- Score: {data['mood_score']}/10
- Emotion: {data['emotion']}
- Assessment: {data['assessment']}
- Trend: {data.get('trend', 'N/A')}

**Coping Strategy:**
{data['coping_strategy']}

*+{data['points_earned']} points | Total: {data['total_points']}*
"""
    
    elif "game_type" in data:
        # Stress Buster
        output = f"{data.get('message', '')}\n\n**{data['game_type'].upper()}**\n\n{data['question']}\n"
        if data.get('options'):
            output += "\n" + "\n".join(data['options']) + "\n"
        if data.get('hint'):
            output += f"\n💡 Hint: {data['hint']}\n"
        output += f"\n**Answer:** {data['answer']}\n"
        if data.get('fun_fact'):
            output += f"📚 {data['fun_fact']}\n"
        return output
    
    elif "analysis" in data and "style" in data.get("analysis", {}):
        # Interpersonal Coach
        return f"""
**Communication Analysis:**
- Style: {data['analysis']['style']}
- Tone Score: {data['analysis']['tone_score']}

**Coaching Tips:**
{chr(10).join(f'  • {tip}' for tip in data.get('coaching', []))}

*+{data['stats']['points_earned']} points*
"""
    
    elif "meal_plans" in data:
        # Meal Planner
        output = "**Meal Plan:**\n\n"
        for plan in data['meal_plans'][:2]:  # Show first 2 days
            output += f"**{plan['day']}:**\n"
            for meal_name, meal_info in plan['meals'].items():
                output += f"  • {meal_name.title()}: {meal_info['dish']} ({meal_info['time']})\n"
        return output + f"\n*+{data['stats']['points_earned']} points*"
    
    elif "tasks" in data:
        # Task Planner
        output = f"**Task Plan** ({data['summary']['total_time']})\n\n**Top Priorities:**\n"
        for task in data['top_3_priorities']:
            output += f"  1. {task}\n"
        return output + f"\n*+{data['stats']['points_earned']} points*"
    
    elif "recommended_foods" in data:
        # Nutrition Advisor
        output = f"**Nutrition Advice: {data['goal']}**\n\n**Recommended Foods:**\n"
        output += ", ".join(data['recommended_foods'][:4]) + "\n\n**Tips:**\n"
        output += "\n".join(f"  • {tip}" for tip in data['tips'][:3])
        return output + f"\n\n*+{data['stats']['points_earned']} points*"
    
    elif "summary" in data:
        # Summarizer
        return f"""
**Summary** ({data['metadata']['reading_time']} read)

{data['summary']}

**Key Points:**
{chr(10).join(f'  • {point}' for point in data.get('key_points', [])[:3])}

*+{data['stats']['points_earned']} points*
"""
    
    # Default fallback
    return str(data)
