"""
Report Blueprint — /api/builds/<slug>/report

GET /api/builds/<slug>/report → Full build report for sharing
"""

from flask import Blueprint

from app import limiter
from app.models import Build
from app.services import build_report_service
from app.services.build_access import load_readable_build
from app.utils.responses import ok, error, not_found, forbidden
from app.utils.cache import get as cache_get, set as cache_set

report_bp = Blueprint("report", __name__)

_REPORT_CACHE_TTL = 3600  # 1 hour


@report_bp.get("/<slug>/report")
@limiter.limit("20 per minute")
def get_report(slug: str):
    # Access control (public, owner, or anonymous-link build) runs before the
    # cache lookup so cached reports never bypass visibility.
    build, denied = load_readable_build(slug)
    if denied:
        return denied

    # Check cache
    cache_key = f"forge:report:{slug}"
    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    try:
        data = build_report_service.generate_report(build)
    except Exception:
        return error(
            "Cannot generate report — build may be missing skills or class data.",
            status=422,
        )

    cache_set(cache_key, data, _REPORT_CACHE_TTL)
    return ok(data=data)
