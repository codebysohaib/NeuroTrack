from flask import Blueprint, request, jsonify
from services.gemini_service import get_ai_response
from utils.validators import validate_mood
import logging
import json

logger = logging.getLogger(__name__)

suggestions_bp = Blueprint("suggestions", __name__)

@suggestions_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    """
    GET /api/suggestions?mood=&count=
    Returns AI-generated mood-based wellness tips.
    Uses Groq AI to generate fresh, personalized content.
    """
    mood = request.args.get("mood", "").strip().lower()

    if not mood:
        return jsonify({
            "error": "Missing parameter",
            "detail": "Query parameter 'mood' is required."
        }), 400

    valid, err = validate_mood(mood)
    if not valid:
        return err

    try:
        # Prompt AI specifically for tips
        prompt = (
            f"The user is feeling '{mood}'. Give them exactly 3 short, concrete, "
            "and helpful wellness tips or CBT-based actions they can take right now. "
            "Format the response as a simple JSON list of strings only. "
            "Example: [\"Tip 1\", \"Tip 2\", \"Tip 3\"]"
        )
        
        ai_raw = get_ai_response(prompt)
        
        # Try to parse JSON from AI response
        try:
            # Look for JSON array in the text
            start = ai_raw.find('[')
            end = ai_raw.rfind(']') + 1
            if start != -1 and end != -1:
                tips = json.loads(ai_raw[start:end])
            else:
                tips = [ai_raw] # Fallback to raw string as single tip
        except:
            tips = [ai_raw]

        return jsonify({
            "mood": mood,
            "count": len(tips),
            "tips": tips,
            "source": "AI Generated"
        }), 200

    except Exception as e:
        logger.error(f"[AI Suggestions Error] {e}")
        return jsonify({"error": "AI could not generate tips right now."}), 500

@suggestions_bp.route("/suggestions/moods", methods=["GET"])
def get_supported_moods():
    """Returns list of common moods for the UI."""
    return jsonify({
        "supported_moods": ["happy", "sad", "anxious", "angry", "stressed", "neutral", "calm", "depressed"],
        "total": 8
    }), 200