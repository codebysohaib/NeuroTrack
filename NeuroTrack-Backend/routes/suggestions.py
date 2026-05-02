from flask import Blueprint, request, jsonify
from services.suggestions_service import get_suggestion, get_all_supported_moods, get_all_suggestions
from utils.validators import validate_mood
import logging

logger = logging.getLogger(__name__)

suggestions_bp = Blueprint("suggestions", __name__)


@suggestions_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    """
    GET /api/suggestions?mood=&count=
    Returns mood-based wellness tips.
    Optional: count (default 1, max 3) to return multiple tips at once.
    """
    mood = request.args.get("mood", "").strip().lower()

    if not mood:
        return jsonify({
            "error": "Missing parameter",
            "detail": "Query parameter 'mood' is required.",
            "supported_moods": get_all_supported_moods()
        }), 400

    valid, err = validate_mood(mood)
    if not valid:
        return jsonify({
            "error": f"Unsupported mood: '{mood}'",
            "detail": "Please use one of the supported moods.",
            "supported_moods": get_all_supported_moods()
        }), 400

    # Optional: return multiple tips
    try:
        count = int(request.args.get("count", 1))
        count = max(1, min(count, 3))
    except ValueError:
        count = 1

    if count == 1:
        tips = [get_suggestion(mood)]
    else:
        tips = get_all_suggestions(mood)[:count]

    return jsonify({
        "mood": mood,
        "count": len(tips),
        "tips": tips,
        "tip": tips[0] if tips else None,  # backward compatibility
    }), 200


@suggestions_bp.route("/suggestions/all", methods=["GET"])
def get_all_suggestions_endpoint():
    """
    GET /api/suggestions/all
    Returns all tips for all supported moods.
    Useful for frontend to preload suggestions.
    """
    try:
        all_moods = get_all_supported_moods()
        result = {}

        for mood in all_moods:
            result[mood] = get_all_suggestions(mood)

        return jsonify({
            "supported_moods": all_moods,
            "total_moods": len(all_moods),
            "suggestions": result
        }), 200

    except Exception as e:
        logger.error(f"[Suggestions All Error] {e}")
        return jsonify({
            "error": "Failed to fetch suggestions.",
            "detail": "Please try again."
        }), 500


@suggestions_bp.route("/suggestions/moods", methods=["GET"])
def get_supported_moods():
    """
    GET /api/suggestions/moods
    Returns list of all supported moods.
    Frontend can use this to dynamically build mood picker UI.
    """
    moods = get_all_supported_moods()
    return jsonify({
        "supported_moods": moods,
        "total": len(moods)
    }), 200