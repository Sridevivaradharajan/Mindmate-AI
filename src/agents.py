"""
MindMate AI - Specialized Agent Functions
Contains all 7 core wellness agents with comprehensive functionality
"""

import os
import time
import re
import logging
import traceback
import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

# Image processing
from PIL import Image

# Audio processing
import speech_recognition as sr

# Document processing
import requests
from bs4 import BeautifulSoup
import PyPDF2

# Google AI
import google.generativeai as genai

# Setup logging
logger = logging.getLogger("MindMate.Agents")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def safe_file_read(file_path: str, expected_extensions: list = None) -> Dict:
    """
    Safely validate and read file with comprehensive error handling.
    
    Returns: {"status": "success/error", "path": str, "error": str}
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
        
        # Check file size (limit to 50MB)
        size = os.path.getsize(file_path)
        if size > 50 * 1024 * 1024:
            return {
                "status": "error",
                "error": f"File too large: {size / (1024*1024):.1f}MB (max 50MB)",
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
# AGENT 1: MOOD AGENT
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
    from user_management import get_user, get_greeting
    from metrics import metric_inc, metric_time
    
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
    
    # Generate coping strategy based on score
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
# AGENT 2: STRESS BUSTER (GAMES)
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
    from user_management import get_user
    from metrics import metric_inc, metric_time
    
    start = time.time()
    user = get_user(user_id)
    
    games = {
        "riddle": [
            {"q": f"🤔 {user.name}, I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?", "a": "An ECHO! 🔊"},
            {"q": f"🤔 {user.name}, what has keys but no locks, space but no room, and you can enter but can't go inside?", "a": "A KEYBOARD! ⌨️"},
            {"q": "🤔 The more you take, the more you leave behind. What am I?", "a": "FOOTSTEPS! 👣"},
            {"q": "🤔 I have cities, but no houses live there. I have mountains, but no trees grow. I have water, but no fish swim. What am I?", "a": "A MAP! 🗺️"},
            {"q": "🤔 What can travel around the world while staying in a corner?", "a": "A STAMP! 📮"},
        ],
        "trivia": [
            {"q": "🎬 In Stranger Things, what tabletop game do the kids play?", "opts": ["A) Monopoly", "B) Dungeons & Dragons", "C) Risk", "D) Chess"], "a": "B) Dungeons & Dragons ✅", "fact": "The Duffer Brothers are huge D&D fans!"},
            {"q": "🎬 What is the highest-grossing film of all time (adjusted)?", "opts": ["A) Titanic", "B) Avatar", "C) Avengers: Endgame", "D) Gone with the Wind"], "a": "D) Gone with the Wind ✅", "fact": "When adjusted for inflation, it beats all modern films!"},
            {"q": "🎵 Which artist has the most Grammy Awards?", "opts": ["A) Beyoncé", "B) Taylor Swift", "C) Adele", "D) Stevie Wonder"], "a": "A) Beyoncé ✅", "fact": "She has 32 Grammy Awards!"},
            {"q": "🌍 What is the smallest country in the world?", "opts": ["A) Monaco", "B) Vatican City", "C) San Marino", "D) Liechtenstein"], "a": "B) Vatican City ✅", "fact": "It's only 0.44 square kilometers!"},
        ],
        "brain_teaser": [
            {"q": f"🧠 {user.name}, a bus driver goes the wrong way down a one-way street, passes 10 police officers, but doesn't get a ticket. Why?", "a": "He was WALKING! 🚶"},
            {"q": "🧠 What can you hold in your right hand but never in your left hand?", "a": "Your LEFT HAND! 🤚"},
            {"q": "🧠 A man lives on the 10th floor. Every day he takes the elevator down to go to work. When he returns, he takes the elevator to the 7th floor and walks up 3 flights. Why?", "a": "He's too SHORT to reach the 10th floor button! 📏"},
            {"q": "🧠 If you have me, you want to share me. If you share me, you no longer have me. What am I?", "a": "A SECRET! 🤫"},
        ],
        "pattern": [
            {"q": "🔢 What comes next? 2, 4, 8, 16, ?", "a": "32 (each number doubles)"},
            {"q": "🔢 What comes next? 1, 1, 2, 3, 5, 8, ?", "a": "13 (Fibonacci sequence - add previous two)"},
            {"q": "🔢 What comes next? 1, 4, 9, 16, 25, ?", "a": "36 (square numbers: 1², 2², 3²...)"},
            {"q": "🔢 What comes next? A, C, F, J, ?", "a": "O (gaps increase: +2, +3, +4, +5)"},
        ],
        "detective": [
            {"q": f"🔍 {user.name}, a man is found dead in a locked room with only a puddle of water and broken glass. How did he die?", "hint": "Think about what was IN the glass...", "a": "🎯 He was a fish! The glass was his fishbowl that broke!"},
            {"q": "🔍 A woman shoots her husband, then holds him underwater for 5 minutes, then hangs him. Later, they go out for dinner. How?", "hint": "Think photography...", "a": "🎯 She's a PHOTOGRAPHER! She shot a photo, developed it in water, and hung it to dry!"},
        ]
    }
    
    # Select game type
    if game_type == "random" or game_type not in games:
        recent = user.game_scores.get("recent_types", [])
        available = [t for t in games.keys() if t not in recent[-2:]]
        game_type = random.choice(available if available else list(games.keys()))
    
    # Select random game from category
    selected = random.choice(games[game_type])
    
    # Build response
    result = {
        "game_type": game_type,
        "question": selected["q"],
        "answer": selected["a"],
        "hint": selected.get("hint"),
        "options": selected.get("opts", []),
        "fun_fact": selected.get("fact"),
    }
    
    # Update user stats
    user.streaks["games"] = user.streaks.get("games", 0) + 1
    user.total_points += 10
    
    if "recent_types" not in user.game_scores:
        user.game_scores["recent_types"] = []
    user.game_scores["recent_types"].append(game_type)
    
    total_played = user.game_scores.get("total_played", 0) + 1
    user.game_scores["total_played"] = total_played
    
    # Award badges
    if total_played == 5 and "🎮 Game Starter" not in user.badges:
        user.badges.append("🎮 Game Starter")
        result["new_badge"] = "🎮 Game Starter"
    elif total_played == 20 and "🎮🎮 Game Master" not in user.badges:
        user.badges.append("🎮🎮 Game Master")
        result["new_badge"] = "🎮🎮 Game Master"
    elif total_played == 50 and "🎮🎮🎮 Game Legend" not in user.badges:
        user.badges.append("🎮🎮🎮 Game Legend")
        result["new_badge"] = "🎮🎮🎮 Game Legend"
    
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
# AGENT 3: INTERPERSONAL COACH (Text + Audio Analysis)
# ============================================================================

def analyze_audio_features(audio_path: str) -> Dict:
    """
    Analyze vocal characteristics: tone, pace, volume, clarity, pitch.
    Uses librosa for advanced audio analysis.
    """
    try:
        import librosa
        import numpy as np
        
        # Load audio
        y, sr_rate = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr_rate)
        
        if duration < 0.5:
            return {"status": "error", "message": "Audio too short (min 0.5 seconds)"}
        
        # 1. VOLUME/ENERGY ANALYSIS
        rms = librosa.feature.rms(y=y)[0]
        avg_volume = float(np.mean(rms))
        volume_variation = float(np.std(rms))
        
        if avg_volume > 0.15:
            volume_level = "loud"
            volume_note = "Speaking loudly - may come across as aggressive"
        elif avg_volume < 0.03:
            volume_level = "soft"
            volume_note = "Speaking softly - may seem unconfident or passive"
        else:
            volume_level = "moderate"
            volume_note = "Good volume - clear and audible"
        
        volume_consistency = "varied" if volume_variation > 0.05 else "steady"
        
        # 2. SPEAKING PACE ANALYSIS
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr_rate, backtrack=False)
        num_onsets = len(onset_frames)
        pace_per_sec = num_onsets / duration if duration > 0 else 0
        
        if pace_per_sec > 4:
            pace_level = "fast"
            pace_note = "Speaking quickly - may indicate nervousness or excitement"
        elif pace_per_sec < 2:
            pace_level = "slow"
            pace_note = "Speaking slowly - sounds thoughtful but may lose attention"
        else:
            pace_level = "moderate"
            pace_note = "Good speaking pace - easy to follow"
        
        # 3. PITCH ANALYSIS
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr_rate)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        
        if len(pitch_values) > 0:
            avg_pitch = float(np.mean(pitch_values))
            pitch_variation = float(np.std(pitch_values))
            
            if avg_pitch > 220:
                pitch_level = "high"
                pitch_note = "Higher pitch - may indicate stress or excitement"
            elif avg_pitch < 100:
                pitch_level = "low"
                pitch_note = "Lower pitch - sounds calm and authoritative"
            else:
                pitch_level = "medium"
                pitch_note = "Natural pitch range"
            
            if pitch_variation > 50:
                pitch_variety = "expressive"
                pitch_variety_note = "Good vocal variety - engaging to listen to"
            else:
                pitch_variety = "monotone"
                pitch_variety_note = "Monotone delivery - may sound disengaged"
        else:
            avg_pitch = 0
            pitch_level = "unclear"
            pitch_note = "Could not analyze pitch"
            pitch_variety = "unclear"
            pitch_variety_note = ""
        
        # 4. CLARITY ANALYSIS (based on zero-crossing rate)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        avg_zcr = float(np.mean(zcr))
        
        if avg_zcr > 0.15:
            clarity_level = "clear"
            clarity_note = "Clear enunciation - easy to understand"
        elif avg_zcr < 0.05:
            clarity_level = "unclear"
            clarity_note = "Mumbled or unclear speech - work on articulation"
        else:
            clarity_level = "moderate"
            clarity_note = "Acceptable clarity - could improve enunciation"
        
        # 5. PAUSES ANALYSIS (silence detection)
        intervals = librosa.effects.split(y, top_db=30)
        num_segments = len(intervals)
        pause_count = num_segments - 1
        avg_pause = (duration - sum((intervals[:, 1] - intervals[:, 0]) / sr_rate)) / max(pause_count, 1)
        
        if avg_pause > 1.5:
            pause_level = "many_long"
            pause_note = "Long pauses - may indicate uncertainty or search for words"
        elif avg_pause > 0.5:
            pause_level = "natural"
            pause_note = "Natural pausing - allows listener to process"
        else:
            pause_level = "few"
            pause_note = "Few pauses - may sound rushed or nervous"
        
        # 6. OVERALL CONFIDENCE SCORE (0-10)
        confidence_score = 5  # baseline
        
        if volume_level == "moderate": confidence_score += 2
        elif volume_level == "loud": confidence_score += 1
        elif volume_level == "soft": confidence_score -= 2
        
        if pace_level == "moderate": confidence_score += 2
        elif pace_level == "fast": confidence_score -= 1
        elif pace_level == "slow": confidence_score -= 1
        
        if pitch_variety == "expressive": confidence_score += 2
        elif pitch_variety == "monotone": confidence_score -= 2
        
        if clarity_level == "clear": confidence_score += 2
        elif clarity_level == "unclear": confidence_score -= 2
        
        if pause_level == "natural": confidence_score += 1
        elif pause_level == "many_long": confidence_score -= 2
        
        confidence_score = max(1, min(10, confidence_score))
        
        # 7. EMOTIONAL TONE DETECTION
        if avg_volume > 0.15 and pace_per_sec > 4:
            emotional_tone = "agitated/stressed"
        elif avg_volume < 0.05 and pitch_level == "low":
            emotional_tone = "calm/sad"
        elif pitch_variety == "expressive" and volume_level == "moderate":
            emotional_tone = "engaged/enthusiastic"
        elif pitch_variety == "monotone" and pace_level == "slow":
            emotional_tone = "bored/disengaged"
        else:
            emotional_tone = "neutral/controlled"
        
        return {
            "status": "success",
            "duration_seconds": round(duration, 2),
            "volume": {
                "level": volume_level,
                "consistency": volume_consistency,
                "note": volume_note,
                "score": 8 if volume_level == "moderate" else 5 if volume_level == "loud" else 4
            },
            "pace": {
                "level": pace_level,
                "syllables_per_sec": round(pace_per_sec, 2),
                "note": pace_note,
                "score": 8 if pace_level == "moderate" else 6
            },
            "pitch": {
                "level": pitch_level,
                "variety": pitch_variety,
                "note": pitch_note,
                "variety_note": pitch_variety_note,
                "score": 8 if pitch_variety == "expressive" else 4
            },
            "clarity": {
                "level": clarity_level,
                "note": clarity_note,
                "score": 9 if clarity_level == "clear" else 6 if clarity_level == "moderate" else 3
            },
            "pauses": {
                "level": pause_level,
                "average_seconds": round(avg_pause, 2),
                "note": pause_note,
                "score": 8 if pause_level == "natural" else 5
            },
            "confidence_score": confidence_score,
            "emotional_tone": emotional_tone,
            "overall_score": round((
                (8 if volume_level == "moderate" else 5) +
                (8 if pace_level == "moderate" else 6) +
                (8 if pitch_variety == "expressive" else 4) +
                (9 if clarity_level == "clear" else 6) +
                (8 if pause_level == "natural" else 5)
            ) / 5, 1)
        }
        
    except ImportError:
        return {
            "status": "limited",
            "message": "librosa not available - only basic transcription provided"
        }
    except Exception as e:
        logger.error(f"Audio feature analysis error: {e}\n{traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Could not analyze audio features: {str(e)}"
        }


def analyze_interpersonal(
    user_id: str,
    text: str = None,
    audio_path: str = None,
    relationship: str = "colleague"
) -> Dict:
    """
    Comprehensive interpersonal skills coach with FULL audio analysis.
    Analyzes text OR audio (with transcription + vocal tone analysis).
    
    Parameters:
    - user_id: User identifier
    - text: Text to analyze (what user said or wants to say)
    - audio_path: Path to audio file for FULL analysis (transcription + tone/pace/clarity)
    - relationship: "boss", "colleague", "partner", "family", "friend"
    
    Returns: Communication analysis with coaching
    """
    from user_management import get_user
    from metrics import metric_inc, metric_time
    
    start = time.time()
    user = get_user(user_id)
    
    # Audio analysis
    transcript = None
    audio_features = None
    
    if audio_path:
        try:
            # Validate audio file
            valid_audio_extensions = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac']
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext not in valid_audio_extensions:
                return {
                    "status": "error",
                    "message": f"Unsupported audio format: {file_ext}. Please upload: WAV, MP3, M4A, MP4, OGG, or FLAC"
                }
            
            if not os.path.exists(audio_path):
                return {
                    "status": "error",
                    "message": f"Audio file not found: {audio_path}"
                }
            
            if os.path.getsize(audio_path) == 0:
                return {
                    "status": "error",
                    "message": "Audio file is empty. Please upload a valid audio recording."
                }
            
            if os.path.getsize(audio_path) > 50 * 1024 * 1024:
                size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                return {
                    "status": "error",
                    "message": f"Audio file too large ({size_mb:.1f}MB). Maximum size is 50MB."
                }
            
            recognizer = sr.Recognizer()
            
            # Convert to WAV if needed
            if not audio_path.endswith('.wav'):
                try:
                    from pydub import AudioSegment
                    import tempfile
                    
                    logger.info(f"Converting audio file: {audio_path} ({file_ext})")
                    audio = AudioSegment.from_file(audio_path)
                    
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                        wav_path = tmp.name
                    
                    audio.export(wav_path, format="wav")
                    audio_path = wav_path
                    logger.info(f"Audio converted successfully to: {wav_path}")
                    
                except Exception as e:
                    logger.error(f"Audio conversion failed: {e}\n{traceback.format_exc()}")
                    
                    if "ffmpeg" in str(e).lower() or "avconv" in str(e).lower():
                        return {
                            "status": "error", 
                            "message": f"Could not convert {file_ext} audio. FFmpeg is required for {file_ext} files. Please upload WAV format instead, or ensure FFmpeg is installed."
                        }
                    else:
                        return {
                            "status": "error", 
                            "message": f"Audio conversion failed: {str(e)}. Please try uploading a WAV file instead, or type your message directly."
                        }
            
            # Transcribe speech
            try:
                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                    transcript = recognizer.recognize_google(audio_data)
                    text = transcript
                    logger.info(f"Audio transcribed successfully: {len(text)} characters")
            except sr.UnknownValueError:
                return {
                    "status": "error", 
                    "message": "Could not understand the audio. Please ensure: (1) Clear speech, (2) Minimal background noise, (3) Good microphone quality. Try recording again or type your message instead."
                }
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                return {
                    "status": "error",
                    "message": f"Speech recognition service is temporarily unavailable. Please try again in a moment, or type your message instead."
                }
            
            # Analyze vocal features
            audio_features = analyze_audio_features(audio_path)
            
            if audio_features.get("status") == "error":
                logger.warning(f"Audio feature analysis failed: {audio_features.get('message')}")
                audio_features = None
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}\n{traceback.format_exc()}")
            return {
                "status": "error", 
                "message": f"Audio processing failed. Please try uploading a WAV file or typing your message. Technical details: {str(e)}"
            }
    
    if not text:
        return {
            "status": "needs_input",
            "message": f"🎤 {user.name}, I can analyze your communication style!",
            "features": [
                "📝 TEXT: Analyze word choice, tone, assertiveness",
                "🎙️ AUDIO: Analyze speech + volume + pace + clarity + pitch + confidence"
            ],
            "options": [
                "Type: 'Analyze: [what you want to say]'",
                "Upload audio file (WAV recommended, also supports MP3, M4A, MP4, OGG, FLAC)"
            ],
            "examples": [
                "Analyze: You always ignore my suggestions",
                "Analyze: I feel frustrated when meetings run late"
            ],
            "audio_tips": "📌 For best results with audio: Use WAV format, speak clearly, minimize background noise"
        }
    
    lower = text.lower()
    
    # Initialize analysis
    analysis = {
        "style": "neutral",
        "tone_score": 6,
        "clarity_score": 7,
        "confidence_score": 6,
        "empathy_score": 5,
        "issues": [],
        "strengths": [],
        "filler_words": []
    }
    
    # Pattern detection
    aggressive = {
        r"\byou always\b": "Absolute blame ('you always')",
        r"\byou never\b": "Absolute blame ('you never')",
        r"\byou should\b": "Commanding tone",
        r"\bwhy didn'?t you\b": "Accusatory question",
        r"\bwhat'?s wrong with you\b": "Personal attack",
        r"\byou need to\b": "Demanding language",
    }
    
    passive = {
        r"\bmaybe we could\b": "Overly tentative",
        r"\bi guess\b": "Lacks confidence",
        r"\bsorry,? but\b": "Unnecessary apologizing",
        r"\bif that'?s okay\b": "Excessive permission-seeking",
        r"\bjust think\b": "'Just' minimizes your opinion",
        r"\bi'?m no expert\b": "Self-deprecating",
    }
    
    assertive = {
        r"\bi feel\b.*\bwhen\b": "✅ Great 'I feel when' statement!",
        r"\bi think\b": "✅ Owning your opinion",
        r"\bi believe\b": "✅ Confident stance",
        r"\bi need\b": "✅ Clear need expression",
        r"\bi'?d like\b": "✅SVContinuePolite but direct",
r"\blet'?s\b": "✅ Collaborative language",
}
empathetic = {
    r"\bi understand\b": "💙 Shows understanding",
    r"\bi hear you\b": "💙 Active listening",
    r"\bthat must be\b": "💙 Emotional validation",
    r"\bhow do you feel\b": "💙 Checking emotions",
    r"\bi appreciate\b": "💙 Showing gratitude",
}

# Count patterns
aggressive_count = 0
passive_count = 0
assertive_count = 0
empathetic_count = 0

for pattern, desc in aggressive.items():
    if re.search(pattern, lower):
        analysis["issues"].append(f"❌ {desc}")
        aggressive_count += 1

for pattern, desc in passive.items():
    if re.search(pattern, lower):
        analysis["issues"].append(f"⚠️ {desc}")
        passive_count += 1

for pattern, desc in assertive.items():
    if re.search(pattern, lower):
        analysis["strengths"].append(desc)
        assertive_count += 1

for pattern, desc in empathetic.items():
    if re.search(pattern, lower):
        analysis["strengths"].append(desc)
        empathetic_count += 1

# Check filler words
fillers = ["um", "uh", "like", "you know", "basically", "literally", "actually", "honestly"]
found_fillers = [f for f in fillers if f" {f} " in f" {lower} "]
analysis["filler_words"] = found_fillers

# Determine style and scores
if aggressive_count >= 2:
    analysis["style"] = "❌ AGGRESSIVE"
    analysis["tone_score"] = 3
    analysis["confidence_score"] = 7
    analysis["empathy_score"] = 2
elif aggressive_count == 1:
    analysis["style"] = "⚠️ SOMEWHAT AGGRESSIVE"
    analysis["tone_score"] = 5
elif passive_count >= 2:
    analysis["style"] = "⚠️ PASSIVE"
    analysis["tone_score"] = 5
    analysis["confidence_score"] = 3
elif assertive_count >= 2 and empathetic_count >= 1:
    analysis["style"] = "✅ ASSERTIVE & EMPATHETIC (Ideal!)"
    analysis["tone_score"] = 9
    analysis["confidence_score"] = 8
    analysis["empathy_score"] = 8
elif assertive_count >= 1:
    analysis["style"] = "✅ ASSERTIVE"
    analysis["tone_score"] = 8
    analysis["confidence_score"] = 7

analysis["clarity_score"] = max(3, 10 - len(found_fillers) * 2)

# Override with audio analysis if available
if audio_features and audio_features.get("status") == "success":
    analysis["clarity_score"] = audio_features["clarity"]["score"]
    analysis["confidence_score"] = audio_features["confidence_score"]
    
    emotional_tone = audio_features.get("emotional_tone", "neutral")
    if "agitated" in emotional_tone or "stressed" in emotional_tone:
        analysis["tone_score"] = min(analysis["tone_score"], 4)
        analysis["issues"].append("🎙️ Voice sounds agitated/stressed")
    elif "calm" in emotional_tone:
        analysis["tone_score"] = max(analysis["tone_score"], 7)
        analysis["strengths"].append("🎙️ Calm vocal tone")
    elif "engaged" in emotional_tone or "enthusiastic" in emotional_tone:
        analysis["strengths"].append("🎙️ Engaged and enthusiastic voice")

analysis["overall_score"] = round(
    (analysis["tone_score"] + analysis["clarity_score"] + 
     analysis["confidence_score"] + analysis["empathy_score"]) / 4
)

# Generate coaching
coaching = []
rewritten = text

if "AGGRESSIVE" in analysis["style"]:
    coaching = [
        f"1️⃣ {user.name}, replace 'You always/never' with 'When [situation]...'",
        "2️⃣ Pause 3 seconds before responding when upset",
        "3️⃣ Focus on behavior, not the person's character",
        "4️⃣ Use format: 'I feel [emotion] when [situation] because [reason]'",
    ]
    rewritten = re.sub(r"\byou always\b", "when this happens, I feel", rewritten, flags=re.IGNORECASE)
    rewritten = re.sub(r"\byou never\b", "when this doesn't happen, I feel", rewritten, flags=re.IGNORECASE)
    
elif "PASSIVE" in analysis["style"]:
    coaching = [
        "1️⃣ Remove qualifiers: 'maybe' → state directly",
        "2️⃣ Only apologize when you've done something wrong",
        "3️⃣ Replace 'I guess' with 'I think' or 'I believe'",
        f"4️⃣ {user.name}, your needs matter - state them clearly!",
    ]
    rewritten = re.sub(r"\bi guess\b", "I think", rewritten, flags=re.IGNORECASE)
    rewritten = re.sub(r"\bmaybe we could\b", "I suggest we", rewritten, flags=re.IGNORECASE)
    
elif "ASSERTIVE" in analysis["style"]:
    coaching = [
        f"1️⃣ Excellent work, {user.name}! Your 'I' statements are effective",
        "2️⃣ To enhance: Add clarifying questions like 'What's your perspective?'",
        "3️⃣ Validate others: 'I hear what you're saying, and...'",
    ]

# Add audio-specific coaching
if audio_features and audio_features.get("status") == "success":
    audio_coaching = []
    
    if audio_features["volume"]["level"] == "loud":
        audio_coaching.append("🔊 Lower your volume slightly to sound less aggressive")
    elif audio_features["volume"]["level"] == "soft":
        audio_coaching.append("🔊 Speak louder to sound more confident")
    
    if audio_features["pace"]["level"] == "fast":
        audio_coaching.append("⏱️ Slow down your speech - take breaths between sentences")
    elif audio_features["pace"]["level"] == "slow":
        audio_coaching.append("⏱️ Increase pace slightly to maintain listener engagement")
    
    if audio_features["pitch"]["variety"] == "monotone":
        audio_coaching.append("🎵 Vary your pitch - emphasize key words for impact")
    
    if audio_features["clarity"]["level"] == "unclear":
        audio_coaching.append("🗣️ Enunciate clearly - open your mouth more when speaking")
    
    if audio_features["pauses"]["level"] == "many_long":
        audio_coaching.append("⏸️ Reduce long pauses - prepare your thoughts beforehand")
    elif audio_features["pauses"]["level"] == "few":
        audio_coaching.append("⏸️ Add strategic pauses to let ideas sink in")
    
    if audio_coaching:
        coaching.extend(["", "🎙️ VOCAL COACHING:"] + audio_coaching)

# Relationship tips
relationship_tips = {
    "boss": "💼 With your boss: Lead with solutions, not just problems. 'I noticed X, I suggest Y.'",
    "colleague": "🤝 With colleagues: Emphasize collaboration. 'How can we solve this together?'",
    "partner": "💕 With your partner: Choose calm moments, avoid discussing issues when tired.",
    "family": "👨‍👩‍👧 With family: Acknowledge their perspective first, then share yours.",
    "friend": "👋 With friends: Be direct but kind. Good friends appreciate honesty.",
}

# Update user stats
user.streaks["communication"] = user.streaks.get("communication", 0) + 1
user.total_points += 15
user.communication_history.append({
    "timestamp": time.time(),
    "score": analysis["overall_score"],
    "style": analysis["style"],
    "had_audio": audio_path is not None
})

# Build result
result = {
    "status": "analyzed",
    "original_message": text,
    "transcribed_from_audio": transcript is not None,
    "analysis": {
        "style": analysis["style"],
        "scores": {
            "tone": f"{analysis['tone_score']}/10",
            "clarity": f"{analysis['clarity_score']}/10",
            "confidence": f"{analysis['confidence_score']}/10",
            "empathy": f"{analysis['empathy_score']}/10",
            "overall": f"{analysis['overall_score']}/10"
        },
        "issues": analysis["issues"],
        "strengths": analysis["strengths"],
        "filler_words": analysis["filler_words"]
    },
    "coaching": coaching,
    "rewritten_message": rewritten if rewritten != text else None,
    "relationship_tip": relationship_tips.get(relationship, ""),
    "stats": {
        "streak": user.streaks["communication"],
        "points_earned": 15,
        "total_points": user.total_points
    }
}

if audio_features and audio_features.get("status") == "success":
    result["vocal_analysis"] = {
        "duration": f"{audio_features['duration_seconds']}s",
        "volume": {
            "level": audio_features["volume"]["level"],
            "note": audio_features["volume"]["note"],
            "score": f"{audio_features['volume']['score']}/10"
        },
        "pace": {
            "level": audio_features["pace"]["level"],
            "rate": f"{audio_features['pace']['syllables_per_sec']} syllables/sec",
            "note": audio_features["pace"]["note"],
            "score": f"{audio_features['pace']['score']}/10"
        },
        "pitch": {
            "level": audio_features["pitch"]["level"],
            "variety": audio_features["pitch"]["variety"],
            "note": audio_features["pitch"]["note"],
            "score": f"{audio_features['pitch']['score']}/10"
        },
        "clarity": {
            "level": audio_features["clarity"]["level"],
            "note": audio_features["clarity"]["note"],
            "score": f"{audio_features['clarity']['score']}/10"
        },
        "pauses": {
            "pattern": audio_features["pauses"]["level"],
            "average": f"{audio_features['pauses']['average_seconds']}s",
            "note": audio_features["pauses"]["note"]
        },
        "confidence_score": f"{audio_features['confidence_score']}/10",
        "emotional_tone": audio_features["emotional_tone"],
        "overall_vocal_score": f"{audio_features['overall_score']}/10"
    }
    result["message"] = f"🎙️ Analyzed {audio_features['duration_seconds']}s of speech with full vocal analysis!"

if rewritten != text:
    result["correction_example"] = f"\n❌ Original: '{text}'\n✅ Try: '{rewritten}'"

metric_inc("communication_analyses")
metric_time("interpersonal_coach", time.time() - start)

return result
============================================================================
AGENT 4: MEAL PLANNER
============================================================================
def analyze_food_image(image_path: str) -> Dict:
"""Use Gemini Vision to detect food items in image."""
try:
validation = safe_file_read(image_path, ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
if validation["status"] == "error":
return {"status": "error", "message": validation["error"], "items": []}
    try:
        image = Image.open(image_path)
        image.verify()
        image = Image.open(image_path)
    except Exception as img_err:
        return {
            "status": "error", 
            "message": f"Invalid image file: {str(img_err)}", 
            "items": []
        }
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    response = model.generate_content([
        "List all food items, ingredients, or groceries visible in this image. "
        "Return ONLY a comma-separated list. Example: chicken, rice, broccoli. "
        "If no food visible, return: none",
        image
    ])
    
    result_text = response.text.strip().lower()
    
    if result_text == "none" or not result_text:
        return {"status": "no_food", "items": []}
    
    items = [item.strip() for item in result_text.split(',') if item.strip()]
    return {"status": "success", "items": items}
    
except Exception as e:
    logger.error(f"Image analysis error: {e}\n{traceback.format_exc()}")
    return {
        "status": "error", 
        "message": f"Image processing failed: {str(e)}", 
        "items": []
    }
def plan_meals(
user_id: str,
ingredients: str = None,
image_path: str = None,
days: int = 3
) -> Dict:
"""
Create meal plans from ingredients (text or image).
Parameters:
- user_id: User identifier
- ingredients: Comma-separated list of ingredients
- image_path: Path to image of groceries/fridge
- days: Number of days to plan (1-7)

Returns: Meal plans with recipes
"""
from user_management import get_user
from metrics import metric_inc, metric_time

start = time.time()
user = get_user(user_id)
groceries = []
image_note = ""

# Process image
if image_path:
    logger.info(f"Processing food image: {image_path}")
    
    validation = safe_file_read(image_path, ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
    if validation["status"] == "error":
        return {
            "status": "error",
            "message": f"Image error: {validation['error']}"
        }
    
    image_result = analyze_food_image(image_path)
    
    if image_result["status"] == "success":
        groceries.extend(image_result["items"])
        image_note = f"📸 Detected from image: {', '.join(image_result['items'])}"
    elif image_result["status"] == "no_food":
        image_note = "📸 No food items detected in image"
    else:
        image_note = f"⚠️ Image error: {image_result.get('message', 'Unknown error')}"

# Process text ingredients
if ingredients:
    text_items = [g.strip().lower() for g in re.split(r'[,;]', ingredients) if len(g.strip()) > 2]
    groceries.extend(text_items)

groceries = list(set(groceries))

if not groceries:
    return {
        "status": "needs_input",
        "message": f"🍳 {user.name}, I need ingredients to plan meals!",
        "image_note": image_note if image_note else None,
        "options": [
            "📝 List ingredients: 'Meal plan: chicken, rice, broccoli'",
            "📸 Upload a photo of your fridge/groceries",
        ],
        "example": "Meal plan: chicken breast, rice, broccoli, eggs, onion"
    }

# Categorize ingredients
categories = {
    "proteins": ["chicken", "beef", "pork", "fish", "salmon", "tuna", "shrimp", "egg", "tofu", "turkey", "lamb"],
    "carbs": ["rice", "pasta", "bread", "potato", "noodle", "quinoa", "oat", "tortilla"],
    "vegetables": ["broccoli", "spinach", "carrot", "tomato", "onion", "pepper", "lettuce", "cucumber", "mushroom", "garlic", "celery", "cabbage"],
    "fruits": ["apple", "banana", "orange", "berry", "grape", "mango", "lemon"],
    "dairy": ["milk", "cheese", "yogurt", "butter", "cream"]
}

categorized = {cat: [] for cat in categories}
for g in groceries:
    for cat, keywords in categories.items():
        if any(k in g for k in keywords):
            categorized[cat].append(g)
            break

# Generate meal plans
meal_plans = []
days = min(max(1, days), 7)

for day in range(1, days + 1):
    day_meals = {"day": f"Day {day}", "meals": {}}
    
    # Breakfast
    if categorized["proteins"] or categorized["dairy"]:
        if "egg" in str(categorized["proteins"]):
            day_meals["meals"]["breakfast"] = {
                "dish": f"Scrambled eggs with {categorized['vegetables'][0] if categorized['vegetables'] else 'toast'}",
                "time": "15 min", "calories": "300-400"
            }
        elif categorized["dairy"]:
            day_meals["meals"]["breakfast"] = {
                "dish": f"Greek yogurt with {categorized['fruits'][0] if categorized['fruits'] else 'granola'}",
                "time": "5 min", "calories": "250-350"
            }
    
    # Lunch
    if categorized["proteins"] and categorized["vegetables"]:
        p = categorized["proteins"][day % len(categorized["proteins"])]
        v = categorized["vegetables"][day % len(categorized["vegetables"])]
        day_meals["meals"]["lunch"] = {
            "dish": f"Grilled {p} salad with {v}",
            "time": "20 min", "calories": "400-500"
        }
    
    # Dinner
    if categorized["proteins"]:
        p = categorized["proteins"][(day + 1) % len(categorized["proteins"])]
        c = categorized["carbs"][0] if categorized["carbs"] else "rice"
        v = categorized["vegetables"][(day + 1) % len(categorized["vegetables"])] if categorized["vegetables"] else "vegetables"
        day_meals["meals"]["dinner"] = {
            "dish": f"{p.title()} stir-fry with {c} and {v}",
            "time": "30 min", "calories": "500-600"
        }
    
    meal_plans.append(day_meals)

# Generate recipes
recipes = []

if "chicken" in str(groceries):
    recipes.append({
        "name": "🍗 Quick Chicken Stir-Fry",
        "time": "25 min",
        "servings": 4,
        "ingredients": [
            "2 chicken breasts, cubed",
            f"2 cups {categorized['vegetables'][0] if categorized['vegetables'] else 'mixed vegetables'}",
            f"1 cup {categorized['carbs'][0] if categorized['carbs'] else 'rice'}",
            "2 tbsp oil, 2 cloves garlic, 3 tbsp soy sauce"
        ],
        "steps": [
            "1️⃣ Cook rice/carbs according to package",
            "2️⃣ Heat oil in wok over high heat",
            "3️⃣ Add chicken, cook 6-8 min until golden",
            "4️⃣ Add garlic and vegetables, stir 4-5 min",
            "5️⃣ Add soy sauce, toss and serve over rice"
        ]
    })

if "egg" in str(groceries):
    recipes.append({
        "name": "🍳 Veggie Omelette",
        "time": "10 min",
        "servings": 1,
        "ingredients": [
            "3 eggs",
            f"1/4 cup diced {categorized['vegetables'][0] if categorized['vegetables'] else 'vegetables'}",
            "2 tbsp cheese, salt, pepper, 1 tbsp butter"
        ],
        "steps": [
            "1️⃣ Beat eggs with salt and pepper",
            "2️⃣ Melt butter in pan over medium heat",
            "3️⃣ Pour eggs, let set 1-2 min",
            "4️⃣ Add veggies and cheese to half",
            "5️⃣ Fold and serve"
        ]
    })

# Shopping suggestions
missing = []
if not categorized["proteins"]: missing.append("protein (chicken, fish, eggs, tofu)")
if not categorized["carbs"]: missing.append("carbs (rice, pasta, bread)")
if not categorized["vegetables"]: missing.append("vegetables")

# Update stats
user.streaks["nutrition"] = user.streaks.get("nutrition", 0) + 1
user.total_points += 25

metric_inc("meal_plans")
metric_time("meal_planner", time.time() - start)

return {
    "status": "complete",
    "ingredients_found": groceries,
    "categories": {k: v for k, v in categorized.items() if v},
    "meal_plans": meal_plans,
    "recipes": recipes,
    "days_planned": days,
    "shopping_suggestions": missing,
    "image_analysis": image_note if image_note else None,
    "stats": {
        "streak": user.streaks["nutrition"],
        "points_earned": 25,
        "total_points": user.total_points
    }
}
============================================================================
AGENT 5: TASK PLANNER
============================================================================
def plan_tasks(user_id: str, tasks_text: str) -> Dict:
"""
Organize and prioritize tasks with time estimates.
Parameters:
- user_id: User identifier
- tasks_text: Comma-separated list of tasks

Returns: Prioritized task list with estimates
"""
from user_management import get_user
from metrics import metric_inc, metric_time

start = time.time()
user = get_user(user_id)

# Parse tasks
tasks = [t.strip() for t in re.split(r'[,;]', tasks_text) if len(t.strip()) > 2]

if not tasks:
    return {
        "status": "needs_input",
        "message": f"📋 {user.name}, please list your tasks!",
        "example": "Tasks: finish report, call client, workout, send emails"
    }

# Analyze and schedule
scheduled = []
total_time = 0

time_estimates = {
    "quick": (["call", "email", "text", "message", "reply"], 15),
    "medium": (["meeting", "review", "check", "update"], 30),
    "long": (["write", "report", "presentation", "project", "analysis"], 60),
    "extended": (["research", "develop", "build", "create", "design"], 90)
}

for i, task in enumerate(tasks):
    lower = task.lower()
    
    # Estimate time
    est = 30
    for duration, (keywords, minutes) in time_estimates.items():
        if any(k in lower for k in keywords):
            est = minutes
            break
    
    # Calculate priority
    priority = 10 - i
    if any(w in lower for w in ["urgent", "asap", "important", "deadline", "critical"]):
        priority += 5
    if any(w in lower for w in ["optional", "maybe", "if time"]):
        priority -= 3
    
    scheduled.append({
        "task": task,
        "estimate_min": est,
        "priority": max(1, min(15, priority)),
        "category": "urgent" if priority > 10 else "normal" if priority > 5 else "low"
    })
    total_time += est

# Sort by priority
scheduled.sort(key=lambda x: x["priority"], reverse=True)

# Generate strategy
if total_time > 240:
    strategy = "🍅 Pomodoro Technique: 25 min focused work → 5 min break → repeat"
    motivation = f"{user.name}, that's {total_time//60}+ hours of work. Break it into sessions!"
elif total_time > 120:
    strategy = "📅 Time Blocking: Schedule 90-min focus blocks with 15-min breaks"
    motivation = f"Solid list! About {total_time//60} hours. You've got this!"
else:
    strategy = "⚡ Batch Processing: Group similar tasks together"
    motivation = f"Quick wins ahead! About {total_time} minutes total."

# Update stats
user.streaks["tasks"] = user.streaks.get("tasks", 0) + 1
user.total_points += 15

metric_inc("tasks_planned")
metric_time("task_planner", time.time() - start)

return {
    "status": "planned",
    "tasks": scheduled,
    "summary": {
        "total_tasks": len(scheduled),
        "total_time": f"{total_time//60}h {total_time%60}m" if total_time >= 60 else f"{total_time}m",
        "urgent_tasks": len([t for t in scheduled if t["category"] == "urgent"]),
    },
    "top_3_priorities": [t["task"] for t in scheduled[:3]],
    "strategy": strategy,
    "motivation": motivation,
    "stats": {
        "streak": user.streaks["tasks"],
        "points_earned": 15,
        "total_points": user.total_points
    }
}
============================================================================
AGENT 6: NUTRITION ADVISOR
============================================================================
def get_nutrition_advice(user_id: str, goal: str) -> Dict:
"""
Provide nutrition advice based on wellness goals.
Parameters:
- user_id: User identifier
- goal: User's goal or concern (stress, energy, weight, sleep, etc.)

Returns: Personalized nutrition guidance
"""
from user_management import get_user
from metrics import metric_inc, metric_time

start = time.time()
user = get_user(user_id)
lower = goal.lower()

advice_db = {
    "stress": {
        "keywords": ["stress", "anxiety", "anxious", "calm", "relax", "nervous"],
        "goal_name": "Stress Management",
        "foods": ["Dark chocolate (85%+)", "Walnuts", "Salmon", "Blueberries", "Green tea", "Chamomile tea"],
        "tips": [
            "🍫 Magnesium in dark chocolate helps reduce cortisol",
            "🐟 Omega-3s in salmon reduce inflammation and anxiety",
            "🫖 L-theanine in green tea promotes calm without drowsiness",
            "🥜 B-vitamins in nuts support nervous system health"
        ],
        "avoid": ["Excessive caffeine", "Alcohol", "Refined sugars", "Processed foods"]
    },
    "energy": {
        "keywords": ["energy", "tired", "fatigue", "exhausted", "sluggish", "alert"],
        "goal_name": "Energy Boost",
        "foods": ["Oatmeal", "Eggs", "Bananas", "Greek yogurt", "Almonds", "Sweet potato"],
        "tips": [
            "🥚 Protein at breakfast sustains energy all morning",
            "🍌 Complex carbs provide steady fuel without crashes",
            "💧 Dehydration is a major cause of fatigue - drink more water!",
            "🥜 Healthy fats keep you satisfied and energized"
        ],
        "avoid": ["Sugar-heavy breakfast", "Skipping meals", "Energy drinks", "Large heavy lunches"]
    },
    "sleep": {
        "keywords": ["sleep", "insomnia", "rest", "tired at night", "can't sleep"],
        "goal_name": "Better Sleep",
        "foods": ["Cherries", "Warm milk", "Turkey", "Kiwi", "Almonds", "Chamomile tea"],
        "tips": [
            "🍒 Cherries are natural source of melatonin",
            "🥛 Warm milk contains tryptophan for relaxation",
            "🥝 Two kiwis before bed improves sleep quality",
            "⏰ Avoid eating 2-3 hours before bedtime"
        ],
        "avoid": ["Caffeine after 2pm", "Alcohol before bed", "Heavy/spicy dinners", "Chocolate at night"]
    },
    "weight": {
        "keywords": ["weight", "diet", "lose", "fat", "calories", "slim"],
        "goal_name": "Weight Management",
        "foods": ["Lean proteins", "Leafy greens", "Berries", "Legumes", "Whole grains", "Greek yogurt"],
        "tips": [
            "🥗 Fill half your plate with vegetables",
            "🍗 Protein keeps you full longer - include at every meal",
            "⏱️ Eat slowly - it takes 20 min to feel full",
            "💧 Drink water before meals to reduce overeating"
        ],
        "avoid": ["Liquid calories", "Processed snacks", "Large portions", "Eating while distracted"]
    },
    "focus": {
        "keywords": ["focus", "concentrate", "brain", "memory", "think", "mental"],
        "goal_name": "Mental Focus",
        "foods": ["Fatty fish", "Blueberries", "Eggs", "Broccoli", "Pumpkin seeds", "Dark chocolate"],
        "tips": [
            "🐟 DHA in fatty fish is essential for brain function",
            "🫐 Antioxidants in blueberries improve memory",
            "🥚 Choline in eggs supports neurotransmitter production",
            "🥦 Vitamin K in broccoli enhances cognitive function"
        ],
        "avoid": ["Excessive sugar", "Trans fats", "Alcohol", "Highly processed foods"]
    }
}

# Find matching goal
selected = None
for key, data in advice_db.items():
    if any(kw in lower for kw in data["keywords"]):
        selected = data
        break

# Default to general wellness
if not selected:
    selected = {
        "goal_name": "General Wellness",
        "foods": ["Colorful vegetables", "Lean proteins", "Whole grains", "Healthy fats", "Water"],
        "tips": [
            "🌈 Eat the rainbow - variety ensures all nutrients",
            "🥩 Include protein at every meal",
            "💧 Aim for 8 glasses of water daily",
            "🍽️ Practice mindful eating - no screens at meals"
        ],
        "avoid": ["Processed foods", "Excessive sugar", "Trans fats", "Skipping meals"]
    }

# Update stats
user.total_points +=SVContinue10
metric_inc("nutrition_advice")
metric_time("nutrition_agent", time.time() - start)

return {
    "status": "success",
    "goal": selected["goal_name"],
    "recommended_foods": selected["foods"],
    "tips": selected["tips"],
    "foods_to_limit": selected.get("avoid", []),
    "quick_meal": f"Try: {selected['foods'][0]} + {selected['foods'][1]} for your next meal",
    "stats": {
        "points_earned": 10,
        "total_points": user.total_points
    },
    "encouragement": f"{user.name}, small changes lead to big results! 💪"
}
============================================================================
AGENT 7: SUMMARIZER
============================================================================
def extract_from_url(url: str) -> Dict:
"""Extract text from URL."""
try:
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
response = requests.get(url, headers=headers, timeout=15)
response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    main = soup.find('main') or soup.find('article') or soup.find('body')
    paragraphs = main.find_all(['p', 'h1', 'h2', 'h3', 'li']) if main else []
    text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
    
    title = soup.find('title')
    
    return {
        "status": "success", "type": "url", "source": url,
        "title": title.get_text().strip() if title else "Untitled",
        "content": text[:15000], "word_count": len(text.split())
    }
except Exception as e:
    return {"status": "error", "message": str(e)}
def extract_from_pdf(pdf_path: str) -> Dict:
"""Extract text from PDF."""
try:
validation = safe_file_read(pdf_path, ['.pdf'])
if validation["status"] == "error":
return {"status": "error", "message": validation["error"]}
    text = ""
    with open(pdf_path, 'rb') as f:
        try:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            
            if num_pages == 0:
                return {"status": "error", "message": "PDF has no pages"}
            
            for i, page in enumerate(reader.pages[:50]):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as page_err:
                    logger.warning(f"Could not extract page {i}: {page_err}")
                    continue
            
            if not text.strip():
                return {"status": "error", "message": "Could not extract any text from PDF"}
            
            return {
                "status": "success", 
                "type": "pdf", 
                "source": pdf_path,
                "content": text[:15000], 
                "word_count": len(text.split()),
                "pages": min(num_pages, 50)
            }
        except Exception as read_err:
            return {"status": "error", "message": f"PDF reading error: {str(read_err)}"}
            
except Exception as e:
    logger.error(f"PDF extraction error: {e}\n{traceback.format_exc()}")
    return {"status": "error", "message": f"PDF processing failed: {str(e)}"}
def summarize_content(
user_id: str,
text: str = None,
url: str = None,
pdf_path: str = None,
output_format: str = "all"
) -> Dict:
"""
Enhanced summarizer supporting TEXT, URL, and PDF.
Parameters:
- user_id: User identifier
- text: Text to analyze
- url: URL to fetch and summarize
- pdf_path: Path to PDF file
- output_format: "summary", "quiz", "findings", "mindmap", "all"

Returns: Comprehensive analysis with AI-generated insights
"""
from user_management import get_user
from metrics import metric_inc, metric_time

start = time.time()
user = get_user(user_id)

# Extract content
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
        "message": f"📄 {user.name}, I can summarize content in these formats:",
        "supported_formats": [
            "✅ Direct text (paste or type)",
            "✅ URL (any website)",
            "✅ PDF (documents up to 50 pages)"
        ],
        "examples": [
            "Summarize: [paste your text here]",
            "Summarize: https://example.com/article",
            "Upload a PDF file"
        ]
    }

if extracted.get("status") == "error":
    return extracted

content = extracted["content"]
word_count = extracted.get("word_count", 0)
reading_time = max(1, word_count // 200)

# Use Gemini for AI summarization
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""Analyze this content comprehensively. Return ONLY valid JSON:
{{
"summary": "3-4 sentence summary",
"key_points": ["point1", "point2", "point3", "point4", "point5"],
"action_items": ["actionable task 1", "actionable task 2"],
"key_entities": {{
"people": ["person1", "person2"],
"organizations": ["org1", "org2"],
"locations": ["place1", "place2"]
}},
"sentiment": "positive/negative/neutral/mixed",
"main_topics": ["topic1", "topic2", "topic3"],
"difficulty_level": "easy/moderate/complex",
"mind_map": {{
"central_topic": "main topic",
"branches": ["subtopic1", "subtopic2", "subtopic3"]
}},
"quiz": [
{{"question": "What is the main idea?", "options": ["A) Option", "B) Option", "C) Option", "D) Option"], "answer": "A"}},
{{"question": "According to the text...", "options": ["A) Option", "B) Option", "C) Option", "D) Option"], "answer": "C"}}
],
"key_findings": ["finding1", "finding2", "finding3"]
}}
Content: {content[:8000]}"""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=2048,
            temperature=0.3
        )
    )
    response_text = response.text.strip()
    
    # Clean JSON
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0]
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0]
    
    response_text = response_text.strip()
    
    try:
        ai_result = json.loads(response_text)
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error: {je}")
        raise Exception("Invalid JSON from AI")
    
except Exception as e:
    logger.error(f"AI summarization failed: {e}")
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    
    ai_result = {
        "summary": '. '.join(sentences[:3]) + '.',
        "key_points": sentences[:5],
        "main_topics": ["General content"],
        "sentiment": "neutral",
        "difficulty_level": "moderate",
        "quiz": [],
        "key_findings": sentences[:3],
        "action_items": [],
        "error_note": "Using fallback analysis"
    }

# Build result
result = {
    "status": "complete",
    "source_type": extracted.get("type"),
    "source": extracted.get("source", "text input"),
    "metadata": {
        "word_count": word_count,
        "reading_time": f"{reading_time} min",
        "processing_time": f"{time.time() - start:.2f}s",
        "difficulty": ai_result.get("difficulty_level", "moderate"),
        "sentiment": ai_result.get("sentiment", "neutral")
    }
}

# Add content based on format
if output_format in ["summary", "all"]:
    result["summary"] = ai_result.get("summary")
    result["key_points"] = ai_result.get("key_points", [])
    result["main_topics"] = ai_result.get("main_topics", [])

if output_format in ["quiz", "all"]:
    result["quiz"] = ai_result.get("quiz", [])

if output_format in ["findings", "all"]:
    result["key_findings"] = ai_result.get("key_findings", [])

if output_format in ["mindmap", "all"]:
    result["mind_map"] = ai_result.get("mind_map", {})

if output_format in ["all"]:
    result["action_items"] = ai_result.get("action_items", [])
    result["key_entities"] = ai_result.get("key_entities", {})

# Update stats
user.total_points += 30

docs_processed = user.game_scores.get("docs_processed", 0) + 1
user.game_scores["docs_processed"] = docs_processed

if docs_processed == 5 and "📚 Knowledge Seeker" not in user.badges:
    user.badges.append("📚 Knowledge Seeker")
    result["new_badge"] = "📚 Knowledge Seeker"
elif docs_processed == 20 and "📚📚 Research Master" not in user.badges:
    user.badges.append("📚📚 Research Master")
    result["new_badge"] = "📚📚 Research Master"

metric_inc("summaries")
metric_time("summarizer", time.time() - start)

result["stats"] = {
    "points_earned": 30,
    "total_points": user.total_points,
    "documents_processed": docs_processed
}

return result
