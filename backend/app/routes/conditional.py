"""
Conditional Blueprint — /api/simulate/conditional

POST /api/simulate/conditional
    Evaluate conditional modifiers against a simulation state snapshot
    and return adjusted damage with an audit of which modifiers fired.

    Input: {
        base_damage:  float,
        state: {
            player_health_pct: float,   (0.0–1.0)
            target_health_pct: float,   (0.0–1.0)
            elapsed_time:      float,
            active_buffs:      [str],
            active_status_effects: {str: int}
        },
        modifiers: [
            {
                modifier_id:   str,
                stat_target:   str,
                value:         float,
                modifier_type: "additive" | "multiplicative" | "override",
                condition: {
                    condition_id:        str,
                    condition_type:      str,
                    threshold_value:     float | null,
                    comparison_operator: str,
                    duration:            float | null
                }
            }
        ]
    }

    Output: {
        base_damage:          float,
        adjusted_damage:      float,
        damage_multiplier:    float,
        active_modifier_ids:  [str],
        stat_deltas:          {stat: float}
    }
"""

from flask import Blueprint, request
from marshmallow import Schema, fields, validates, ValidationError, post_load

from app import limiter
from app.utils.responses import ok, validation_error

conditional_bp = Blueprint("conditional", __name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class _ConditionSchema(Schema):
    condition_id        = fields.Str(required=True)
    condition_type      = fields.Str(required=True)
    threshold_value     = fields.Float(load_default=None)
    comparison_operator = fields.Str(load_default="lt")
    duration            = fields.Float(load_default=None)


class _ModifierSchema(Schema):
    modifier_id   = fields.Str(required=True)
    stat_target   = fields.Str(required=True)
    value         = fields.Float(required=True)
    modifier_type = fields.Str(required=True)
    condition     = fields.Nested(_ConditionSchema, required=True)


class _StateSchema(Schema):
    player_health_pct     = fields.Float(load_default=1.0)
    target_health_pct     = fields.Float(load_default=1.0)
    elapsed_time          = fields.Float(load_default=0.0)
    active_buffs          = fields.List(fields.Str(), load_default=list)
    active_status_effects = fields.Dict(keys=fields.Str(), values=fields.Int(), load_default=dict)


class ConditionalSimulateSchema(Schema):
    base_damage = fields.Float(required=True)
    state       = fields.Nested(_StateSchema, load_default=dict)
    modifiers   = fields.List(fields.Nested(_ModifierSchema), load_default=list)

    @validates("base_damage")
    def _validate_damage(self, value, **kwargs):
        if value < 0:
            raise ValidationError("base_damage must be >= 0")


_schema = ConditionalSimulateSchema()


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@conditional_bp.post("/conditional")
@limiter.limit("30 per minute")
def simulate_conditional():
    """Evaluate conditional modifiers and return adjusted damage."""
    try:
        data = _schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    from state.state_engine import SimulationState
    from conditions.models.condition import Condition
    from modifiers.models.conditional_modifier import ConditionalModifier
    from app.services.state_encounter_integration import StateEncounterIntegration

    # Build SimulationState from the flattened pct input
    raw_state = data.get("state") or {}
    player_pct = float(raw_state.get("player_health_pct", 1.0))
    target_pct = float(raw_state.get("target_health_pct", 1.0))

    state = SimulationState(
        player_health=player_pct,
        player_max_health=1.0,
        target_health=target_pct,
        target_max_health=1.0,
        elapsed_time=float(raw_state.get("elapsed_time", 0.0)),
        active_buffs=set(raw_state.get("active_buffs") or []),
        active_status_effects=dict(raw_state.get("active_status_effects") or {}),
    )

    # Deserialise modifiers
    modifiers: list[ConditionalModifier] = []
    for m in data.get("modifiers") or []:
        try:
            modifiers.append(ConditionalModifier.from_dict(m))
        except (KeyError, ValueError) as exc:
            return validation_error({"modifiers": [str(exc)]})

    result = StateEncounterIntegration().evaluate_damage(
        base_damage=data["base_damage"],
        modifiers=modifiers,
        state=state,
    )

    return ok(data={
        "base_damage":         result.base_damage,
        "adjusted_damage":     result.adjusted_damage,
        "damage_multiplier":   result.damage_multiplier,
        "active_modifier_ids": result.active_modifier_ids,
        "stat_deltas":         result.stat_deltas,
    })
