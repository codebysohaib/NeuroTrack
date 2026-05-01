"""
Health check endpoint.
Provides real-time service status, dependency checks, and uptime.
Used by deployment platforms, monitoring tools, and load balancers.
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone
import logging
import os
import platform
import sys

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)

START_TIME = datetime.now(timezone.utc)
VERSION = "1.0.0"
SERVICE_NAME = "ai-mental-health-backend"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_uptime() -> str:
    """Calculate service uptime since startup."""
    delta = datetime.now(timezone.utc) - START_TIME
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def _get_uptime_seconds() -> int:
    """Returns uptime as raw seconds for monitoring tools."""
    delta = datetime.now(timezone.utc) - START_TIME
    return int(delta.total_seconds())


def _check_firebase() -> dict:
    """Verify Firebase connectivity using the service's own status reporter."""
    try:
        from services.firebase_service import get_firebase_status
        return get_firebase_status()
    except Exception as e:
        logger.warning(f"[Health] Firebase check failed: {e}")
        return {"status": "unavailable", "detail": str(e)}


def _check_groq() -> dict:
    """Verify Groq API configuration using the service's own status reporter."""
    try:
        from services.gemini_service import get_groq_status
        return get_groq_status()
    except Exception as e:
        logger.warning(f"[Health] Groq check failed: {e}")
        return {"status": "unavailable", "detail": str(e)}


def _get_system_info() -> dict:
    """Returns basic runtime environment metadata."""
    return {
        "python_version": sys.version.split(" ")[0],
        "platform": platform.system(),
        "environment": os.getenv("FLASK_ENV", "development"),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    Full health check with dependency status and uptime.
    Returns 200 if fully healthy, 207 if degraded.
    """
    firebase_status = _check_firebase()
    groq_status = _check_groq()

    firebase_healthy = firebase_status.get("status") == "connected"
    groq_healthy = groq_status.get("status") in ("configured", "connected")
    all_healthy = firebase_healthy and groq_healthy

    payload = {
        "service": SERVICE_NAME,
        "status": "healthy" if all_healthy else "degraded",
        "version": VERSION,
        "uptime": _get_uptime(),
        "uptime_seconds": _get_uptime_seconds(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "started_at": START_TIME.isoformat(),
        "services": {
            "firebase": firebase_status,
            "groq": groq_status,
        },
        "system": _get_system_info(),
    }

    status_code = 200 if all_healthy else 207
    logger.info(f"[Health] status={payload['status']} uptime={payload['uptime']}")
    return jsonify(payload), status_code


@health_bp.route("/ping", methods=["GET"])
def ping():
    """
    GET /api/ping
    Lightweight liveness probe — no dependency checks.
    Used by load balancers and container orchestrators (Docker, K8s).
    Returns in <5ms.
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@health_bp.route("/version", methods=["GET"])
def version():
    """
    GET /api/version
    Returns service version and runtime info.
    """
    return jsonify({
        "service": SERVICE_NAME,
        "version": VERSION,
        "python": sys.version.split(" ")[0],
        "environment": os.getenv("FLASK_ENV", "development"),
        "started_at": START_TIME.isoformat(),
    }), 200