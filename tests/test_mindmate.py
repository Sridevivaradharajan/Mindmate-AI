"""
Pytest tests for Mindmate AI Agent.

Run with: pytest tests/test_mindmate.py -v -s
"""

import os
import sys
import pytest
import pytest_asyncio

# Add src to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from google.genai import types as genai_types
from src.Orchestrator import mindmate_agent, runner, session_service


@pytest_asyncio.fixture(scope="function")
async def test_session():
    """Create a test session using the orchestrator's session service."""
    await session_service.create_session(
        app_name="mindmate",
        user_id="test_user",
        session_id="test_session"
    )
    yield
    # Cleanup after test (optional)
    try:
        await session_service.delete_session(
            app_name="mindmate",
            user_id="test_user", 
            session_id="test_session"
        )
    except:
        pass


@pytest.mark.asyncio
async def test_mood_agent(test_session):
    """Test Agent 1 - Mood Analysis."""
    print("\n" + "="*70)
    print("[TEST 1/7] Mood Agent")
    print("="*70)
    
    query = "I'm feeling stressed about work"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_stress_buster(test_session):
    """Test Agent 2 - Stress Buster Game."""
    print("\n" + "="*70)
    print("[TEST 2/7] Stress Buster")
    print("="*70)
    
    query = "Give me a riddle"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_interpersonal_coach(test_session):
    """Test Agent 3 - Interpersonal Coach."""
    print("\n" + "="*70)
    print("[TEST 3/7] Interpersonal Coach")
    print("="*70)
    
    query = "Analyze: You never listen to me"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_meal_planner(test_session):
    """Test Agent 4 - Meal Planner."""
    print("\n" + "="*70)
    print("[TEST 4/7] Meal Planner")
    print("="*70)
    
    query = "Meal plan: chicken, rice, broccoli for 3 days"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_task_planner(test_session):
    """Test Agent 5 - Task Planner."""
    print("\n" + "="*70)
    print("[TEST 5/7] Task Planner")
    print("="*70)
    
    query = "Tasks: finish report, call clients, workout"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_nutrition_advisor(test_session):
    """Test Agent 6 - Nutrition Advisor."""
    print("\n" + "="*70)
    print("[TEST 6/7] Nutrition Advisor")
    print("="*70)
    
    query = "What should I eat for more energy?"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_summarizer(test_session):
    """Test Agent 7 - Summarizer."""
    print("\n" + "="*70)
    print("[TEST 7/7] Summarizer")
    print("="*70)
    
    query = "Summarize: AI is transforming healthcare with 95% accuracy in cancer detection. Deep learning models analyze medical images faster than human doctors. The technology shows promise but requires careful validation."
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query[:50]}...")
            print(f"Response: {response[:300]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


@pytest.mark.asyncio
async def test_agent_integration(test_session):
    """Test that the main agent responds to general queries."""
    print("\n" + "="*70)
    print("[INTEGRATION TEST] General Query")
    print("="*70)
    
    query = "Hi, what can you help me with?"
    
    response_found = False
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query)]
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"\nQuery: {query}")
            print(f"Response: {response[:400]}...")
            assert len(response) > 0
            response_found = True
            break
    
    assert response_found, "No response received from agent"


def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "="*70)
    print("[IMPORT TEST] Verifying all modules")
    print("="*70)
    
    from src import (
        mindmate_agent,
        analyze_mood,
        play_stress_game,
        analyze_interpersonal,
        plan_meals,
        plan_tasks,
        get_nutrition_advice,
        summarize_content,
    )
    
    assert mindmate_agent is not None
    assert callable(analyze_mood)
    assert callable(play_stress_game)
    assert callable(analyze_interpersonal)
    assert callable(plan_meals)
    assert callable(plan_tasks)
    assert callable(get_nutrition_advice)
    assert callable(summarize_content)
    
    print("✅ All imports successful")


if __name__ == "__main__":
    # Allow running directly with: python tests/test_mindmate.py
    pytest.main([__file__, "-v", "-s"])