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

print("✅ Agent 1: Mood Agent ready")

