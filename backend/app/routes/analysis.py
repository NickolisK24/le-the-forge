"""
Analysis Blueprint — /api/builds/<slug>/analysis

Advanced build analysis endpoints:
  GET /api/builds/<slug>/analysis/boss/<boss_id>   — Boss encounter simulation
  GET /api/builds/<slug>/analysis/corruption        — Corruption scaling curve
  GET /api/builds/<slug>/analysis/gear-upgrades     — Gear upgrade ranking
"""

from flask import Blueprint, request

from app import limiter
from app.services import build_service
from app.services.build_analysis_service import analyze_build
from app.engines.boss_encounter import simulate_boss_encounter
from app.engines.corruption_scaler import scale_corruption
from app.engines.gear_upgrade_ranker import rank_gear_upgrades
from app.engines.stat_engine import BuildStats
from app.utils.responses import ok, error as err_response, not_found
from app.utils.cache import cached_route, delete_pattern
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

analysis_bp = Blueprint("analysis", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_boss(boss_id: str) -> dict | None:
    """Load a boss profile from the game data pipeline."""
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        if pipeline and hasattr(pipeline, "enemies"):
            for enemy in pipeline.enemies:
                profile = enemy.to_dict() if hasattr(enemy, "to_dict") else enemy
                if profile.get("id") == boss_id:
                    return profile
    except RuntimeError:
        pass
    return None


def _load_all_bosses() -> list[dict]:
    """Load all boss/enemy profiles from the game data pipeline."""
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        if pipeline and hasattr(pipeline, "enemies"):
            return [
                e.to_dict() if hasattr(e, "to_dict") else e
                for e in pipeline.enemies
            ]
    except RuntimeError:
        pass
    return []


def _default_boss_id() -> str:
    """Return a sensible default boss for corruption scaling."""
    return "boss_standard"


def _resolve_build_stats(build) -> tuple[BuildStats | None, dict | None, str, int]:
    """Resolve a build into BuildStats + metadata needed for engines.

    Returns (stats_or_none, analysis_dict_or_none, primary_skill, skill_level).
    """
    try:
        analysis = analyze_build(build)
        from app.engines.stat_engine import BuildStats as BS
        stats_dict = analysis.get("stats", {})
        stats = BS(**{k: v for k, v in stats_dict.items() if hasattr(BS, k)})
        primary_skill = analysis.get("primary_skill", "")
        skill_level = analysis.get("skill_level", 20)
        return stats, analysis, primary_skill, skill_level
    except Exception as exc:
        log.warning("analysis.resolve_stats_failed", error=str(exc))
        return None, None, "", 20


# ---------------------------------------------------------------------------
# GET /api/builds/<slug>/analysis/boss/<boss_id>
# ---------------------------------------------------------------------------

@analysis_bp.get("/<slug>/analysis/boss/<boss_id>")
@limiter.limit("10 per minute")
def boss_analysis(slug: str, boss_id: str):
    """Run boss encounter simulation for a build against a specific boss."""
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    boss = _load_boss(boss_id)
    if not boss:
        return not_found("Boss")

    # Parse corruption query param
    corruption_str = request.args.get("corruption", "0")
    try:
        corruption = int(corruption_str)
    except (ValueError, TypeError):
        return err_response("corruption must be an integer", 400)

    if corruption < 0 or corruption > 500:
        return err_response("corruption must be between 0 and 500", 400)

    # Check cache
    from app.utils.cache import get as cache_get, set as cache_set
    cache_key = f"forge:analysis:boss:{slug}:{boss_id}:{corruption}"
    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    stats, analysis, primary_skill, skill_level = _resolve_build_stats(build)
    if stats is None:
        return err_response("Could not resolve build stats for analysis", 422)

    # Apply corruption scaling
    from app.engines.corruption_scaler import health_multiplier, damage_multiplier
    hp_mult = health_multiplier(corruption)
    dmg_mult = damage_multiplier(corruption)

    result = simulate_boss_encounter(
        stats, boss, primary_skill, skill_level,
        corruption=corruption,
        health_multiplier=hp_mult,
        damage_multiplier=dmg_mult,
    )

    data = result.to_dict()
    cache_set(cache_key, data, ttl=1800)
    return ok(data=data)


# ---------------------------------------------------------------------------
# GET /api/builds/<slug>/analysis/corruption
# ---------------------------------------------------------------------------

@analysis_bp.get("/<slug>/analysis/corruption")
@limiter.limit("10 per minute")
def corruption_analysis(slug: str):
    """Run corruption scaling analysis across standard breakpoints."""
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    boss_id = request.args.get("boss_id", _default_boss_id())
    boss = _load_boss(boss_id)
    if not boss:
        return not_found("Boss")

    # Check cache
    from app.utils.cache import get as cache_get, set as cache_set
    cache_key = f"forge:analysis:corruption:{slug}:{boss_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    stats, analysis, primary_skill, skill_level = _resolve_build_stats(build)
    if stats is None:
        return err_response("Could not resolve build stats for analysis", 422)

    result = scale_corruption(stats, boss, primary_skill, skill_level)
    data = result.to_dict()
    cache_set(cache_key, data, ttl=1800)
    return ok(data=data)


# ---------------------------------------------------------------------------
# GET /api/builds/<slug>/analysis/gear-upgrades
# ---------------------------------------------------------------------------

@analysis_bp.get("/<slug>/analysis/gear-upgrades")
@limiter.limit("10 per minute")
def gear_upgrades(slug: str):
    """Rank gear upgrade candidates for a build."""
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    slot = request.args.get("slot")

    # Check cache
    from app.utils.cache import get as cache_get, set as cache_set
    cache_key = f"forge:analysis:gear:{slug}:{slot or 'all'}"
    cached = cache_get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    stats, analysis, primary_skill, skill_level = _resolve_build_stats(build)
    if stats is None:
        return err_response("Could not resolve build stats for analysis", 422)

    # Build a dict representation for the gear ranker
    build_dict = {
        "character_class": build.character_class,
        "mastery": build.mastery,
        "passive_tree": build.passive_tree or [],
        "gear": build.gear or [],
        "nodes": [],
    }

    result = rank_gear_upgrades(
        stats, build_dict, primary_skill, skill_level,
        slot_filter=slot,
    )

    data = result.to_dict()
    cache_set(cache_key, data, ttl=1800)
    return ok(data=data)
