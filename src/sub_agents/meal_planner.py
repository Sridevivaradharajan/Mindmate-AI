def analyze_food_image(image_path: str) -> Dict:
    """Use Gemini Vision to detect food items in image with robust error handling."""
    try:
        # CHANGE 1: Add validation first
        validation = safe_file_read(image_path, ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
        if validation["status"] == "error":
            return {"status": "error", "message": validation["error"], "items": []}
        
        # CHANGE 2: Add image verification
        try:
            image = Image.open(image_path)
            image.verify()  # Verify it's actually an image
            image = Image.open(image_path)  # Reopen after verify
        except Exception as img_err:
            return {
                "status": "error", 
                "message": f"Invalid image file: {str(img_err)}", 
                "items": []
            }
        
        # Rest remains the same
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
        logger.error(f"Image analysis error: {e}\n{traceback.format_exc()}")  # CHANGE 3: Add traceback
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
    start = time.time()
    user = get_user(user_id)
    groceries = []
    image_note = ""
    
    # Process image if provided
    if image_path:
        logger.info(f"Processing food image: {image_path}")
        
        # CHANGE: Add validation before analysis
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
    
    # Remove duplicates
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
    days = min(max(1, days), 7)  # Clamp 1-7
    
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
    
    # Generate detailed recipes
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
    
    # Update user stats
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

print("✅ Agent 4: Meal Planner ready")
