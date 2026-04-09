"""
Views Blueprint — /api/builds/<slug>/view

POST /api/builds/<slug>/view → Track a build page view (rate-limited per IP per build)
"""

import hashlib
from datetime import datetime, timezone

from flask import Blueprint, request

from app import db, limiter
from app.models import Build, BuildView
from app.utils.responses import error, not_found
from app.utils.cache import get as cache_get, set as cache_set

views_bp = Blueprint("views", __name__)

_VIEW_RATE_TTL = 3600  # 1 hour per IP per build


def _hash_ip(ip: str) -> str:
    """SHA-256 hash of IP address — never store raw IP."""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()


@views_bp.post("/<slug>/view")
@limiter.limit("60 per minute")
def track_view(slug: str):
    build = Build.query.filter_by(slug=slug).first()
    if not build:
        return not_found("Build")

    ip = request.remote_addr or "unknown"
    ip_hash = _hash_ip(ip)

    # Rate limit: 1 view per IP per build per hour via Redis
    rate_key = f"forge:view:{ip_hash}:{slug}"
    if cache_get(rate_key) is not None:
        return "", 204  # Silently succeed — don't reveal rate limiting to frontend

    # Record the view
    build.view_count = (build.view_count or 0) + 1
    build.last_viewed_at = datetime.now(timezone.utc)

    view = BuildView(
        build_id=build.id,
        viewer_ip_hash=ip_hash,
    )
    db.session.add(view)
    db.session.commit()

    # Set rate limit key
    cache_set(rate_key, 1, _VIEW_RATE_TTL)

    return "", 204
