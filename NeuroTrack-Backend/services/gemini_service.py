"""
AI response service powered by Groq (LLaMA 3.3 70B).
Handles all interactions with the Groq API.
Trained to give proper, solution-focused mental health + general support.
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
# System Prompt — solution-focused, detailed, empathetic
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a helpful, versatile AI assistant, similar to Gemini.
Your name is NeuroTrack AI, but your capabilities are broad and general-purpose.
You can answer any questions the user has, ranging from coding, math, general knowledge, science, writing, to mental health support and more.

## Your Personality
- Helpful, intelligent, and informative.
- Clear and concise, providing detailed answers when necessary.
- Conversational and polite.
- Non-judgmental and encouraging.

## How to Respond
- Answer the user's question directly and accurately.
- For technical questions (like coding or math), provide step-by-step explanations and code snippets.
- For general questions, provide structured, easy-to-read information (use bolding, lists, etc.).
- If the user asks about mental health or emotional problems, provide warm, empathetic support and actionable advice, but remember you can talk about anything else as well.

## Hard Rules
- Answer whatever the user wants to know about. Do not artificially restrict your answers to only mental health.
- Give real, complete answers.
- If someone seems to be in a life-threatening crisis, ALWAYS include the Pakistan helpline: Umang 0317-4288665.
"""

CRISIS_KEYWORDS = frozenset({
    "suicide", "suicidal", "kill myself", "end my life",
    "self harm", "self-harm", "hurt myself", "don't want to live",
    "want to die", "cutting myself", "no reason to live",
    "better off dead", "can't go on"
})

CRISIS_RESPONSE = """I hear you, and what you're feeling right now is real and it matters. You don't have to face this alone.

**Please reach out right now:**
- 📞 **Umang helpline (Pakistan):** 0317-4288665 (free, confidential)
- 📞 **Rozan Counseling:** 051-2890505
- Or text someone you trust — even just "I need to talk"

If you're in immediate danger, please go to your nearest emergency room or call 115 (Rescue).

I'm here with you. Can you tell me a little more about what's been happening? Sometimes just putting it into words helps, and I want to understand."""

FALLBACK_RESPONSES = [
    "I'm here for you. What's on your mind? Tell me what you're going through and I'll do my best to help.",
    "I want to help — can you share a bit more about what you're feeling or dealing with right now?",
    "I'm listening. Whatever you're facing, let's work through it together.",
]

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 2048   # Increased to allow complete, helpful general responses (like coding, math, etc.)
TEMPERATURE = 0.75


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
    Generates a helpful, solution-focused mental health support response.
    Handles crisis detection, API errors, and fallback gracefully.

    Args:
        user_message: The user's raw input message.

    Returns:
        A detailed, actionable AI-generated response string.
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