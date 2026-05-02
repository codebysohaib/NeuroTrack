"""
Request validation utilities.
Centralized validation layer — all input sanitization lives here.
Keeps route handlers clean and business logic separate.
"""

from flask import jsonify, make_response
from typing import Any
import re
import logging

logger = logging.getLogger(__name__)

VALID_MOODS = frozenset({
    "happy", "sad", "anxious", "angry",
    "stressed", "tired", "lonely", "overwhelmed",
    "depressed", "calm", "neutral"
})

MAX_USER_ID_LENGTH = 128
MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 2
MAX_NOTE_LENGTH = 500
USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.@]+$')


def validate_required_fields(data: dict, fields: list[str]):
    """
    Validates all required fields are present and non-empty.
    Returns (True, None) if valid.
    Returns (False, error_response, status_code) if invalid.
    """
    if not isinstance(data, dict):
        return False, make_response(jsonify({
            "error": "Invalid request body",
            "detail": "Expected a JSON object."
        }), 400)

    for field in fields:
        value = data.get(field)
        if value is None:
            return False, make_response(jsonify({
                "error": "Missing required field",
                "detail": f"Field '{field}' is required.",
                "field": field
            }), 400)
        if not str(value).strip():
            return False, make_response(jsonify({
                "error": "Empty required field",
                "detail": f"Field '{field}' cannot be empty.",
                "field": field
            }), 400)

    return True, None


def validate_mood(mood: str):
    """
    Validates mood is one of the supported values.
    Returns (True, None) if valid.
    Returns (False, error_response, status_code) if invalid.
    """
    if not mood or not isinstance(mood, str):
        return False, make_response(jsonify({
            "error": "Invalid mood",
            "detail": "Mood must be a non-empty string.",
            "supported_moods": sorted(VALID_MOODS)
        }), 400)

    cleaned = mood.lower().strip()

    if cleaned not in VALID_MOODS:
        return False, make_response(jsonify({
            "error": "Unsupported mood",
            "detail": f"'{mood}' is not a recognized mood.",
            "supported_moods": sorted(VALID_MOODS)
        }), 400)

    return True, None


def validate_user_id(user_id: Any):
    """
    Validates user_id is safe, non-empty, and within length limits.
    Prevents injection and ensures consistent ID format.
    """
    if not user_id or not isinstance(user_id, str):
        return False, make_response(jsonify({
            "error": "Invalid user_id",
            "detail": "user_id must be a non-empty string."
        }), 400)

    cleaned = user_id.strip()

    if not cleaned:
        return False, make_response(jsonify({
            "error": "Invalid user_id",
            "detail": "user_id cannot be blank."
        }), 400)

    if len(cleaned) > MAX_USER_ID_LENGTH:
        return False, make_response(jsonify({
            "error": "Invalid user_id",
            "detail": f"user_id must be under {MAX_USER_ID_LENGTH} characters."
        }), 400)

    if not USER_ID_PATTERN.match(cleaned):
        return False, make_response(jsonify({
            "error": "Invalid user_id format",
            "detail": "user_id may only contain letters, numbers, hyphens, underscores, dots, and @ symbols."
        }), 400)

    return True, None


def validate_message(message: Any):
    """
    Validates chat message length and content.
    """
    if not message or not isinstance(message, str):
        return False, make_response(jsonify({
            "error": "Invalid message",
            "detail": "Message must be a non-empty string."
        }), 400)

    cleaned = message.strip()

    if len(cleaned) < MIN_MESSAGE_LENGTH:
        return False, make_response(jsonify({
            "error": "Message too short",
            "detail": f"Message must be at least {MIN_MESSAGE_LENGTH} characters."
        }), 400)

    if len(cleaned) > MAX_MESSAGE_LENGTH:
        return False, make_response(jsonify({
            "error": "Message too long",
            "detail": f"Message must be under {MAX_MESSAGE_LENGTH} characters."
        }), 400)

    return True, None


def validate_note(note: Any):
    """
    Validates optional mood note length.
    """
    if note is None:
        return True, None

    if not isinstance(note, str):
        return False, make_response(jsonify({
            "error": "Invalid note",
            "detail": "Note must be a string."
        }), 400)

    if len(note.strip()) > MAX_NOTE_LENGTH:
        return False, make_response(jsonify({
            "error": "Note too long",
            "detail": f"Note must be under {MAX_NOTE_LENGTH} characters."
        }), 400)

    return True, None


def validate_intensity(intensity: Any):
    """
    Validates optional mood intensity score (1-10).
    """
    if intensity is None:
        return True, None

    try:
        value = int(intensity)
    except (ValueError, TypeError):
        return False, make_response(jsonify({
            "error": "Invalid intensity",
            "detail": "Intensity must be an integer."
        }), 400)

    if not (1 <= value <= 10):
        return False, make_response(jsonify({
            "error": "Invalid intensity",
            "detail": "Intensity must be between 1 and 10."
        }), 400)

    return True, None