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
        # Avoid repeating recent games
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

print("✅ Agent 2: Stress Buster ready")
