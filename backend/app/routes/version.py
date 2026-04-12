"""
Version Blueprint — /api/version

GET /api/version  → Current app version, git commit SHA, and data version.

Response
--------
{
  "data": {
    "version": "1.0.0-beta",
    "commit": "a1b2c3d",
    "data_version": "1.0.0",
    "current_patch": "1.4.3",
    "current_season": 4
  }
}

version        Semantic version from the VERSION file at the project root.
commit         Short git commit SHA of the running build.
data_version   Bumped whenever reference data (affixes.json, etc.) changes.
current_patch  Last Epoch patch string tracked by this instance.
current_season Last Epoch season number tracked by this instance.
"""

import os
import subprocess

from flask import Blueprint, current_app

from app.utils.responses import ok

version_bp = Blueprint("version", __name__)

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)


def _read_version() -> str:
    try:
        with open(os.path.join(_PROJECT_ROOT, "VERSION")) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"


def _git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd=_PROJECT_ROOT,
        ).decode().strip() or None
    except Exception:
        return None


@version_bp.get("")
def get_version():
    """Return app version metadata."""
    return ok(data={
        "version": _read_version(),
        "commit": _git_sha(),
        "data_version": current_app.config.get("DATA_VERSION", "1.0.0"),
        "current_patch": current_app.config.get("CURRENT_PATCH", "1.4.3"),
        "current_season": current_app.config.get("CURRENT_SEASON", 4),
    })
