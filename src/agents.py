"""MindMate AI - Agent Functions"""

import time
import re
import os
import json
import logging
import traceback
import tempfile
from typing import Dict, Optional

# Core imports
import speech_recognition as sr
from PIL import Image

# Optional imports with graceful fallbacks
try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa not available - audio analysis will be limited")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available - audio conversion limited")

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2
        from PyPDF2 import PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False
        logging.warning("pypdf/PyPDF2 not available - PDF support disabled")

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("requests/BeautifulSoup not available - URL support disabled")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google.generativeai not available - AI features limited")

from .config import logger
from .user_model import get_user, get_greeting, user_journeys
from .utils import metric_inc, metric_time, safe_file_read


# ============================================================================
# AGENT 1 - MOOD AGENT
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
    
    # Generate coping strategy
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
    user.total_points += 5
    metric_inc("mood_analyses")
    metric_time("mood_agent", time.time() - start)
    
    return {
        "mood_score": score,
        "emotion": emotion,
        "stress_level": stress_level,
        "assessment": assessment,
        "coping_strategy": coping,
        "trend": trend,
        "points_earned": 5,
        "total_points": user.total_points,
        "greeting": get_greeting(user_id)
    }


# ============================================================================
# AGENT 2 - STRESS BUSTER (GAMES)
# ============================================================================

def play_stress_game(user_id: str, game_type: str = "random") -> Dict:
    """
    Provide fun mental break games for stress relief.
    
    Parameters:
    - user_id: User identifier
    - game_type: "riddle", "trivia", "brain_teaser", "pattern", "detective", "random"
    
    Returns: Game content with question and answer
    """
    import random
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
            {"q": "🎵 Which artist has the most Grammy Awards?", "opts": ["A) Beyoncé", "B) Taylor Swift", "C) Adele"], "a": "A) Beyoncé ✅", "fact": "She has 32 Grammy Awards!"},
        ],
        "brain_teaser": [
            {"q": f"🧠 {user.name}, a bus driver goes the wrong way down a one-way street, passes 10 police officers, but doesn't get a ticket. Why?", "a": "He was WALKING! 🚶"},
            {"q": "🧠 What can you hold in your right hand but never in your left hand?", "a": "Your LEFT HAND! 🤚"},
        ],
        "pattern": [
            {"q": "🔢 What comes next? 2, 4, 8, 16, ?", "a": "32 (each number doubles)"},
            {"q": "🔢 What comes next? 1, 1, 2, 3, 5, 8, ?", "a": "13 (Fibonacci sequence)"},
        ],
        "detective": [
            {"q": f"🔍 {user.name}, a man is found dead with only water and broken glass. How?", "hint": "Think about what was IN the glass...", "a": "🎯 He was a fish! The glass was his fishbowl!"},
        ]
    }
    
    # Select game type
    if game_type == "random" or game_type not in games:
        recent = user.game_scores.get("recent_types", [])
        available = [t for t in games.keys() if t not in recent[-2:]]
        game_type = random.choice(available if available else list(games.keys()))
    
    selected = random.choice(games[game_type])
    
    result = {
        "game_type": game_type,
        "question": selected["q"],
        "answer": selected["a"],
        "hint": selected.get("hint"),
        "options": selected.get("opts", []),
        "fun_fact": selected.get("fact"),
    }
    
    user.streaks["games"] = user.streaks.get("games", 0) + 1
    user.total_points += 10
    
    if "recent_types" not in user.game_scores:
        user.game_scores["recent_types"] = []
    user.game_scores["recent_types"].append(game_type)
    
    total_played = user.game_scores.get("total_played", 0) + 1
    user.game_scores["total_played"] = total_played
    
    result["stats"] = {
        "streak": user.streaks["games"],
        "total_games": total_played,
        "points_earned": 10,
        "total_points": user.total_points
    }
    result["message"] = f"🎯 Game #{total_played}! Take a brain break, {user.name}! 🧠✨"
    
    metric_inc("games_played")
    metric_time("stress_buster", time.time() - start)
    
    return result


# ============================================================================
# AGENT 3 - INTERPERSONAL COACH
# ============================================================================

def analyze_audio_features(audio_path: str) -> Dict:
    """Analyze vocal characteristics: tone, pace, volume, clarity, pitch."""
    if not LIBROSA_AVAILABLE:
        return {"status": "limited", "message": "librosa not available - only basic transcription"}
    
    try:
        import librosa
        import numpy as np
        
        y, sr_rate = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr_rate)
        
        if duration < 0.5:
            return {"status": "error", "message": "Audio too short (min 0.5 seconds)"}
        
        # Volume analysis
        rms = librosa.feature.rms(y=y)[0]
        avg_volume = float(np.mean(rms))
        
        if avg_volume > 0.15:
            volume_level = "loud"
            volume_note = "Speaking loudly - may come across as aggressive"
        elif avg_volume < 0.03:
            volume_level = "soft"
            volume_note = "Speaking softly - may seem unconfident"
        else:
            volume_level = "moderate"
            volume_note = "Good volume - clear and audible"
        
        # Pace analysis
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr_rate, backtrack=False)
        pace_per_sec = len(onset_frames) / duration if duration > 0 else 0
        
        if pace_per_sec > 4:
            pace_level = "fast"
            pace_note = "Speaking quickly - may indicate nervousness"
        elif pace_per_sec < 2:
            pace_level = "slow"
            pace_note = "Speaking slowly - sounds thoughtful"
        else:
            pace_level = "moderate"
            pace_note = "Good speaking pace"
        
        confidence_score = 5
        if volume_level == "moderate": confidence_score += 2
        if pace_level == "moderate": confidence_score += 2
        
        return {
            "status": "success",
            "duration_seconds": round(duration, 2),
            "volume": {"level": volume_level, "note": volume_note, "score": 8 if volume_level == "moderate" else 5},
            "pace": {"level": pace_level, "note": pace_note, "score": 8 if pace_level == "moderate" else 6},
            "confidence_score": confidence_score,
            "overall_score": 7.0
        }
        
    except Exception as e:
        logger.error(f"Audio feature analysis error: {e}")
        return {"status": "error", "message": str(e)}


def analyze_interpersonal(
    user_id: str,
    text: Optional[str] = None,
    audio_path: Optional[str] = None,
    relationship: str = "colleague"
) -> Dict:
    """
    Comprehensive interpersonal skills coach.
    
    Parameters:
    - user_id: User identifier
    - text: Text to analyze
    - audio_path: Path to audio file (optional)
    - relationship: "boss", "colleague", "partner", "family", "friend"
    
    Returns: Communication analysis with coaching
    """
    start = time.time()
    user = get_user(user_id)
    
    # Audio transcription
    transcript = None
    audio_features = None
    
    if audio_path:
        try:
            valid_extensions = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac']
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return {"status": "error", "message": f"Unsupported format: {file_ext}"}
            
            if not os.path.exists(audio_path):
                return {"status": "error", "message": "Audio file not found"}
            
            # Convert to WAV if needed
            if not audio_path.endswith('.wav') and PYDUB_AVAILABLE:
                audio = AudioSegment.from_file(audio_path)
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    wav_path = tmp.name
                audio.export(wav_path, format="wav")
                audio_path = wav_path
            
            # Transcribe
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                transcript = recognizer.recognize_google(audio_data)
                text = transcript
            
            # Analyze features
            audio_features = analyze_audio_features(audio_path)
            
        except sr.UnknownValueError:
            return {"status": "error", "message": "Could not understand audio"}
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            return {"status": "error", "message": f"Audio processing failed: {str(e)}"}
    
    if not text:
        return {
            "status": "needs_input",
            "message": f"🎤 {user.name}, I can analyze your communication!",
            "options": ["Type: 'Analyze: [your message]'", "Upload audio (WAV/MP3)"]
        }
    
    lower = text.lower()
    
    # Pattern detection
    analysis = {"style": "neutral", "tone_score": 6, "issues": [], "strengths": []}
    
    aggressive_patterns = [
        (r"\byou always\b", "Absolute blame"),
        (r"\byou never\b", "Absolute blame"),
        (r"\byou should\b", "Commanding tone"),
    ]
    
    assertive_patterns = [
        (r"\bi feel\b.*\bwhen\b", "✅ Great 'I feel when' statement!"),
        (r"\bi think\b", "✅ Owning your opinion"),
    ]
    
    aggressive_count = sum(1 for p, _ in aggressive_patterns if re.search(p, lower))
    assertive_count = sum(1 for p, _ in assertive_patterns if re.search(p, lower))
    
    if aggressive_count >= 2:
        analysis["style"] = "❌ AGGRESSIVE"
        analysis["tone_score"] = 3
    elif assertive_count >= 1:
        analysis["style"] = "✅ ASSERTIVE"
        analysis["tone_score"] = 8
    
    # Coaching
    coaching = []
    if "AGGRESSIVE" in analysis["style"]:
        coaching = ["Replace 'you always' with 'when this happens, I feel...'"]
    else:
        coaching = [f"Great work, {user.name}!"]
    
    user.total_points += 15
    metric_inc("communication_analyses")
    metric_time("interpersonal_coach", time.time() - start)
    
    return {
        "status": "analyzed",
        "original_message": text,
        "analysis": {"style": analysis["style"], "tone_score": f"{analysis['tone_score']}/10"},
        "coaching": coaching,
        "stats": {"points_earned": 15, "total_points": user.total_points}
    }


# ============================================================================
# AGENT 4 - MEAL PLANNER
# ============================================================================

def analyze_food_image(image_path: str) -> Dict:
    """Use Gemini Vision to detect food items."""
    if not GENAI_AVAILABLE:
        return {"status": "error", "message": "Gemini not available", "items": []}
    
    try:
        image = Image.open(image_path)
        image.verify()
        image = Image.open(image_path)
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content([
            "List all food items visible. Return comma-separated list or 'none'.",
            image
        ])
        
        result_text = response.text.strip().lower()
        if result_text == "none":
            return {"status": "no_food", "items": []}
        
        items = [item.strip() for item in result_text.split(',') if item.strip()]
        return {"status": "success", "items": items}
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {"status": "error", "message": str(e), "items": []}


def plan_meals(
    user_id: str,
    ingredients: Optional[str] = None,
    image_path: Optional[str] = None,
    days: int = 3
) -> Dict:
    """
    Create meal plans from ingredients.
    
    Parameters:
    - user_id: User identifier
    - ingredients: Comma-separated list
    - image_path: Path to food image (optional)
    - days: Number of days (1-7)
    
    Returns: Meal plans with recipes
    """
    start = time.time()
    user = get_user(user_id)
    groceries = []
    
    # Process image
    if image_path:
        result = analyze_food_image(image_path)
        if result["status"] == "success":
            groceries.extend(result["items"])
    
    # Process text
    if ingredients:
        items = [g.strip().lower() for g in re.split(r'[,;]', ingredients) if len(g.strip()) > 2]
        groceries.extend(items)
    
    groceries = list(set(groceries))
    
    if not groceries:
        return {
            "status": "needs_input",
            "message": f"🍳 {user.name}, I need ingredients!",
            "example": "Meal plan: chicken, rice, broccoli"
        }
    
    # Generate simple meal plan
    meal_plans = []
    days = min(max(1, days), 7)
    
    for day in range(1, days + 1):
        meal_plans.append({
            "day": f"Day {day}",
            "meals": {
                "breakfast": {"dish": f"Eggs with {groceries[0] if groceries else 'vegetables'}", "time": "15 min"},
                "lunch": {"dish": f"Grilled {groceries[0]} salad", "time": "20 min"},
                "dinner": {"dish": f"Stir-fry with rice", "time": "30 min"}
            }
        })
    
    user.total_points += 25
    metric_inc("meal_plans")
    metric_time("meal_planner", time.time() - start)
    
    return {
        "status": "complete",
        "ingredients_found": groceries,
        "meal_plans": meal_plans,
        "days_planned": days,
        "stats": {"points_earned": 25, "total_points": user.total_points}
    }


# ============================================================================
# AGENT 5 - TASK PLANNER
# ============================================================================

def plan_tasks(user_id: str, tasks_text: str) -> Dict:
    """
    Organize and prioritize tasks.
    
    Parameters:
    - user_id: User identifier
    - tasks_text: Comma-separated tasks
    
    Returns: Prioritized task list
    """
    start = time.time()
    user = get_user(user_id)
    
    tasks = [t.strip() for t in re.split(r'[,;]', tasks_text) if len(t.strip()) > 2]
    
    if not tasks:
        return {
            "status": "needs_input",
            "message": f"📋 {user.name}, please list your tasks!",
            "example": "Tasks: finish report, call client, workout"
        }
    
    scheduled = []
    total_time = 0
    
    for i, task in enumerate(tasks):
        est = 30  # default minutes
        priority = 10 - i
        
        if any(w in task.lower() for w in ["urgent", "important"]):
            priority += 5
        
        scheduled.append({
            "task": task,
            "estimate_min": est,
            "priority": max(1, min(15, priority)),
            "category": "urgent" if priority > 10 else "normal"
        })
        total_time += est
    
    scheduled.sort(key=lambda x: x["priority"], reverse=True)
    
    user.total_points += 15
    metric_inc("tasks_planned")
    metric_time("task_planner", time.time() - start)
    
    return {
        "status": "planned",
        "tasks": scheduled,
        "summary": {
            "total_tasks": len(scheduled),
            "total_time": f"{total_time//60}h {total_time%60}m",
        },
        "top_3_priorities": [t["task"] for t in scheduled[:3]],
        "stats": {"points_earned": 15, "total_points": user.total_points}
    }


# ============================================================================
# AGENT 6 - NUTRITION ADVISOR
# ============================================================================

def get_nutrition_advice(user_id: str, goal: str) -> Dict:
    """
    Provide nutrition advice based on goals.
    
    Parameters:
    - user_id: User identifier
    - goal: User's wellness goal
    
    Returns: Personalized nutrition guidance
    """
    start = time.time()
    user = get_user(user_id)
    lower = goal.lower()
    
    advice_db = {
        "stress": {
            "keywords": ["stress", "anxiety", "calm"],
            "goal_name": "Stress Management",
            "foods": ["Dark chocolate", "Walnuts", "Salmon", "Green tea"],
            "tips": ["🍫 Magnesium reduces cortisol", "🐟 Omega-3s reduce anxiety"]
        },
        "energy": {
            "keywords": ["energy", "tired", "fatigue"],
            "goal_name": "Energy Boost",
            "foods": ["Oatmeal", "Eggs", "Bananas", "Almonds"],
            "tips": ["🥚 Protein sustains energy", "💧 Drink more water!"]
        }
    }
    
    selected = None
    for key, data in advice_db.items():
        if any(kw in lower for kw in data["keywords"]):
            selected = data
            break
    
    if not selected:
        selected = {
            "goal_name": "General Wellness",
            "foods": ["Vegetables", "Lean proteins", "Whole grains"],
            "tips": ["🌈 Eat the rainbow", "💧 Stay hydrated"]
        }
    
    user.total_points += 10
    metric_inc("nutrition_advice")
    metric_time("nutrition_agent", time.time() - start)
    
    return {
        "status": "success",
        "goal": selected["goal_name"],
        "recommended_foods": selected["foods"],
        "tips": selected["tips"],
        "stats": {"points_earned": 10, "total_points": user.total_points}
    }


# ============================================================================
# AGENT 7 - SUMMARIZER
# ============================================================================

def extract_from_url(url: str) -> Dict:
    """Extract text from URL."""
    if not WEB_SCRAPING_AVAILABLE:
        return {"status": "error", "message": "requests/BeautifulSoup not available"}
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all(['p', 'h1', 'h2'])
        text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return {
            "status": "success",
            "type": "url",
            "content": text[:15000],
            "word_count": len(text.split())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def extract_from_pdf(pdf_path: str) -> Dict:
    """Extract text from PDF."""
    if not PYPDF_AVAILABLE:
        return {"status": "error", "message": "pypdf not available"}
    
    try:
        validation = safe_file_read(pdf_path, ['.pdf'])
        if validation["status"] == "error":
            return {"status": "error", "message": validation["error"]}
        
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages[:50]:
                text += page.extract_text() + "\n"
        
        return {
            "status": "success",
            "type": "pdf",
            "content": text[:15000],
            "word_count": len(text.split())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def summarize_content(
    user_id: str,
    text: Optional[str] = None,
    url: Optional[str] = None,
    pdf_path: Optional[str] = None,
    output_format: str = "all"
) -> Dict:
    """
    Enhanced summarizer supporting TEXT, URL, and PDF.
    
    Parameters:
    - user_id: User identifier
    - text: Direct text input
    - url: URL to fetch
    - pdf_path: Path to PDF
    - output_format: "summary", "quiz", "all"
    
    Returns: Analysis with insights
    """
    start = time.time()
    user = get_user(user_id)
    
    extracted = None
    
    if url:
        extracted = extract_from_url(url)
    elif pdf_path:
        extracted = extract_from_pdf(pdf_path)
    elif text and len(text) >= 50:
        extracted = {"status": "success", "type": "text", "content": text, "word_count": len(text.split())}
    else:
        return {
            "status": "needs_input",
            "message": f"📄 {user.name}, I can summarize text, URLs, or PDFs!",
            "example": "Summarize: [paste text]"
        }
    
    if extracted.get("status") == "error":
        return extracted
    
    content = extracted["content"]
    word_count = extracted.get("word_count", 0)
    
    # Simple extractive summary
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    summary = '. '.join(sentences[:3]) + '.'
    
    user.total_points += 30
    metric_inc("summaries")
    metric_time("summarizer", time.time() - start)
    
    return {
        "status": "complete",
        "source_type": extracted.get("type"),
        "metadata": {"word_count": word_count, "reading_time": f"{max(1, word_count//200)} min"},
        "summary": summary,
        "key_points": sentences[:5],
        "stats": {"points_earned": 30, "total_points": user.total_points}
    }
