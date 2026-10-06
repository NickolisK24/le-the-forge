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
        damage_events:    [ { time, target_id, damage, overkill, killed } ],
        damage_events_total:     int,   (events generated)
        damage_events_truncated: bool,  (true when only the first
                                         MAX_RETURNED_EVENTS are returned)
    }

    Requests are bounded before any simulation state is built: duration,
    tick size, target count, and the step budget (ticks x targets), so one
    anonymous request cannot allocate unbounded memory.
"""

import math


from flask import Blueprint, request
from marshmallow import Schema, fields, ValidationError, validate, validates, validates_schema

from app import limiter
from app.utils.responses import ok, validation_error, error

multi_target_bp = Blueprint("multi_target", __name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

# Request bounds. The simulator UI allows tick 0.01–1 s and duration 1–300 s,
# and the largest template has 10 targets. Measured cost is roughly linear in
# steps (ticks x targets): 120k steps ≈ 0.4 s and ~110 MB peak; the audit's
# 3.6M-step request took 17 s and 1.7 GB.
MAX_DURATION_SECONDS = 300.0
MIN_TICK_SECONDS = 0.01
MAX_TICK_SECONDS = 10.0
MAX_TARGETS = 20
MAX_SIMULATION_STEPS = 120_000
MAX_RETURNED_EVENTS = 5_000
MAX_HEALTH = 1e12
MAX_BASE_DAMAGE = 1e9


def simulation_steps(max_duration: float, tick_size: float, target_count: int) -> int:
    return math.ceil(max_duration / tick_size) * max(target_count, 1)


class _TargetSpec(Schema):
    target_id      = fields.Str(required=True, validate=validate.Length(min=1, max=64))
    max_health     = fields.Float(
        required=True,
        validate=validate.Range(min=0, max=MAX_HEALTH, min_inclusive=False),
    )
    position_index = fields.Int(load_default=0, validate=validate.Range(min=0, max=MAX_TARGETS))


class MultiTargetSimulateSchema(Schema):
    base_damage    = fields.Float(required=True, validate=validate.Range(max=MAX_BASE_DAMAGE))
    distribution   = fields.Str(load_default="full_aoe")
    selection_mode = fields.Str(load_default="all_targets")
    tick_size      = fields.Float(
        load_default=0.1,
        validate=validate.Range(min=MIN_TICK_SECONDS, max=MAX_TICK_SECONDS),
    )
    max_duration   = fields.Float(
        load_default=60.0,
        validate=validate.Range(max=MAX_DURATION_SECONDS),
    )
    template       = fields.Str(load_default=None, allow_none=True)
    targets        = fields.List(
        fields.Nested(_TargetSpec), load_default=list,
        validate=validate.Length(max=MAX_TARGETS),
    )

    @validates_schema
    def _validate_step_budget(self, data, **kwargs):
        targets = data.get("targets") or []
        if data.get("template") or not targets:
            return  # template sizes are checked in the route
        steps = simulation_steps(data["max_duration"], data["tick_size"], len(targets))
        if steps > MAX_SIMULATION_STEPS:
            raise ValidationError(
                f"Simulation too large: {steps} steps (duration / tick_size x targets); "
                f"the limit is {MAX_SIMULATION_STEPS}. Increase tick_size or shorten max_duration.",
                field_name="max_duration",
            )

    @validates("base_damage")
    def _validate_damage(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("base_damage must be > 0")

    @validates("max_duration")
    def _validate_duration(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("max_duration must be > 0")

    @validates("tick_size")
    def _validate_tick(self, value, **kwargs):
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

    target_count = len(manager.all_targets())
    steps = simulation_steps(data["max_duration"], data["tick_size"], target_count)
    if target_count > MAX_TARGETS or steps > MAX_SIMULATION_STEPS:
        return error(
            f"Simulation too large: {steps} steps for {target_count} targets; "
            f"the limit is {MAX_SIMULATION_STEPS} steps and {MAX_TARGETS} targets.",
            422,
        )

    state = MultiTargetState(manager=manager)
    result = MultiTargetEncounterEngine().run(
        state=state,
        base_damage=data["base_damage"],
        distribution=data["distribution"],
        selection_mode=data["selection_mode"],
        tick_size=data["tick_size"],
        max_duration=data["max_duration"],
    )

    events = result.damage_events
    return ok(data={
        "cleared":       result.cleared,
        "time_to_clear": result.time_to_clear,
        "total_kills":   result.total_kills,
        "metrics":       result.metrics,
        "damage_events": events[:MAX_RETURNED_EVENTS],
        "damage_events_total": len(events),
        "damage_events_truncated": len(events) > MAX_RETURNED_EVENTS,
    })
