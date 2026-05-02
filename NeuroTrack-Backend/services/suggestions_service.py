"""
Mood-based suggestion engine.
Maps user moods to actionable, CBT-inspired wellness tips.
Designed to be extensible, testable, and production-ready.
"""

import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SUGGESTIONS: dict[str, list[str]] = {
    "happy": [
        "Keep the momentum going — write down 3 things that made you smile today.",
        "Share your positive energy with someone you care about.",
        "Use this high-energy state to tackle something you've been postponing.",
        "Practice gratitude journaling — happiness compounds when acknowledged.",
    ],
    "sad": [
        "Try a 2-minute deep breathing exercise: inhale 4s, hold 4s, exhale 6s.",
        "It's okay to feel sad. Step outside for 5 minutes — fresh air genuinely helps.",
        "Write down one small thing you're grateful for right now, no matter how small.",
        "Put on a song that comforts you and let yourself feel it fully.",
    ],
    "anxious": [
        "Ground yourself: name 5 things you can see, 4 you can touch, 3 you can hear.",
        "Try box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 3 times.",
        "Write your worry down on paper — externalizing it reduces its power over you.",
        "Remind yourself: you have handled hard things before. This will pass too.",
    ],
    "angry": [
        "Step away for 5 minutes before reacting. Your feelings are valid — space helps.",
        "Count slowly to 10, or splash cold water on your face to reset.",
        "Write out what made you angry — articulating it releases emotional pressure.",
        "Take a brisk 5-minute walk to burn off the adrenaline safely.",
    ],
    "stressed": [
        "Break your workload into one small step. Just one. What's the first thing?",
        "Take a 5-minute walk — even around the room. Movement resets your nervous system.",
        "Try the 4-7-8 technique: inhale 4s, hold 7s, exhale 8s. Repeat twice.",
        "Say no to one non-essential thing today. Protecting your energy is not selfish.",
    ],
    "tired": [
        "Rest is productive. A 10-20 minute nap can restore focus significantly.",
        "Drink a glass of water — fatigue is often early-stage dehydration.",
        "Give yourself permission to do less today. You're still doing enough.",
        "Try a 2-minute stretch — loosening tight muscles reduces mental fatigue.",
    ],
    "lonely": [
        "Reach out to one person today — a short text is more than enough.",
        "Being alone and feeling lonely are different. Try a creative activity you enjoy.",
        "Consider joining an online community around something you genuinely love.",
        "Write a letter to your future self — it builds a sense of connection over time.",
    ],
    "overwhelmed": [
        "You don't have to do everything today. Pick one thing and let the rest wait.",
        "Try a brain dump: write everything on your mind, then pick only the top priority.",
        "Take 3 slow deep breaths right now. Your nervous system will respond immediately.",
        "Ask for help with one thing. Delegation is a skill, not a weakness.",
    ],
    "depressed": [
        "Start with the smallest possible action — even just getting a glass of water counts.",
        "You don't have to feel better instantly. Just focus on the next 10 minutes.",
        "Reach out to someone you trust today, even with just a simple message.",
        "Consider speaking to a mental health professional — support is a sign of strength.",
    ],
    "calm": [
        "This is a great state to set intentions. What do you want to focus on today?",
        "Use this clarity to reflect on what's going well and what you'd like to improve.",
        "Practice a short mindfulness session to deepen this calm state.",
        "Write down one goal for the week while your mind is clear.",
    ],
    "neutral": [
        "Check in with your body — sometimes neutral means you need a moment of rest.",
        "A short walk or change of scenery can spark energy when you're feeling flat.",
        "Try something small and creative to see what mood it brings out.",
        "Reach out to someone — connection often shifts a neutral state positively.",
    ],
}

DEFAULT_SUGGESTION = (
    "Take a moment to check in with yourself. "
    "A short walk, a glass of water, or a few deep breaths "
    "can make a real difference."
)

MOOD_CATEGORIES: dict[str, list[str]] = {
    "positive": ["happy", "calm"],
    "low_energy": ["sad", "tired", "depressed", "lonely"],
    "high_tension": ["anxious", "stressed", "angry", "overwhelmed"],
    "neutral": ["neutral"],
}


def get_suggestion(mood: str) -> str:
    """
    Returns a single random CBT-inspired tip for the given mood.
    Falls back to a universal default if mood is unrecognized.
    """
    tips = SUGGESTIONS.get(mood.lower().strip())
    if tips:
        return random.choice(tips)
    logger.warning(f"[Suggestions] Unrecognized mood requested: '{mood}'")
    return DEFAULT_SUGGESTION


def get_all_suggestions(mood: str) -> list[str]:
    """
    Returns all tips for a given mood.
    Used when frontend wants to cycle through multiple suggestions.
    """
    tips = SUGGESTIONS.get(mood.lower().strip(), [])
    if not tips:
        return [DEFAULT_SUGGESTION]
    shuffled = tips.copy()
    random.shuffle(shuffled)
    return shuffled


def get_all_supported_moods() -> list[str]:
    """Returns sorted list of all supported mood keys."""
    return sorted(SUGGESTIONS.keys())


def get_mood_category(mood: str) -> Optional[str]:
    """
    Returns the emotional category of a mood.
    Useful for frontend to group or color-code moods.
    Categories: positive, low_energy, high_tension, neutral
    """
    mood = mood.lower().strip()
    for category, moods in MOOD_CATEGORIES.items():
        if mood in moods:
            return category
    return None


def get_suggestions_by_category(category: str) -> dict[str, list[str]]:
    """
    Returns all tips grouped by a mood category.
    Useful for building category-based recommendation screens.
    """
    moods = MOOD_CATEGORIES.get(category.lower(), [])
    if not moods:
        return {}
    return {mood: SUGGESTIONS.get(mood, []) for mood in moods}