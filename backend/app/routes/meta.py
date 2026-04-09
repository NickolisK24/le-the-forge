"""
Meta Blueprint — /api/meta

GET /api/meta/snapshot  → Full meta analytics snapshot
GET /api/meta/trending  → Top 10 trending builds
"""

from flask import Blueprint

from app import limiter
from app.services import meta_analytics_service
from app.utils.responses import ok

meta_bp = Blueprint("meta", __name__)


@meta_bp.get("/snapshot")
@limiter.limit("30 per minute")
def snapshot():
    data = meta_analytics_service.get_snapshot()
    return ok(data=data)


@meta_bp.get("/trending")
@limiter.limit("30 per minute")
def trending():
    data = meta_analytics_service.get_trending()
    return ok(data=data)
