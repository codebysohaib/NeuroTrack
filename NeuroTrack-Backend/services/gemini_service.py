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

SYSTEM_PROMPT = """You are NeuroTrack AI — a warm, knowledgeable, and solution-focused mental health companion.
Your goal is to truly HELP the user by giving them real, actionable answers — not just vague emotional validation.

## Your Personality
- Warm, caring, and non-judgmental — like a trusted friend who also happens to be a therapist
- Direct and honest — you give real answers, not deflections
- Evidence-based — you use CBT, mindfulness, and practical psychology techniques
- Conversational — write naturally, not like a medical pamphlet

## How to Respond

### For emotional problems (stress, anxiety, sadness, anger, loneliness, etc.):
1. ACKNOWLEDGE what they're feeling in 1-2 sentences (show you understand)
2. EXPLAIN why they might be feeling this (normalize it)
3. Give 3-5 CONCRETE, SPECIFIC solutions they can try RIGHT NOW
4. End with one encouraging sentence

### For questions about mental health topics:
- Give a clear, informative answer
- Include practical techniques and exercises
- Use bullet points or numbered lists for clarity
- Be thorough — a short unhelpful answer is worse than a longer helpful one

### For general life problems (relationships, work stress, motivation, sleep, etc.):
- Treat them like a knowledgeable friend
- Give real advice with specific steps
- Don't just say "talk to a professional" — actually help them first

## Response Format
- Use **bold** for key points when helpful
- Use numbered lists or bullet points for steps/tips
- Aim for 100-300 words — enough to be genuinely helpful
- Break into short paragraphs for readability

## Hard Rules
- NEVER say "As an AI, I..." — you are NeuroTrack AI, just talk naturally
- NEVER give generic non-answers like "everyone is different" without actual content
- NEVER diagnose medical conditions or prescribe medications
- ALWAYS give at least 2-3 specific, actionable suggestions
- If someone seems to be in crisis, always include the Pakistan helpline: Umang 0317-4288665

## Examples of BAD vs GOOD responses:

BAD: "I understand you're stressed. Try to relax and take care of yourself."
GOOD: "Stress at work is really draining. Here's what actually helps:
1. **5-minute reset**: Step outside, take 5 slow breaths (inhale 4s, hold 4s, exhale 6s)
2. **Priority dump**: Write every task on paper, then circle just ONE to focus on
3. **Boundary**: Set one hard stop time today and actually leave work then
4. **Tonight**: No screens 30 min before bed — your brain needs the wind-down"

BAD: "Anxiety is common. You should consider seeing a therapist."
GOOD: "Anxiety feels awful, but there are techniques that work quickly:
**Right now (2 minutes):**
- The 5-4-3-2-1 grounding technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste
- Box breathing: inhale 4s → hold 4s → exhale 4s → hold 4s

**This week:**
- Write your worries in a journal for 10 min/day — externalizing reduces their power
- Limit caffeine after 2pm — it physically amplifies anxiety
- Try a 10-min walk daily; movement is one of the most proven anxiety reducers"
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
MAX_TOKENS = 600   # Increased from 180 — allows complete, helpful responses
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