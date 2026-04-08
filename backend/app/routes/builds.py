"""
Builds Blueprint — /api/builds

GET    /api/builds                 → Paginated list with filters
POST   /api/builds                 → Create build (auth optional — anon builds allowed)
GET    /api/builds/<slug>          → Get single build (increments view_count)
PATCH  /api/builds/<slug>          → Update build (owner only)
DELETE /api/builds/<slug>          → Delete build (owner only)
POST   /api/builds/<slug>/vote     → Cast or toggle vote (auth required)
GET    /api/builds/meta/snapshot   → Aggregate meta stats
POST   /api/builds/<slug>/optimize → Ranked stat upgrades with explanations
GET    /api/builds/<slug>/optimize → Phase 4 sensitivity + ranking + efficiency (cached)
"""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app import db, limiter
from app.models import Build
from app.schemas import (
    BuildSchema,
    BuildListSchema,
    BuildCreateSchema,
    BuildUpdateSchema,
    VoteSchema,
)
from app.services import build_service
from app.utils.auth import login_required, get_current_user
from app.utils.responses import (
    ok, created, no_content, error,
    not_found, forbidden, validation_error,
    paginate_meta,
)
from app.utils.cache import get, set as cache_set, delete, delete_pattern, make_hash

builds_bp = Blueprint("builds", __name__)

build_schema = BuildSchema()
build_list_schema = BuildListSchema(many=True)
build_create_schema = BuildCreateSchema()
build_update_schema = BuildUpdateSchema()
vote_schema = VoteSchema()

_LIST_CACHE_TTL = 30     # seconds — short TTL since builds can be created often
_META_CACHE_TTL = 120    # seconds for meta snapshot
_OPTIMIZE_CACHE_TTL = 1800  # 30 minutes for optimization results

_BUILDS_LIST_KEY = "forge:builds:list"
_BUILDS_META_KEY = "forge:builds:meta"
_OPTIMIZE_CACHE_KEY = "forge:optimize"


def _invalidate_builds_cache() -> None:
    """Bust all build list and meta cache entries."""
    delete_pattern("forge:builds:list:*")
    delete_pattern("forge:builds:meta:*")


def _invalidate_optimize_cache(slug: str) -> None:
    """Bust optimization cache for a specific build."""
    delete_pattern(f"{_OPTIMIZE_CACHE_KEY}:{slug}:*")


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

@builds_bp.get("")
def list_builds():
    args = request.args

    try:
        page = int(args.get("page", 1))
        per_page = int(args.get("per_page", 20))
    except (TypeError, ValueError):
        return error("page and per_page must be integers.")

    # Boolean filter coercion
    def _bool(key):
        v = args.get(key)
        if v is None:
            return None
        return v.lower() in ("1", "true", "yes")

    filter_kwargs = dict(
        page=page,
        per_page=per_page,
        character_class=args.get("class"),
        mastery=args.get("mastery"),
        tier=args.get("tier"),
        is_ssf=_bool("ssf"),
        is_hc=_bool("hc"),
        is_ladder_viable=_bool("ladder"),
        is_budget=_bool("budget"),
        cycle=args.get("cycle"),
        sort=args.get("sort", "votes"),
        search=args.get("q"),
    )

    cache_key = f"{_BUILDS_LIST_KEY}:{make_hash(filter_kwargs)}"
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached["data"], meta=cached["meta"])
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    builds, total, pages = build_service.list_builds(**filter_kwargs)
    data = build_list_schema.dump(builds)
    meta = paginate_meta(page, per_page, total, pages)
    cache_set(cache_key, {"data": data, "meta": meta}, _LIST_CACHE_TTL)

    return ok(data=data, meta=meta)


# ---------------------------------------------------------------------------
# Meta snapshot (before <slug> routes to avoid "meta" matching as slug)
# ---------------------------------------------------------------------------

@builds_bp.get("/meta/snapshot")
def meta_snapshot():
    cached = get(_BUILDS_META_KEY)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp
    data = build_service.meta_snapshot()
    cache_set(_BUILDS_META_KEY, data, _META_CACHE_TTL)
    return ok(data=data)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def _validate_passive_tree(node_ids: list, character_class: str) -> str | None:
    """
    Validate every namespaced node ID in passive_tree against the DB.

    Returns the first invalid ID string, or None if all are valid.
    Integer IDs (legacy format) are skipped — they pre-date the namespaced
    system and cannot be checked against passive_nodes.
    """
    from app.models import PassiveNode
    for nid in node_ids:
        if not isinstance(nid, str):
            continue  # legacy integer IDs: skip
        node = db.session.get(PassiveNode, nid)
        if node is None or node.character_class != character_class:
            return nid
    return None


@builds_bp.post("")
@limiter.limit("20 per minute")
def create_build():
    try:
        data = build_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    passive_ids = data.get("passive_tree", [])
    if passive_ids:
        bad = _validate_passive_tree(passive_ids, data["character_class"])
        if bad:
            return error(f"Invalid passive node: {bad}")

    user = get_current_user()
    build = build_service.create_build(data, user_id=user.id if user else None)
    _invalidate_builds_cache()
    return created(data=build_schema.dump(build))


# ---------------------------------------------------------------------------
# Single build
# ---------------------------------------------------------------------------

@builds_bp.get("/<slug>")
def get_build(slug: str):
    build = build_service.get_build(slug, increment_views=True)
    if not build:
        return not_found("Build")

    result = build_schema.dump(build)

    user = get_current_user()
    if user:
        result["user_vote"] = build_service.get_user_vote(build.id, user.id)
    else:
        result["user_vote"] = 0

    return ok(data=result)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@builds_bp.patch("/<slug>")
@limiter.limit("20 per minute")
@login_required
def update_build(slug: str):
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    user = get_current_user()
    if build.author_id and build.author_id != user.id:
        return forbidden()

    try:
        data = build_update_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    build = build_service.update_build(build, data)
    _invalidate_builds_cache()
    _invalidate_optimize_cache(slug)
    return ok(data=build_schema.dump(build))


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@builds_bp.delete("/<slug>")
@limiter.limit("10 per minute")
@login_required
def delete_build(slug: str):
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    user = get_current_user()
    if build.author_id and build.author_id != user.id:
        return forbidden()

    build_service.delete_build(build)
    _invalidate_builds_cache()
    _invalidate_optimize_cache(slug)
    return no_content()


# ---------------------------------------------------------------------------
# Vote
# ---------------------------------------------------------------------------

@builds_bp.post("/<slug>/simulate")
@limiter.limit("10 per minute")
def simulate_build(slug: str):
    """
    Run the full simulation pipeline for a build.
    Returns DPS, defense, stat aggregation, and upgrade recommendations.
    No authentication required.
    """
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")
    result = build_service.simulate_build(build)
    return ok(data=result)


@builds_bp.post("/<slug>/optimize")
@limiter.limit("10 per minute")
def optimize_build(slug: str):
    """
    Dedicated optimization endpoint for a saved build.
    Returns ranked stat upgrades with DPS/EHP gain percentages and explanations.
    """
    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    result = build_service.simulate_build(build)
    return ok(data={
        "stat_upgrades": result.get("stat_upgrades", []),
        "primary_skill": result.get("primary_skill"),
        "skill_level": result.get("skill_level"),
    })


@builds_bp.get("/<slug>/optimize")
@limiter.limit("10 per minute")
def optimize_build_v2(slug: str):
    """
    Phase 4 optimization: sensitivity analysis + ranked upgrades + efficiency scoring.

    Query params:
        mode: "balanced" (default), "offense", or "defense"

    Returns stat_rankings, top_upgrade_candidates, mode, and generated_at.
    Cached in Redis for 30 minutes per slug+mode. Invalidated on build update.
    """
    from datetime import datetime, timezone
    from flask import current_app
    from app.engines.sensitivity_analyzer import analyze_sensitivity
    from app.engines.upgrade_ranker import rank_upgrades, VALID_MODES
    from app.engines.efficiency_scorer import score_affix_efficiency

    mode = request.args.get("mode", "balanced")
    if mode not in VALID_MODES:
        return error(f"Invalid mode '{mode}'. Must be one of: {', '.join(sorted(VALID_MODES))}")

    # Check cache
    cache_key = f"{_OPTIMIZE_CACHE_KEY}:{slug}:{mode}"
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    build = build_service.get_build(slug)
    if not build:
        return not_found("Build")

    # Run the simulation pipeline to get resolved stats
    sim = build_service.simulate_build(build)
    primary_skill = sim.get("primary_skill") or ""
    skill_level = sim.get("skill_level", 20)

    # Reconstruct BuildStats from the simulation stats dict
    from app.engines.stat_engine import BuildStats
    stats = BuildStats(**{k: v for k, v in sim["stats"].items() if hasattr(BuildStats, k)})

    # 1. Sensitivity analysis
    sensitivity = analyze_sensitivity(stats, primary_skill, skill_level)

    # 2. Rank upgrades by mode
    ranking = rank_upgrades(sensitivity, mode=mode)

    # 3. Efficiency scoring against all available affixes
    affix_registry = current_app.extensions.get("affix_registry")
    candidates_data = []
    if affix_registry:
        all_affixes = [affix.to_dict() for affix in affix_registry.all()]
        efficiency = score_affix_efficiency(
            stats, all_affixes, primary_skill, skill_level,
            top_n=10,
            offense_weight=ranking.offense_weight,
            defense_weight=ranking.defense_weight,
        )
        candidates_data = [c.to_dict() for c in efficiency.candidates]

    result = {
        "stat_rankings": [s.to_dict() for s in ranking.stat_rankings],
        "top_upgrade_candidates": candidates_data,
        "mode": ranking.mode,
        "offense_weight": ranking.offense_weight,
        "defense_weight": ranking.defense_weight,
        "base_dps": round(sensitivity.base_dps, 2),
        "base_ehp": round(sensitivity.base_ehp, 2),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    cache_set(cache_key, result, _OPTIMIZE_CACHE_TTL)
    return ok(data=result)


@builds_bp.post("/<slug>/vote")
@login_required
@limiter.limit("30 per minute")
def vote(slug: str):
    build = Build.query.filter_by(slug=slug).first()
    if not build:
        return not_found("Build")

    try:
        data = vote_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    user = get_current_user()
    result = build_service.cast_vote(build, user.id, data["direction"])
    _invalidate_builds_cache()
    return ok(data=result)
