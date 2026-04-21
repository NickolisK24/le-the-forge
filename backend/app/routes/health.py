"""
Health Blueprint — /api/health

Unauthenticated liveness probe. Render calls this endpoint every few seconds
via `healthCheckPath` in render.yaml; external monitors can poll it the same
way. Rate-limited to 60 requests per minute per IP so a runaway probe can't
exhaust the limiter.

The endpoint is intentionally forgiving: if the optional data/version.json
file is missing or malformed we still return 200 with a "unknown"
patch_version — the process is alive, which is the only thing Render needs
to know.

Response shape
--------------
{
  "status":          "ok",
  "version":         "0.8.0",          # from VERSION file at repo root
  "patch_version":   "1.4.3",          # from data/version.json
  "uptime_seconds":  42                # wall-clock since process start
}
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from flask import Blueprint, current_app, jsonify

from app import __version__, limiter

health_bp = Blueprint("health", __name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_VERSION_JSON = _REPO_ROOT / "data" / "version.json"


def _read_patch_version() -> str:
    try:
        with open(_VERSION_JSON, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return "unknown"
    return data.get("patch") or data.get("patch_version") or "unknown"


@health_bp.get("/health")
@limiter.limit("60 per minute")
def health():
    start_time = current_app.extensions.get("start_time", time.time())
    return jsonify({
        "status": "ok",
        "version": __version__,
        "patch_version": _read_patch_version(),
        "uptime_seconds": int(time.time() - start_time),
    }), 200
