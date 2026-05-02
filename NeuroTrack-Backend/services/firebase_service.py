"""
Firebase Firestore service.
Singleton pattern — initializes once, reuses connection across all requests.
Handles missing credentials gracefully to prevent full app crash.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_db = None
_initialized = False
_init_error = None


def _initialize_firebase() -> bool:
    """
    Initializes Firebase Admin SDK once.
    Returns True if successful, False if failed.
    Stores error for health check reporting.
    """
    global _initialized, _init_error

    if _initialized:
        return True

    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")

    if not cred_path:
        _init_error = "FIREBASE_CREDENTIALS_PATH is not set."
        logger.error(f"[Firebase Init] {_init_error}")
        return False

    if not os.path.exists(cred_path):
        _init_error = f"Credentials file not found: '{cred_path}'"
        logger.error(f"[Firebase Init] {_init_error}")
        return False

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        _initialized = True
        _init_error = None
        logger.info("[Firebase Init] Successfully initialized Firebase Admin SDK.")
        return True

    except Exception as e:
        _init_error = str(e)
        logger.error(f"[Firebase Init] Failed to initialize: {e}")
        return False


def get_db():
    """
    Returns a Firestore client (singleton).
    Raises RuntimeError if Firebase failed to initialize.
    Always call inside try/except in route handlers.
    """
    global _db

    if _db is not None:
        return _db

    success = _initialize_firebase()

    if not success:
        raise RuntimeError(
            f"Firebase is unavailable: {_init_error or 'Unknown error'}"
        )

    _db = firestore.client()
    return _db


def get_firebase_status() -> dict:
    """
    Returns Firebase connection status.
    Used by health check endpoint to report dependency status.
    """
    if _db is not None:
        return {"status": "connected"}

    if _init_error:
        return {"status": "unavailable", "detail": _init_error}

    # Try initializing on first health check
    try:
        get_db()
        return {"status": "connected"}
    except RuntimeError as e:
        return {"status": "unavailable", "detail": str(e)}


def is_firebase_ready() -> bool:
    """Quick boolean check for Firebase availability."""
    return _db is not None or _initialized