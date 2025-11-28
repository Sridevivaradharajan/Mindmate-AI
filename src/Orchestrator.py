"""ADK Orchestrator - Main agent setup."""

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool

from .config import logger
from .utils import safe_tool_wrapper
from .agents import (
    analyze_mood,
    play_stress_game,
    analyze_interpersonal,
    plan_meals,
    plan_tasks,
    get_nutrition_advice,
    summarize_content,
)

# Wrap all agent functions with error handling
wrapped_analyze_mood = safe_tool_wrapper(analyze_mood)
wrapped_play_stress_game = safe_tool_wrapper(play_stress_game)
wrapped_analyze_interpersonal = safe_tool_wrapper(analyze_interpersonal)
wrapped_plan_meals = safe_tool_wrapper(plan_meals)
wrapped_plan_tasks = safe_tool_wrapper(plan_tasks)
wrapped_get_nutrition_advice = safe_tool_wrapper(get_nutrition_advice)
wrapped_summarize_content = safe_tool_wrapper(summarize_content)

# Create ADK FunctionTools
ALL_TOOLS = [
    FunctionTool(wrapped_analyze_mood),
    FunctionTool(wrapped_play_stress_game),
    FunctionTool(wrapped_analyze_interpersonal),
    FunctionTool(wrapped_plan_meals),
    FunctionTool(wrapped_plan_tasks),
    FunctionTool(wrapped_get_nutrition_advice),
    FunctionTool(wrapped_summarize_content),
]

# System instruction (copy from your notebook)
SYSTEM_INSTRUCTION = """
[Copy the full SYSTEM_INSTRUCTION from your notebook Cell 12]
"""

# Create ADK Agent
mindmate_agent = Agent(
    name="mindmate",
    model="gemini-2.5-flash",
    description="MindMate AI - Your wellness companion",
    instruction=SYSTEM_INSTRUCTION,
    tools=ALL_TOOLS
)

# Create session service and runner
session_service = InMemorySessionService()
runner = InMemoryRunner(agent=mindmate_agent, app_name="mindmate")

logger.info("✅ Mindmate AI orchestrator ready")
