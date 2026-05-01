from flask import Blueprint, request, jsonify
from services.gemini_service import get_ai_response
from services.firebase_service import get_db
from utils.validators import validate_required_fields
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

VALID_MOODS = {"happy", "sad", "anxious", "angry", "stressed", "neutral", "depressed", "calm"}
MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 2


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Accepts user_id + message, returns AI-generated mental health support reply.
    Persists conversation to Firestore asynchronously (non-blocking).
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Invalid request",
            "detail": "Request body must be valid JSON"
        }), 400

    valid, err = validate_required_fields(data, ["user_id", "message"])
    if not valid:
        return err

    user_id = str(data["user_id"]).strip()
    message = str(data["message"]).strip()

    if not user_id:
        return jsonify({"error": "user_id cannot be empty"}), 400

    if len(message) < MIN_MESSAGE_LENGTH:
        return jsonify({
            "error": "Message too short",
            "detail": f"Message must be at least {MIN_MESSAGE_LENGTH} characters."
        }), 400

    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({
            "error": "Message too long",
            "detail": f"Message must be under {MAX_MESSAGE_LENGTH} characters."
        }), 400

    # Optional mood context to enrich AI response
    mood_context = data.get("mood", "").strip().lower()
    if mood_context and mood_context not in VALID_MOODS:
        mood_context = ""

    # Build enriched prompt if mood context provided
    enriched_message = (
        f"[User is feeling {mood_context}] {message}"
        if mood_context else message
    )

    # Get AI reply
    reply = get_ai_response(enriched_message)

    # Persist to Firestore (non-blocking — never crash the request)
    _log_chat_to_firebase(user_id, message, reply, mood_context)

    return jsonify({
        "reply": reply,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


def _log_chat_to_firebase(user_id: str, message: str, reply: str, mood: str = "") -> None:
    """Persist chat log to Firestore. Silently fails to never block the response."""
    try:
        db = get_db()
        db.collection("chats").add({
            "user_id": user_id,
            "message": message,
            "reply": reply,
            "mood_context": mood,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_length": len(message),
            "reply_length": len(reply)
        })
    except Exception as e:
        logger.warning(f"[Firebase Chat Log Error] {e}")