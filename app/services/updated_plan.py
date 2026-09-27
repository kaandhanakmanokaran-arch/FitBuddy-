from ..config import get_settings
from ..safety import safety_context
from .gemini_client import get_client
from .gemini_generator import demo_workout


def update_workout_plan(user, original_plan: str, feedback: str) -> tuple[str, str]:
    settings = get_settings()
    client = get_client()
    if client is None:
        return (
            original_plan
            + f"\n\n--- Feedback applied in DEMO mode ---\nRequested change: {feedback}\n"
              "The real Gemini mode would regenerate the full seven-day plan using this feedback.",
            "demo",
        )

    prompt = f"""
Revise the following 7-day fitness plan using the user's feedback.

User:
- Name: {user.username}
- Age: {user.age}
- Goal: {user.goal}
- Preferred intensity: {user.intensity}

Feedback:
{feedback}

Original plan:
{original_plan}

{safety_context(user.age, user.goal)}

Return a complete revised 7-day plan, not just a list of edits. Preserve useful parts of the original plan,
apply reasonable feedback, and keep the result safe and adaptable.
"""
    response = client.models.generate_content(
        model=settings.gemini_workout_model,
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty updated plan.")
    return text, "gemini"
