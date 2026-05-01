"""
AI response service powered by Groq (LLaMA 3.3 70B).
Handles all interactions with the Groq API.
Designed for mental health support using CBT principles.
"""

from groq import Groq
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

_client = None


def _get_client() -> Groq:
    """
    Lazy-initialize Groq client (singleton).
    Fails fast with a clear error if API key is missing.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in environment variables.")

    _client = Groq(api_key=api_key)
    logger.info("[Groq] Client initialized successfully.")
    return _client


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a compassionate mental health support assistant.
Your role is to provide emotional support using Cognitive Behavioral Therapy (CBT) principles.

Rules you MUST follow:
- Keep every response to 2-4 sentences maximum
- Use a calm, warm, and non-judgmental tone
- Never diagnose, prescribe, or give medical advice
- Never mention specific medications or dosages
- Encourage small, concrete positive actions
- If the user expresses suicidal thoughts or self-harm, always recommend professional help immediately
- Speak directly to the user — no preamble, no "As an AI" disclaimers"""

CRISIS_KEYWORDS = frozenset({
    "suicide", "suicidal", "kill myself", "end my life",
    "self harm", "self-harm", "hurt myself", "don't want to live",
    "want to die", "cutting myself"
})

CRISIS_RESPONSE = (
    "I hear you, and I'm genuinely concerned about your safety. "
    "Please reach out to a crisis helpline immediately — "
    "in Pakistan you can call Umang at 0317-4288665, "
    "or text a trusted person in your life right now. "
    "You don't have to face this alone."
)

FALLBACK_RESPONSES = [
    "I'm here for you. Take a slow, deep breath — you're not alone in this.",
    "What you're feeling is valid. Try taking one slow breath and focus on this moment.",
    "I'm having trouble responding right now, but I want you to know — you matter.",
]

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 180
TEMPERATURE = 0.7


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _is_crisis_message(message: str) -> bool:
    """Detects crisis-level language requiring immediate escalation."""
    lowered = message.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)


def _get_fallback() -> str:
    """Returns a rotating fallback message when the API is unavailable."""
    import random
    return random.choice(FALLBACK_RESPONSES)


def get_ai_response(user_message: str) -> str:
    """
    Generates a CBT-style mental health support response.
    Handles crisis detection, API errors, and fallback gracefully.

    Args:
        user_message: The user's raw input message.

    Returns:
        A supportive AI-generated response string.
    """
    if not user_message or not user_message.strip():
        return _get_fallback()

    # Crisis detection — always prioritize safety
    if _is_crisis_message(user_message):
        logger.warning("[Groq] Crisis message detected — returning crisis response.")
        return CRISIS_RESPONSE

    try:
        client = _get_client()

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message.strip()}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        reply = response.choices[0].message.content.strip()

        if not reply:
            logger.warning("[Groq] Empty response received from API.")
            return _get_fallback()

        logger.info(f"[Groq] Response generated. tokens_used={response.usage.total_tokens}")
        return reply

    except RuntimeError as e:
        logger.error(f"[Groq] Configuration error: {e}")
        return _get_fallback()

    except Exception as e:
        logger.error(f"[Groq] API error: {e}")
        return _get_fallback()


def get_groq_status() -> dict:
    """
    Returns Groq service status.
    Used by health check endpoint.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return {"status": "unavailable", "detail": "GROQ_API_KEY is not set."}
    return {"status": "configured", "model": MODEL}