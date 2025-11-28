def plan_tasks(user_id: str, tasks_text: str) -> Dict:
    """
    Organize and prioritize tasks with time estimates.
    
    Parameters:
    - user_id: User identifier
    - tasks_text: Comma-separated list of tasks
    
    Returns: Prioritized task list with estimates
    """
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
    
    # Analyze and schedule tasks
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
        est = 30  # default
        for duration, (keywords, minutes) in time_estimates.items():
            if any(k in lower for k in keywords):
                est = minutes
                break
        
        # Calculate priority
        priority = 10 - i  # Base priority by order
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
    if total_time > 240:  # > 4 hours
        strategy = "🍅 Pomodoro Technique: 25 min focused work → 5 min break → repeat"
        motivation = f"{user.name}, that's {total_time//60}+ hours of work. Break it into sessions!"
    elif total_time > 120:  # > 2 hours
        strategy = "📅 Time Blocking: Schedule 90-min focus blocks with 15-min breaks"
        motivation = f"Solid list! About {total_time//60} hours. You've got this!"
    else:
        strategy = "⚡ Batch Processing: Group similar tasks together"
        motivation = f"Quick wins ahead! About {total_time} minutes total."
    
    # Update user stats
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

print("✅ Agent 5: Task Planner ready")
