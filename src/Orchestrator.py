"""
ADK Agent Orchestrator
Sets up the main MindMate agent with all tools
"""

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
import traceback

from .agents import (
    analyze_mood,
    play_stress_game,
    analyze_interpersonal,
    plan_meals,
    plan_tasks,
    get_nutrition_advice,
    summarize_content
)
from .config import GEMINI_MODEL, AGENT_NAME, APP_NAME, setup_logging

logger = setup_logging()


def safe_tool_wrapper(func):
    """Decorator to wrap tool functions with error handling."""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, dict) and result.get("status") == "error":
                user_message = result.get("message", "An error occurred")
                return {
                    "status": "error",
                    "message": f"I encountered an issue: {user_message}. Please try again.",
                    "original_error": user_message
                }
            return result
        except Exception as e:
            logger.error(f"Tool {func.__name__} error: {e}\n{traceback.format_exc()}")
            return {
                "status": "error",
                "message": "I'm sorry, something went wrong. Please try again.",
                "function": func.__name__
            }
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Create wrapped versions
wrapped_analyze_mood = safe_tool_wrapper(analyze_mood)
wrapped_play_stress_game = safe_tool_wrapper(play_stress_game)
wrapped_analyze_interpersonal = safe_tool_wrapper(analyze_interpersonal)
wrapped_plan_meals = safe_tool_wrapper(plan_meals)
wrapped_plan_tasks = safe_tool_wrapper(plan_tasks)
wrapped_get_nutrition_advice = safe_tool_wrapper(get_nutrition_advice)
wrapped_summarize_content = safe_tool_wrapper(summarize_content)

# Create ADK FunctionTools
mood_tool = FunctionTool(wrapped_analyze_mood)
game_tool = FunctionTool(wrapped_play_stress_game)
interpersonal_tool = FunctionTool(wrapped_analyze_interpersonal)
meal_tool = FunctionTool(wrapped_plan_meals)
task_tool = FunctionTool(wrapped_plan_tasks)
nutrition_tool = FunctionTool(wrapped_get_nutrition_advice)
summarize_tool = FunctionTool(wrapped_summarize_content)

ALL_TOOLS = [
    mood_tool,
    game_tool,
    interpersonal_tool,
    meal_tool,
    task_tool,
    nutrition_tool,
    summarize_tool
]

# System instruction
SYSTEM_INSTRUCTION = """You are MindMate AI, a compassionate wellness companion with 7 specialized agents.

🔧 AVAILABLE TOOLS:

1. analyze_mood(user_id, message, stress_level=5) - Emotional support & mood tracking
2. play_stress_game(user_id, game_type="random") - Fun mental break games
3. analyze_interpersonal(user_id, text=None, audio_path=None, relationship="colleague") - Communication analysis
4. plan_meals(user_id, ingredients=None, image_path=None, days=3) - Meal planning
5. plan_tasks(user_id, tasks_text) - Task organization
6. get_nutrition_advice(user_id, goal) - Nutrition guidance
7. summarize_content(user_id, text=None, url=None, pdf_path=None) - Content summarization

💙 PERSONALITY:
- Warm, empathetic, and supportive
- Always use user's name when available
- Celebrate progress with points/streaks
- Provide encouragement

🚨 PRIORITY: If stress_level > 8, immediately offer play_stress_game.

Remember: You're a supportive friend, not a therapist. Encourage professional help for serious concerns."""

# Create ADK Agent
mindmate_agent = Agent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    description="MindMate AI - Your wellness companion with mood tracking, stress relief, meal planning, and more",
    instruction=SYSTEM_INSTRUCTION,
    tools=ALL_TOOLS
)

# Create session service and runner
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=mindmate_agent, app_name=APP_NAME)

logger.info("✅ MindMate orchestrator initialized")
