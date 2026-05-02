from flask import Blueprint, request, jsonify
from services.firebase_service import get_db
from utils.validators import validate_required_fields, validate_mood
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

mood_bp = Blueprint("mood", __name__)

VALID_MOODS = {"happy", "sad", "anxious", "angry", "stressed", "neutral", "depressed", "calm"}
MAX_NOTE_LENGTH = 500
DEFAULT_HISTORY_LIMIT = 30
MAX_HISTORY_LIMIT = 100


@mood_bp.route("/mood", methods=["POST"])
def save_mood():
    """
    POST /api/mood
    Saves a mood entry for a user with optional note and intensity.
    Required: user_id, mood
    Optional: note, intensity (1-10)
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Invalid request",
            "detail": "Request body must be valid JSON"
        }), 400

    valid, err = validate_required_fields(data, ["user_id", "mood"])
    if not valid:
        return err

    user_id = str(data["user_id"]).strip()
    mood = str(data["mood"]).strip().lower()
    note = str(data.get("note", "")).strip()

    if not user_id:
        return jsonify({"error": "user_id cannot be empty"}), 400

    mood_valid, mood_err = validate_mood(mood)
    if not mood_valid:
        return mood_err

    if len(note) > MAX_NOTE_LENGTH:
        return jsonify({
            "error": "Note too long",
            "detail": f"Note must be under {MAX_NOTE_LENGTH} characters."
        }), 400

    intensity = data.get("intensity")
    if intensity is not None:
        try:
            intensity = int(intensity)
            if not (1 <= intensity <= 10):
                return jsonify({
                    "error": "Invalid intensity",
                    "detail": "Intensity must be between 1 and 10."
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid intensity",
                "detail": "Intensity must be an integer between 1 and 10."
            }), 400

    timestamp = datetime.now(timezone.utc).isoformat()

    mood_entry = {
        "user_id": user_id,
        "mood": mood,
        "note": note,
        "intensity": intensity,
        "timestamp": timestamp,
    }

    try:
        db = get_db()
        _, doc_ref = db.collection("moods").add(mood_entry)
        logger.info(f"[Mood Saved] user={user_id} mood={mood} doc={doc_ref.id}")

        return jsonify({
            "success": True,
            "message": "Mood logged successfully.",
            "data": {
                "id": doc_ref.id,
                "user_id": user_id,
                "mood": mood,
                "note": note,
                "intensity": intensity,
                "timestamp": timestamp,
            }
        }), 201

    except Exception as e:
        logger.error(f"[Firebase Mood Save Error] user={user_id} error={e}")
        return jsonify({
            "error": "Failed to save mood.",
            "detail": "Database error. Please try again."
        }), 500


@mood_bp.route("/mood/history", methods=["GET"])
def get_mood_history():
    """
    GET /api/mood/history?user_id=&limit=&mood=
    Returns mood history newest-first. Sorting done in Python to avoid
    requiring a composite Firestore index (user_id + timestamp).
    """
    user_id = request.args.get("user_id", "").strip()

    if not user_id:
        return jsonify({
            "error": "Missing parameter",
            "detail": "Query parameter 'user_id' is required."
        }), 400

    try:
        limit = int(request.args.get("limit", DEFAULT_HISTORY_LIMIT))
        limit = max(1, min(limit, MAX_HISTORY_LIMIT))
    except ValueError:
        limit = DEFAULT_HISTORY_LIMIT

    mood_filter = request.args.get("mood", "").strip().lower()
    if mood_filter and mood_filter not in VALID_MOODS:
        return jsonify({
            "error": "Invalid mood filter",
            "detail": f"Valid moods: {sorted(VALID_MOODS)}"
        }), 400

    try:
        db = get_db()
        # Query by user_id only — no .order_by() avoids composite index requirement
        docs = (
            db.collection("moods")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .stream()
        )

        history = []
        for doc in docs:
            entry = doc.to_dict()
            mood_val = entry.get("mood", "")

            if mood_filter and mood_val != mood_filter:
                continue

            history.append({
                "id": doc.id,
                "mood": mood_val,
                "note": entry.get("note", ""),
                "intensity": entry.get("intensity"),
                "timestamp": entry.get("timestamp", ""),
            })

        # Sort newest first in Python — no Firestore composite index needed
        history.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        history = history[:limit]

        return jsonify({
            "user_id": user_id,
            "count": len(history),
            "limit": limit,
            "filter": mood_filter or None,
            "history": history
        }), 200

    except Exception as e:
        logger.error(f"[Firebase Mood History Error] user={user_id} error={e}")
        return jsonify({
            "error": "Failed to fetch mood history.",
            "detail": "Database error. Please try again."
        }), 500


@mood_bp.route("/mood/summary", methods=["GET"])
def get_mood_summary():
    """
    GET /api/mood/summary?user_id=
    Returns mood frequency breakdown and most common mood.
    Sorting done in Python to avoid composite Firestore index requirement.
    """
    user_id = request.args.get("user_id", "").strip()

    if not user_id:
        return jsonify({
            "error": "Missing parameter",
            "detail": "Query parameter 'user_id' is required."
        }), 400

    try:
        db = get_db()
        # Query by user_id only — no .order_by() avoids composite index requirement
        docs = (
            db.collection("moods")
            .where(filter=FieldFilter("user_id", "==", user_id))
            .stream()
        )

        all_entries = []
        for doc in docs:
            all_entries.append(doc.to_dict())

        if not all_entries:
            return jsonify({
                "user_id": user_id,
                "total_entries": 0,
                "most_common_mood": None,
                "latest_mood": None,
                "breakdown": {}
            }), 200

        # Sort newest first in Python
        all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        mood_counts = {}
        for entry in all_entries:
            mood = entry.get("mood", "unknown")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        latest_mood = all_entries[0].get("mood") if all_entries else None
        most_common = max(mood_counts, key=mood_counts.get)

        return jsonify({
            "user_id": user_id,
            "total_entries": len(all_entries),
            "most_common_mood": most_common,
            "latest_mood": latest_mood,
            "breakdown": mood_counts
        }), 200

    except Exception as e:
        logger.error(f"[Firebase Mood Summary Error] user={user_id} error={e}")
        return jsonify({
            "error": "Failed to fetch mood summary.",
            "detail": "Database error. Please try again."
        }), 500