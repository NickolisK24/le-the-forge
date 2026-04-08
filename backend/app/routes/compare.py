"""
Compare Blueprint — /api/compare

GET /api/compare/<slug_a>/<slug_b> → Side-by-side simulation comparison
"""

from flask import Blueprint

from app import limiter
from app.services import build_service
from app.services.build_analysis_service import analyze_build
from app.engines.comparison_engine import compare_builds
from app.engines.stat_engine import BuildStats
from app.utils.responses import ok, error, not_found
from app.utils.cache import get as cache_get, set as cache_set

compare_bp = Blueprint("compare", __name__)

_COMPARE_CACHE_TTL = 1200  # 20 minutes


def _resolve_stats(build):
    """Run the analysis pipeline and reconstruct BuildStats from the result."""
    analysis = analyze_build(build)
    stats_dict = analysis.get("stats", {})
    valid = {k: v for k, v in stats_dict.items() if hasattr(BuildStats, k)}
    stats = BuildStats(**valid)
    primary_skill = analysis.get("primary_skill") or ""
    skill_level = analysis.get("skill_level", 20)
    return stats, primary_skill, skill_level


@compare_bp.get("/<slug_a>/<slug_b>")
@limiter.limit("15 per minute")
def compare(slug_a: str, slug_b: str):
    if slug_a == slug_b:
        return error("Cannot compare a build to itself.", status=400)

    # Alphabetically sort for cache key to avoid duplicate entries
    sorted_slugs = tuple(sorted([slug_a, slug_b]))
    cache_key = f"forge:compare:{sorted_slugs[0]}:{sorted_slugs[1]}"

    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    build_a = build_service.get_build(slug_a)
    if not build_a:
        return not_found("Build A")

    build_b = build_service.get_build(slug_b)
    if not build_b:
        return not_found("Build B")

    try:
        stats_a, skill_a, level_a = _resolve_stats(build_a)
        stats_b, skill_b, level_b = _resolve_stats(build_b)
    except Exception:
        return error("One or both builds cannot be simulated (missing skills or class data).", status=422)

    result = compare_builds(
        build_a, build_b,
        stats_a, stats_b,
        skill_a, skill_b,
        level_a, level_b,
    )

    data = result.to_dict()
    cache_set(cache_key, data, _COMPARE_CACHE_TTL)
    return ok(data=data)
