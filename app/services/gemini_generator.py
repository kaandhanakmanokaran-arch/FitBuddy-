from ..config import get_settings
from ..safety import safety_context
from .gemini_client import get_client


def demo_workout(username: str, goal: str, intensity: str) -> str:
    return f"""7-Day FitBuddy Demo Plan for {username}
Goal: {goal}
Intensity: {intensity}

Day 1 — Full Body Foundation
Warm-up: 5–10 minutes of comfortable movement.
Main: Bodyweight squat 2×8–12, incline push-up 2×6–12, glute bridge 2×10–15, easy walk 10 minutes.
Cooldown: Gentle mobility and relaxed breathing.

Day 2 — Cardio + Mobility
Warm-up: 5 minutes easy walking.
Main: Comfortable cardio 20–25 minutes with breaks as needed; mobility for hips, shoulders and ankles.
Cooldown: 5 minutes easy movement.

Day 3 — Recovery
Easy walk or other enjoyable light movement for 15–30 minutes.
Add gentle stretching if comfortable.

Day 4 — Strength Basics
Warm-up: 5–10 minutes.
Main: Sit-to-stand 2×8–12, wall push-up 2×8–12, bird-dog 2×6 each side.
Cooldown: Gentle mobility.

Day 5 — Cardio + Core
Warm-up: 5 minutes.
Main: Comfortable cardio 15–25 minutes; dead bug 2×6–10 each side; side plank from knees 2×10–20 seconds if comfortable.
Cooldown: Easy breathing and mobility.

Day 6 — Full Body Variety
Choose 3–4 comfortable movements from earlier days and keep the session easy to moderate.

Day 7 — Rest / Active Recovery
Rest, or take an easy walk and do gentle mobility.

Adjust or stop any movement that causes pain. This demo is for software testing and is not medical advice."""


def generate_workout_gemini(user) -> tuple[str, str]:
    settings = get_settings()
    client = get_client()
    if client is None:
        return demo_workout(user.username, user.goal, user.intensity), "demo"

    prompt = f"""
Create a safe, practical 7-day general fitness plan.

User:
- Name: {user.username}
- Age: {user.age}
- Weight: {user.weight} kg
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

{safety_context(user.age, user.goal)}

Return exactly 7 labeled days. For each day include:
1. Focus
2. Warm-up
3. Main activity with exercise names and beginner-friendly sets/reps or durations
4. Rest/recovery guidance
5. Cool-down

Do not prescribe medication. Do not diagnose. Do not promise a specific physical result.
Keep the plan adaptable and encourage stopping if there is pain or unusual symptoms.
"""
    response = client.models.generate_content(
        model=settings.gemini_workout_model,
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty workout plan.")
    return text, "gemini"
