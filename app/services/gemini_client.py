from functools import lru_cache

from ..config import get_settings


@lru_cache
def get_client():
    """Return a Gemini client only when Gemini is actually configured.

    Importing google-genai lazily is intentional: FitBuddy can run in DEMO mode
    without the optional Gemini SDK or an API key.
    """
    settings = get_settings()
    if not settings.gemini_enabled:
        return None

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "Gemini is enabled but the google-genai package is not installed. "
            "Run: python -m pip install -r requirements.txt"
        ) from exc

    return genai.Client(api_key=settings.gemini_api_key)
