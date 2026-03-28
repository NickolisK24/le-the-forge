"""
Simulate Blueprint — /api/simulate

Stateless simulation endpoints. The frontend sends raw build/stats data
and gets back computed results — no saved build or session required.

These endpoints make the backend the single source of truth for all
simulation math. The frontend should call these instead of duplicating
engine logic in TypeScript.

POST /api/simulate/stats    → aggregate stats from class/mastery/passives/gear
POST /api/simulate/combat   → DPS + Monte Carlo from stats + skill
POST /api/simulate/defense  → EHP + survivability from stats
POST /api/simulate/optimize → stat upgrade recommendations from stats + skill
POST /api/simulate/build    → full pipeline (stats → combat → defense → optimize)

Async mode
----------
The two expensive endpoints (/combat and /build) accept an optional
``"async": true`` field in the request body.  When set the simulation is
submitted to the background job pool and the response is:

    {"data": {"job_id": "a1b2c3d4"}, ...}   (HTTP 202)

The client then polls GET /api/jobs/<job_id> until status == "done".
"""

from flask import Blueprint, request
from marshmallow import ValidationError

from app import limiter
from app.models import PassiveNode
from app.services.passive_stat_resolver import resolve_passive_stats
from app.schemas.simulate import (
    SimulateStatsSchema,
    SimulateCombatSchema,
    SimulateDefenseSchema,
    SimulateOptimizeSchema,
    SimulateSensitivitySchema,
    SimulateBuildSchema,
)
from app.services import simulation_service
from app.utils.responses import ok, error, validation_error
from app.utils.cache import get, set as cache_set, make_hash


simulate_bp = Blueprint("simulate", __name__)

stats_schema = SimulateStatsSchema()
combat_schema = SimulateCombatSchema()
defense_schema = SimulateDefenseSchema()
optimize_schema = SimulateOptimizeSchema()
sensitivity_schema = SimulateSensitivitySchema()
build_schema = SimulateBuildSchema()

_SIM_CACHE_TTL = 300  # 5 minutes for simulation results


def _load_passive_nodes(character_class: str) -> list[dict]:
    """Load passive nodes for a class from the database."""
    db_nodes = PassiveNode.query.filter_by(character_class=character_class).all()
    return [{"id": n.id, "type": n.node_type, "name": n.name} for n in db_nodes]


def _sim_cache_key(prefix: str, data: dict) -> str:
    return f"forge:sim:{prefix}:{make_hash(data)}"


@simulate_bp.post("/stats")
@limiter.limit("30 per minute")
def simulate_stats():
    """Aggregate all character stats from class, mastery, passives, and gear."""
    try:
        data = stats_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    cache_key = _sim_cache_key("stats", data)
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    nodes = _load_passive_nodes(data["character_class"])
    passive_tree = data.get("passive_tree", [])
    passive_stats = resolve_passive_stats(passive_tree) if passive_tree else None
    stats = simulation_service.aggregate_stats(
        character_class=data["character_class"],
        mastery=data["mastery"],
        allocated_node_ids=data.get("allocated_node_ids", []),
        nodes=nodes,
        gear_affixes=data.get("gear_affixes", []),
        passive_stats=passive_stats,
    )
    result = stats.to_dict()
    if passive_stats and passive_stats.get("special_effects"):
        result["special_effects"] = passive_stats["special_effects"]
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)


@simulate_bp.post("/combat")
@limiter.limit("20 per minute")
def simulate_combat():
    """Calculate DPS and run Monte Carlo variance simulation.

    Pass ``"async": true`` in the request body to run in the background.
    Returns ``{"job_id": "..."}`` (HTTP 202) which you poll at GET /api/jobs/<id>.
    """
    try:
        data = combat_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    run_async = data.pop("async", False) if isinstance(data, dict) else False

    cache_key = _sim_cache_key("combat", data)
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    if run_async:
        from app.utils import jobs
        job_id = jobs.enqueue(
            simulation_service.simulate_combat,
            stats_dict=data["stats"],
            skill_name=data["skill_name"],
            skill_level=data.get("skill_level", 20),
            n_simulations=data.get("n_simulations", 10_000),
            seed=data.get("seed"),
        )
        return ok(data={"job_id": job_id}), 202

    result = simulation_service.simulate_combat(
        stats_dict=data["stats"],
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        n_simulations=data.get("n_simulations", 10_000),
        seed=data.get("seed"),
    )
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)


@simulate_bp.post("/defense")
@limiter.limit("30 per minute")
def simulate_defense():
    """Calculate EHP, resistances, ward sustainability, and survivability score."""
    try:
        data = defense_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    cache_key = _sim_cache_key("defense", data)
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    result = simulation_service.simulate_defense(stats_dict=data["stats"])
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)


@simulate_bp.post("/optimize")
@limiter.limit("10 per minute")
def simulate_optimize():
    """Rank stat upgrades by DPS and EHP gain percentage."""
    try:
        data = optimize_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    cache_key = _sim_cache_key("optimize", data)
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    result = simulation_service.simulate_optimize(
        stats_dict=data["stats"],
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        top_n=data.get("top_n", 5),
    )
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)


@simulate_bp.post("/sensitivity")
@limiter.limit("10 per minute")
def simulate_sensitivity():
    """Stat sensitivity analysis — which stats give the most marginal value."""
    try:
        data = sensitivity_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    cache_key = _sim_cache_key("sensitivity", data)
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    result = simulation_service.simulate_sensitivity(
        stats_dict=data["stats"],
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        stat_keys=data.get("stat_keys"),
        delta=data.get("delta", 10.0),
    )
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)


@simulate_bp.post("/build")
@limiter.limit("10 per minute")
def simulate_build():
    """Full pipeline: aggregate stats → DPS → defense → optimization.

    Pass ``"async": true`` in the request body to run in the background.
    Returns ``{"job_id": "..."}`` (HTTP 202) which you poll at GET /api/jobs/<id>.
    """
    try:
        data = build_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    run_async = data.pop("async", False) if isinstance(data, dict) else False

    # Resolve nodes synchronously (DB access must stay in request thread)
    nodes = _load_passive_nodes(data["character_class"])
    passive_tree = data.get("passive_tree", [])
    passive_stats = resolve_passive_stats(passive_tree) if passive_tree else None

    cache_key = _sim_cache_key("build", {**data, "nodes": nodes})
    cached = get(cache_key)
    if cached is not None:
        resp = ok(data=cached)
        resp[0].headers["X-Cache"] = "HIT"
        return resp

    sim_kwargs = dict(
        character_class=data["character_class"],
        mastery=data["mastery"],
        allocated_node_ids=data.get("allocated_node_ids", []),
        nodes=nodes,
        gear_affixes=data.get("gear_affixes", []),
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        n_simulations=data.get("n_simulations", 5_000),
        seed=data.get("seed"),
        passive_stats=passive_stats,
    )

    if run_async:
        from app.utils import jobs
        job_id = jobs.enqueue(simulation_service.simulate_full_build, **sim_kwargs)
        return ok(data={"job_id": job_id}), 202

    result = simulation_service.simulate_full_build(**sim_kwargs)
    cache_set(cache_key, result, _SIM_CACHE_TTL)
    return ok(data=result)
