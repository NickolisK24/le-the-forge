"""
G11 — Rotation → Encounter Integration

Bridges the rotation engine to the Phase C encounter simulation:
  1. Execute the rotation to get a sequence of CastResult objects.
  2. For each cast, run a mini encounter simulation using the cast's damage
     as base_damage.
  3. Aggregate per-cast encounter outputs into a single RotationEncounterResult.

The caller only needs to supply a RotationDefinition, a SkillDefinition
registry, encounter kwargs, and a simulation duration.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from rotation.models.rotation_definition import RotationDefinition
from rotation.rotation_executor           import execute_rotation, CastResult
from rotation.metrics                     import compute_metrics, RotationMetrics
from skills.models.skill_definition       import SkillDefinition


@dataclass
class RotationEncounterResult:
    """Aggregated result from a rotation-driven encounter simulation."""
    total_damage:     float
    dps:              float
    total_casts:      int
    rotation_metrics: RotationMetrics
    cast_results:     list[dict]          = field(default_factory=list)
    encounter_kwargs: dict                = field(default_factory=dict)


def simulate_rotation_encounter(
    rotation:       RotationDefinition,
    skill_registry: dict[str, SkillDefinition],
    duration:       float,
    gcd:            float = 0.0,
    encounter_kwargs: dict | None = None,
) -> RotationEncounterResult:
    """
    Run a full rotation-driven encounter simulation.

    Parameters
    ----------
    rotation:
        Which rotation to execute.
    skill_registry:
        skill_id → SkillDefinition.
    duration:
        Total simulation window in seconds.
    gcd:
        Global cooldown (0 = none).
    encounter_kwargs:
        Encounter settings forwarded to run_encounter_simulation.
        Defaults: TRAINING_DUMMY, 60s, 0.1 tick, SINGLE distribution.

    Returns
    -------
    RotationEncounterResult with aggregated damage, DPS, and per-cast detail.
    """
    from app.services.simulation_service import run_encounter_simulation

    enc = encounter_kwargs or {
        "enemy_template": "TRAINING_DUMMY",
        "fight_duration": duration,
        "tick_size":      0.1,
        "distribution":   "SINGLE",
    }

    # 1. Execute rotation
    cast_results = execute_rotation(rotation, skill_registry, duration, gcd=gcd)
    metrics = compute_metrics(cast_results, duration)

    if not cast_results:
        return RotationEncounterResult(
            total_damage     = 0.0,
            dps              = 0.0,
            total_casts      = 0,
            rotation_metrics = metrics,
            cast_results     = [],
            encounter_kwargs = enc,
        )

    # 2. Run one encounter per cast using that cast's damage, then sum
    total_damage = 0.0
    cast_detail: list[dict] = []

    for cast in cast_results:
        # Each cast is simulated as a single-tick encounter (1 hit of base_damage)
        cast_enc = {**enc, "fight_duration": max(enc.get("fight_duration", duration),
                                                  cast.resolves_at + 0.1)}
        try:
            enc_result = run_encounter_simulation(
                base_damage     = cast.damage,
                enemy_template  = enc.get("enemy_template", "TRAINING_DUMMY"),
                fight_duration  = cast.resolves_at + max(enc.get("tick_size", 0.1), 0.1),
                tick_size       = enc.get("tick_size", 0.1),
                distribution    = enc.get("distribution", "SINGLE"),
                crit_chance     = enc.get("crit_chance", 0.0),
                crit_multiplier = enc.get("crit_multiplier", 2.0),
            )
            cast_damage = enc_result.get("total_damage", cast.damage)
        except Exception:
            cast_damage = cast.damage
            enc_result  = {}

        total_damage += cast_damage
        cast_detail.append({
            "skill_id":    cast.skill_id,
            "cast_at":     cast.cast_at,
            "resolves_at": cast.resolves_at,
            "damage":      cast_damage,
        })

    dps = total_damage / duration if duration > 0 else 0.0

    return RotationEncounterResult(
        total_damage     = total_damage,
        dps              = dps,
        total_casts      = len(cast_results),
        rotation_metrics = metrics,
        cast_results     = cast_detail,
        encounter_kwargs = enc,
    )
