"""
Multi-Target Blueprint — /api/simulate/multi-target

POST /api/simulate/multi-target
    Execute a multi-target encounter simulation.

    Input: {
        base_damage:     float,           (damage per second)
        distribution:    str,             (default "full_aoe")
        selection_mode:  str,             (default "all_targets")
        tick_size:       float,           (default 0.1)
        max_duration:    float,           (default 60.0)
        template:        str | null,      ("single_boss"|"elite_pack"|"mob_swarm")
        targets: [                        (if template omitted)
            { target_id, max_health, position_index? }
        ]
    }

    Output: {
        cleared:          bool,
        time_to_clear:    float | null,
        total_kills:      int,
        metrics:          { total_kills, time_to_clear, damage_per_target,
                            overkill_waste, kill_times },
        damage_events:    [ { time, target_id, damage, overkill, killed } ]
    }
"""

from flask import Blueprint, request
from marshmallow import Schema, fields, ValidationError, validates

from app import limiter
from app.utils.responses import ok, validation_error, error

multi_target_bp = Blueprint("multi_target", __name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class _TargetSpec(Schema):
    target_id      = fields.Str(required=True)
    max_health     = fields.Float(required=True)
    position_index = fields.Int(load_default=0)


class MultiTargetSimulateSchema(Schema):
    base_damage    = fields.Float(required=True)
    distribution   = fields.Str(load_default="full_aoe")
    selection_mode = fields.Str(load_default="all_targets")
    tick_size      = fields.Float(load_default=0.1)
    max_duration   = fields.Float(load_default=60.0)
    template       = fields.Str(load_default=None, allow_none=True)
    targets        = fields.List(fields.Nested(_TargetSpec), load_default=list)

    @validates("base_damage")
    def _validate_damage(self, value):
        if value <= 0:
            raise ValidationError("base_damage must be > 0")

    @validates("max_duration")
    def _validate_duration(self, value):
        if value <= 0:
            raise ValidationError("max_duration must be > 0")

    @validates("tick_size")
    def _validate_tick(self, value):
        if value <= 0:
            raise ValidationError("tick_size must be > 0")


_schema = MultiTargetSimulateSchema()


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@multi_target_bp.post("/multi-target")
@limiter.limit("20 per minute")
def simulate_multi_target():
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    from targets.target_templates import TEMPLATES, custom, TargetSpec
    from targets.target_manager import TargetManager
    from targets.models.target_entity import TargetEntity
    from state.multi_target_state import MultiTargetState
    from app.services.multi_target_encounter import MultiTargetEncounterEngine
    from damage.multi_target_distribution import VALID_DISTRIBUTIONS
    from targets.target_selector import VALID_MODES

    # Validate distribution / selection
    if data["distribution"] not in VALID_DISTRIBUTIONS:
        return error(f"distribution must be one of: {sorted(VALID_DISTRIBUTIONS)}", 422)
    if data["selection_mode"] not in VALID_MODES:
        return error(f"selection_mode must be one of: {sorted(VALID_MODES)}", 422)

    # Build target manager
    tmpl = data.get("template")
    if tmpl:
        if tmpl not in TEMPLATES:
            return error(f"Unknown template {tmpl!r}", 422)
        manager = TEMPLATES[tmpl]()
    else:
        raw_targets = data.get("targets") or []
        if not raw_targets:
            return error("Provide at least one target or a template", 422)
        try:
            specs = [TargetSpec(t["target_id"], t["max_health"], t.get("position_index", 0))
                     for t in raw_targets]
            manager = custom(specs)
        except (ValueError, KeyError) as exc:
            return error(str(exc), 422)

    state = MultiTargetState(manager=manager)
    result = MultiTargetEncounterEngine().run(
        state=state,
        base_damage=data["base_damage"],
        distribution=data["distribution"],
        selection_mode=data["selection_mode"],
        tick_size=data["tick_size"],
        max_duration=data["max_duration"],
    )

    return ok(data={
        "cleared":       result.cleared,
        "time_to_clear": result.time_to_clear,
        "total_kills":   result.total_kills,
        "metrics":       result.metrics,
        "damage_events": result.damage_events,
    })
