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
"""

from flask import Blueprint, request
from marshmallow import ValidationError

from app import limiter
from app.models import PassiveNode
from app.schemas.simulate import (
    SimulateStatsSchema,
    SimulateCombatSchema,
    SimulateDefenseSchema,
    SimulateOptimizeSchema,
    SimulateBuildSchema,
)
from app.services import simulation_service
from app.utils.responses import ok, error, validation_error


simulate_bp = Blueprint("simulate", __name__)

stats_schema = SimulateStatsSchema()
combat_schema = SimulateCombatSchema()
defense_schema = SimulateDefenseSchema()
optimize_schema = SimulateOptimizeSchema()
build_schema = SimulateBuildSchema()


def _load_passive_nodes(character_class: str) -> list[dict]:
    """Load passive nodes for a class from the database."""
    db_nodes = PassiveNode.query.filter_by(character_class=character_class).all()
    return [{"id": n.id, "type": n.node_type, "name": n.name} for n in db_nodes]


@simulate_bp.post("/stats")
@limiter.limit("30 per minute")
def simulate_stats():
    """Aggregate all character stats from class, mastery, passives, and gear."""
    try:
        data = stats_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    nodes = _load_passive_nodes(data["character_class"])
    stats = simulation_service.aggregate_stats(
        character_class=data["character_class"],
        mastery=data["mastery"],
        allocated_node_ids=data.get("allocated_node_ids", []),
        nodes=nodes,
        gear_affixes=data.get("gear_affixes", []),
    )
    return ok(data=stats.to_dict())


@simulate_bp.post("/combat")
@limiter.limit("20 per minute")
def simulate_combat():
    """Calculate DPS and run Monte Carlo variance simulation."""
    try:
        data = combat_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    result = simulation_service.simulate_combat(
        stats_dict=data["stats"],
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        n_simulations=data.get("n_simulations", 10_000),
        seed=data.get("seed"),
    )
    return ok(data=result)


@simulate_bp.post("/defense")
@limiter.limit("30 per minute")
def simulate_defense():
    """Calculate EHP, resistances, ward sustainability, and survivability score."""
    try:
        data = defense_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    result = simulation_service.simulate_defense(stats_dict=data["stats"])
    return ok(data=result)


@simulate_bp.post("/optimize")
@limiter.limit("10 per minute")
def simulate_optimize():
    """Rank stat upgrades by DPS and EHP gain percentage."""
    try:
        data = optimize_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    result = simulation_service.simulate_optimize(
        stats_dict=data["stats"],
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        top_n=data.get("top_n", 5),
    )
    return ok(data=result)


@simulate_bp.post("/build")
@limiter.limit("10 per minute")
def simulate_build():
    """Full pipeline: aggregate stats → DPS → defense → optimization."""
    try:
        data = build_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    nodes = _load_passive_nodes(data["character_class"])
    result = simulation_service.simulate_full_build(
        character_class=data["character_class"],
        mastery=data["mastery"],
        allocated_node_ids=data.get("allocated_node_ids", []),
        nodes=nodes,
        gear_affixes=data.get("gear_affixes", []),
        skill_name=data["skill_name"],
        skill_level=data.get("skill_level", 20),
        n_simulations=data.get("n_simulations", 5_000),
        seed=data.get("seed"),
    )
    return ok(data=result)
