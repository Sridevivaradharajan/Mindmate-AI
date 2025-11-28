def get_nutrition_advice(user_id: str, goal: str) -> Dict:
    """
    Provide nutrition advice based on wellness goals.
    
    Parameters:
    - user_id: User identifier
    - goal: User's goal or concern (stress, energy, weight, sleep, etc.)
    
    Returns: Personalized nutrition guidance
    """
    start = time.time()
    user = get_user(user_id)
    lower = goal.lower()
    
    # Detect goal from text
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
    
    # Update user stats
    user.total_points += 10
    
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

print("✅ Agent 6: Nutrition Advisor ready")
