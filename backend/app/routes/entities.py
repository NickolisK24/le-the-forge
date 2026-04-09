"""
Entities Blueprint — /api/entities

Lightweight endpoints for entity listings.

GET /api/entities/bosses — List all boss/enemy profiles (id + name only).
"""

from flask import Blueprint

from app.utils.responses import ok
from app.utils.cache import cached_route

entities_bp = Blueprint("entities", __name__)


@entities_bp.get("/bosses")
@cached_route("entities:bosses", ttl=86400)
def list_bosses():
    """Return a lightweight list of all boss/enemy profiles."""
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        if pipeline and hasattr(pipeline, "enemies"):
            bosses = []
            for enemy in pipeline.enemies:
                profile = enemy.to_dict() if hasattr(enemy, "to_dict") else enemy
                bosses.append({
                    "id": profile.get("id", "unknown"),
                    "name": profile.get("name", "Unknown"),
                    "category": profile.get("category", "unknown"),
                })
            return ok(data=bosses)
    except RuntimeError:
        pass
    return ok(data=[])
