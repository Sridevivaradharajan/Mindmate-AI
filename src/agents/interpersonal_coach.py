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
        
        # Volume contributes
        if volume_level == "moderate": confidence_score += 2
        elif volume_level == "loud": confidence_score += 1
        elif volume_level == "soft": confidence_score -= 2
        
        # Pace contributes
        if pace_level == "moderate": confidence_score += 2
        elif pace_level == "fast": confidence_score -= 1
        elif pace_level == "slow": confidence_score -= 1
        
        # Pitch variety contributes
        if pitch_variety == "expressive": confidence_score += 2
        elif pitch_variety == "monotone": confidence_score -= 2
        
        # Clarity contributes
        if clarity_level == "clear": confidence_score += 2
        elif clarity_level == "unclear": confidence_score -= 2
        
        # Pauses contribute
        if pause_level == "natural": confidence_score += 1
        elif pause_level == "many_long": confidence_score -= 2
        
        confidence_score = max(1, min(10, confidence_score))
        
        # 7. EMOTIONAL TONE DETECTION (basic)
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
    start = time.time()
    user = get_user(user_id)
    
    # Audio analysis
    transcript = None
    audio_features = None
    
    if audio_path:
        try:
            # ============================================================
            # CHANGE 1: Add file validation
            # ============================================================
            valid_audio_extensions = ['.wav', '.mp3', '.m4a', '.mp4', '.ogg', '.flac']
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext not in valid_audio_extensions:
                return {
                    "status": "error",
                    "message": f"Unsupported audio format: {file_ext}. Please upload: WAV, MP3, M4A, MP4, OGG, or FLAC"
                }
            
            # Check if file exists and is readable
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
            
            # File size limit (50MB)
            if os.path.getsize(audio_path) > 50 * 1024 * 1024:
                size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                return {
                    "status": "error",
                    "message": f"Audio file too large ({size_mb:.1f}MB). Maximum size is 50MB."
                }
            
            recognizer = sr.Recognizer()
            
            # ============================================================
            # CHANGE 2: Improved audio conversion with better error handling
            # ============================================================
            if not audio_path.endswith('.wav'):
                try:
                    from pydub import AudioSegment
                    import tempfile
                    
                    logger.info(f"Converting audio file: {audio_path} ({file_ext})")
                    
                    # Load audio file
                    audio = AudioSegment.from_file(audio_path)
                    
                    # Create temporary wav file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                        wav_path = tmp.name
                    
                    # Export to WAV format
                    audio.export(wav_path, format="wav")
                    audio_path = wav_path
                    
                    logger.info(f"Audio converted successfully to: {wav_path}")
                    
                except Exception as e:
                    logger.error(f"Audio conversion failed: {e}\n{traceback.format_exc()}")
                    
                    # Provide helpful error message
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
            
            # ============================================================
            # STEP 1: Transcribe speech to text
            # ============================================================
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
            
            # ============================================================
            # STEP 2: Analyze vocal features (tone, pace, clarity, etc.)
            # ============================================================
            audio_features = analyze_audio_features(audio_path)
            
            if audio_features.get("status") == "error":
                logger.warning(f"Audio feature analysis failed: {audio_features.get('message')}")
                # Continue with just transcription, don't fail completely
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
    
    # ========== PATTERN DETECTION ==========
    
    # Aggressive patterns
    aggressive = {
        r"\byou always\b": "Absolute blame ('you always')",
        r"\byou never\b": "Absolute blame ('you never')",
        r"\byou should\b": "Commanding tone",
        r"\bwhy didn'?t you\b": "Accusatory question",
        r"\bwhat'?s wrong with you\b": "Personal attack",
        r"\byou need to\b": "Demanding language",
        r"\byou'?re (being )?(stupid|lazy|useless)\b": "Direct insult",
    }
    
    # Passive patterns
    passive = {
        r"\bmaybe we could\b": "Overly tentative",
        r"\bi guess\b": "Lacks confidence",
        r"\bsorry,? but\b": "Unnecessary apologizing",
        r"\bif that'?s okay\b": "Excessive permission-seeking",
        r"\bjust think\b": "'Just' minimizes your opinion",
        r"\bi'?m no expert\b": "Self-deprecating",
        r"\bkind of\b|\bsort of\b": "Hedging language",
    }
    
    # Assertive patterns (positive!)
    assertive = {
        r"\bi feel\b.*\bwhen\b": "✅ Great 'I feel when' statement!",
        r"\bi think\b": "✅ Owning your opinion",
        r"\bi believe\b": "✅ Confident stance",
        r"\bi need\b": "✅ Clear need expression",
        r"\bi'?d like\b": "✅ Polite but direct",
        r"\blet'?s\b": "✅ Collaborative language",
        r"\bwhat do you think\b": "✅ Inviting dialogue",
    }
    
    # Empathetic patterns (positive!)
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
    
    # Check filler words in TEXT
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
    
    # Adjust clarity for fillers (text-based)
    analysis["clarity_score"] = max(3, 10 - len(found_fillers) * 2)
    
    # IF AUDIO: Override scores with vocal analysis
    if audio_features and audio_features.get("status") == "success":
        # Use audio analysis for clarity, confidence, tone
        analysis["clarity_score"] = audio_features["clarity"]["score"]
        analysis["confidence_score"] = audio_features["confidence_score"]
        
        # Adjust tone based on emotional tone from voice
        emotional_tone = audio_features.get("emotional_tone", "neutral")
        if "agitated" in emotional_tone or "stressed" in emotional_tone:
            analysis["tone_score"] = min(analysis["tone_score"], 4)
            analysis["issues"].append("🎙️ Voice sounds agitated/stressed")
        elif "calm" in emotional_tone:
            analysis["tone_score"] = max(analysis["tone_score"], 7)
            analysis["strengths"].append("🎙️ Calm vocal tone")
        elif "engaged" in emotional_tone or "enthusiastic" in emotional_tone:
            analysis["strengths"].append("🎙️ Engaged and enthusiastic voice")
    
    # Overall score
    analysis["overall_score"] = round(
        (analysis["tone_score"] + analysis["clarity_score"] + 
         analysis["confidence_score"] + analysis["empathy_score"]) / 4
    )
    
    # ========== GENERATE COACHING ==========
    
    coaching = []
    rewritten = text
    
    if "AGGRESSIVE" in analysis["style"]:
        coaching = [
            f"1️⃣ {user.name}, replace 'You always/never' with 'When [situation]...'",
            "2️⃣ Pause 3 seconds before responding when upset",
            "3️⃣ Focus on behavior, not the person's character",
            "4️⃣ Use format: 'I feel [emotion] when [situation] because [reason]'",
        ]
        # Rewrite aggressive message
        rewritten = re.sub(r"\byou always\b", "when this happens, I feel", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\byou never\b", "when this doesn't happen, I feel", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\byou should\b", "I'd appreciate if you could", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\bwhy didn'?t you\b", "I noticed", rewritten, flags=re.IGNORECASE)
        
    elif "PASSIVE" in analysis["style"]:
        coaching = [
            "1️⃣ Remove qualifiers: 'maybe' → state directly",
            "2️⃣ Only apologize when you've done something wrong",
            "3️⃣ Replace 'I guess' with 'I think' or 'I believe'",
            f"4️⃣ {user.name}, your needs matter - state them clearly!",
        ]
        rewritten = re.sub(r"\bi guess\b", "I think", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\bmaybe we could\b", "I suggest we", rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\bsorry,? but\b", "", rewritten, flags=re.IGNORECASE)
        
    elif "ASSERTIVE" in analysis["style"]:
        coaching = [
            f"1️⃣ Excellent work, {user.name}! Your 'I' statements are effective",
            "2️⃣ To enhance: Add clarifying questions like 'What's your perspective?'",
            "3️⃣ Validate others: 'I hear what you're saying, and...'",
        ]
    
    # ADD AUDIO-SPECIFIC COACHING
    if audio_features and audio_features.get("status") == "success":
        audio_coaching = []
        
        # Volume coaching
        if audio_features["volume"]["level"] == "loud":
            audio_coaching.append("🔊 Lower your volume slightly to sound less aggressive")
        elif audio_features["volume"]["level"] == "soft":
            audio_coaching.append("🔊 Speak louder to sound more confident")
        
        # Pace coaching
        if audio_features["pace"]["level"] == "fast":
            audio_coaching.append("⏱️ Slow down your speech - take breaths between sentences")
        elif audio_features["pace"]["level"] == "slow":
            audio_coaching.append("⏱️ Increase pace slightly to maintain listener engagement")
        
        # Pitch coaching
        if audio_features["pitch"]["variety"] == "monotone":
            audio_coaching.append("🎵 Vary your pitch - emphasize key words for impact")
        
        # Clarity coaching
        if audio_features["clarity"]["level"] == "unclear":
            audio_coaching.append("🗣️ Enunciate clearly - open your mouth more when speaking")
        
        # Pause coaching
        if audio_features["pauses"]["level"] == "many_long":
            audio_coaching.append("⏸️ Reduce long pauses - prepare your thoughts beforehand")
        elif audio_features["pauses"]["level"] == "few":
            audio_coaching.append("⏸️ Add strategic pauses to let ideas sink in")
        
        if audio_coaching:
            coaching.extend(["", "🎙️ VOCAL COACHING:"] + audio_coaching)
    
    # Relationship-specific tips
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
    
    # Add audio analysis if available
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

print("✅ Agent 3: Interpersonal Coach with FULL audio analysis ready")
