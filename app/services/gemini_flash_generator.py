from ..config import get_settings
from ..safety import safety_context
from .gemini_client import get_client


def demo_tip(goal: str) -> str:
    tips = {
        "weight loss": "Build meals around vegetables, whole foods, adequate protein and regular hydration. Avoid crash diets.",
        "muscle gain": "Include a protein source in regular meals and prioritize sleep and recovery alongside resistance exercise.",
        "general wellness": "Keep hydration, balanced meals, regular movement and consistent sleep as simple daily foundations.",
        "flexibility": "Stay hydrated and include gentle mobility work regularly; move gradually rather than forcing a stretch.",
    }
    return tips.get(goal, tips["general wellness"])


def generate_nutrition_tip_with_flash(user) -> tuple[str, str]:
    settings = get_settings()
    client = get_client()
    if client is None:
        return demo_tip(user.goal), "demo"

    prompt = f"""
Give one concise nutrition or recovery tip for a user whose general fitness goal is "{user.goal}".
Age: {user.age}.
{safety_context(user.age, user.goal)}

Keep it to 2–4 sentences. Emphasize balanced eating, hydration, sleep or recovery.
Do not prescribe a restrictive diet, calories, supplements, fasting, or medical treatment.
"""
    response = client.models.generate_content(
        model=settings.gemini_tip_model,
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")
    return text, "gemini"
