"""
Rotation Blueprint — /api/simulate/rotation

POST /api/simulate/rotation
    Execute a skill rotation against an encounter and return damage metrics.

    Input:  { rotation, skills, duration?, gcd?, encounter? }
    Output: {
        total_damage, dps, total_casts,
        rotation_metrics: { total_damage, total_casts, dps, uptime_fraction,
                             idle_time, efficiency, cast_counts, damage_by_skill,
                             avg_cast_interval },
        cast_results: [ { skill_id, cast_at, resolves_at, damage }, ... ]
    }
"""

from flask import Blueprint, request
from marshmallow import ValidationError

from app import limiter
from app.schemas.rotation import SimulateRotationSchema
from app.utils.responses import ok, error, validation_error

rotation_bp = Blueprint("rotation", __name__)

_schema = SimulateRotationSchema()


@rotation_bp.post("/rotation")
@limiter.limit("10 per minute")
def simulate_rotation():
    """Execute a skill rotation and return encounter metrics."""
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    from skills.models.skill_definition import SkillDefinition
    from rotation.models.rotation_definition import RotationDefinition
    from rotation.models.rotation_step import RotationStep
    from services.rotation_integration import simulate_rotation_encounter

    # Build skill registry from inline definitions
    skill_registry = {
        s["skill_id"]: SkillDefinition(
            skill_id      = s["skill_id"],
            base_damage   = s.get("base_damage",   0.0),
            cast_time     = s.get("cast_time",     0.0),
            cooldown      = s.get("cooldown",      0.0),
            resource_cost = s.get("resource_cost", 0.0),
            tags          = s.get("tags",          []),
        )
        for s in data["skills"]
    }

    # Build rotation definition
    raw_rot = data["rotation"]
    rotation = RotationDefinition(
        rotation_id = raw_rot.get("rotation_id", "custom"),
        steps = [
            RotationStep(
                skill_id         = step["skill_id"],
                delay_after_cast = step.get("delay_after_cast", 0.0),
                priority         = step.get("priority",         0),
                repeat_count     = step.get("repeat_count",     1),
            )
            for step in raw_rot.get("steps", [])
        ],
        loop = raw_rot.get("loop", True),
    )

    # Build encounter kwargs
    encounter_kwargs = None
    if data.get("encounter"):
        enc = data["encounter"]
        encounter_kwargs = {
            "enemy_template": enc.get("enemy_template", "TRAINING_DUMMY"),
            "fight_duration": enc.get("fight_duration", data["duration"]),
            "tick_size":      enc.get("tick_size",      0.1),
            "distribution":   enc.get("distribution",   "SINGLE"),
            "crit_chance":    enc.get("crit_chance",    0.0),
            "crit_multiplier":enc.get("crit_multiplier",2.0),
        }

    try:
        result = simulate_rotation_encounter(
            rotation         = rotation,
            skill_registry   = skill_registry,
            duration         = data["duration"],
            gcd              = data.get("gcd", 0.0),
            encounter_kwargs = encounter_kwargs,
        )
    except Exception as e:
        return error(f"Rotation simulation failed: {e}", status=500)

    m = result.rotation_metrics
    return ok(data={
        "total_damage":  result.total_damage,
        "dps":           result.dps,
        "total_casts":   result.total_casts,
        "rotation_metrics": {
            "total_damage":      m.total_damage,
            "total_casts":       m.total_casts,
            "duration_used":     m.duration_used,
            "dps":               m.dps,
            "uptime_fraction":   m.uptime_fraction,
            "idle_time":         m.idle_time,
            "efficiency":        m.efficiency,
            "cast_counts":       m.cast_counts,
            "damage_by_skill":   m.damage_by_skill,
            "avg_cast_interval": m.avg_cast_interval,
        },
        "cast_results": result.cast_results,
    })
