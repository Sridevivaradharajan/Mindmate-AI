# MindMate AI - Personal Wellness Agent System

Capstone submission for Google's 5-Day AI Agents Intensive Course (Concierge Agents Track)

---

## Problem Statement

Mental wellness support is fragmented and inaccessible. Professional therapy costs $100-300 per session with weeks-long waiting lists. Users juggle multiple apps for mood tracking, meal planning, and stress management. Traditional solutions lack immediate availability when support is needed most.

Twenty percent of adults face mental health challenges annually, 70% of workplace conflicts stem from poor communication, and 60% resort to unhealthy eating due to decision fatigue. An integrated, immediate, and cost-effective solution is needed.

---

## Solution

MindMate AI is a multi-agent wellness system providing immediate support across seven domains through a unified interface. The system sees (analyzes food photos), hears (vocal tone analysis), and remembers (tracks your last 20 emotional check-ins).

Key capabilities:
- 24/7 availability with instant responses
- Seven specialized agents sharing user context
- Persistent memory tracking emotional patterns and trends
- Multimodal processing (text, audio, images, documents)
- Proactive interventions when wellness patterns decline

---

## Architecture

MindMate uses a sequential multi-agent pattern. A central orchestrator powered by Gemini 2.5 Flash analyzes user intent and routes requests to specialized sub-agents. Each agent is implemented as an ADK FunctionTool with comprehensive error handling.

**Flow**: User Input → Central Orchestrator → Specialized Agent → User Journey State → Response

**Core Components**:
- Central orchestrator for intelligent routing
- Seven specialized sub-agents as FunctionTools
- InMemorySessionService for session persistence
- UserJourney dataclass maintaining user state

---

## The Seven Agents

### 1. Mood Analysis Agent
Analyzes emotional state using 27 keywords, assigns mood scores (1-10), tracks last 20 check-ins, calculates trends (improving/declining/stable), and provides coping strategies. Automatically triggers stress relief when mood drops below threshold.

### 2. Stress Relief Agent
Delivers mental break games across five categories: riddles, trivia, brain teasers, patterns, and detective mysteries. Anti-repetition algorithm ensures variety. Tracks streaks and unlocks achievement badges.

### 3. Communication Coach Agent
**Text Mode**: Detects 40+ communication patterns (aggressive/passive/assertive), scores tone/clarity/confidence/empathy, rewrites messages, provides behavioral coaching.

**Audio Mode**: Transcribes speech and analyzes volume, pace, pitch, clarity, pauses, confidence (1-10), and emotional tone using librosa acoustic analysis. Supports WAV, MP3, M4A, MP4, OGG, FLAC formats.

### 4. Meal Planning Agent
Accepts text ingredients or food photographs. Uses Gemini Vision API to detect food items. Generates 1-7 day meal plans with recipes, prep times, calories, and shopping lists.

### 5. Task Organization Agent
Parses task lists, estimates completion times (15-90 min), assigns priorities, and recommends productivity strategies: Pomodoro (4+ hours), Time Blocking (2-4 hours), or Batch Processing (under 2 hours).

### 6. Nutrition Advisory Agent
Maps wellness goals (stress, energy, sleep, weight, focus) to evidence-based food recommendations with scientific rationale. Provides foods to limit and meal suggestions.

### 7. Content Analysis Agent
Processes text, URLs, and PDFs (up to 50 pages). Generates summaries, key points, quiz questions, mind maps, sentiment analysis, and reading time estimates using Gemini 2.5 Flash.

---

## Key Technical Features

**Multi-Agent System**: One orchestrator coordinating seven specialized sub-agents through sequential flow

**Custom Tools**: Seven FunctionTools with defensive error handling and graceful degradation

**Sessions & Memory**: InMemorySessionService manages sessions. UserJourney dataclass stores emotional history, stress patterns, streaks, badges, and points across sessions.

**Observability**: Tracks nine metrics (mood analyses, games played, meal plans, etc.) with per-agent latency monitoring

**Error Handling**: Comprehensive file validation (existence, type, size, corruption), user-friendly error messages, and fallback mechanisms

---

## Gamification

Points awarded per activity: Mood check-in (5), Stress game (10), Nutrition advice (10), Communication analysis (15), Task planning (15), Meal planning (25), Document summary (30).

Achievement badges unlock at milestones: Game Starter (5 games), Game Master (20 games), Knowledge Seeker (5 documents), Research Master (20 documents).

Daily streaks tracked per agent type to maintain engagement.

---

## Technical Stack

**AI**: Google Gemini 2.5 Flash, Gemini Vision API, Google ADK

**Audio**: SpeechRecognition, librosa, pydub, soundfile

**Documents**: PyPDF2, BeautifulSoup4, requests

**Core**: Pillow, dataclasses, asyncio

---

## Usage

**Chat Interface**: Natural language conversation for all agents. Example: "I'm feeling anxious" or "Meal plan: chicken, rice, broccoli"

**Direct Functions**: Programmatic access with explicit parameters. Example: analyze_mood(user_id, message, stress_level)

**File Uploads**: Interactive widgets for images, audio recordings, and documents in Jupyter environment

---

## Limitations

- Memory resets on notebook restart (in-memory only)
- DOCX/IPYNB formats excluded (unreliable extraction)
- FFmpeg required for audio processing
- 50MB file size limit
- English-only interface

---

## Value Statement

MindMate AI provides immediate, comprehensive wellness support at zero cost. By consolidating seven specialized functions into a unified interface with persistent memory and proactive interventions, it eliminates the fragmentation and cost barriers preventing individuals from accessing mental health support.

---

Built with Google's Agent Development Kit as part of the 5-Day AI Agents Intensive Course.
