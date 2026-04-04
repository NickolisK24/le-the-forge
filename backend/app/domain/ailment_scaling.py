"""
Stat-Driven Ailment Scaling (Step 51).

scale_ailment_damage() multiplies a base ailment damage_per_tick value
by the player's additive increased-damage stats, exactly mirroring the
additive stacking model used everywhere else in the engine.

Stat pools per ailment type (all additive):
  BLEED   physical_damage_pct + dot_damage_pct + ailment_damage_pct + bleed_damage_pct
  IGNITE  fire_damage_pct     + dot_damage_pct + ailment_damage_pct + ignite_damage_pct
  POISON  poison_damage_pct   + dot_damage_pct + ailment_damage_pct + poison_dot_damage_pct
  SHOCK / FROSTBITE  dot_damage_pct + ailment_damage_pct  (utility ailments, minimal scaling)

Formula:
    scaled = base_damage × (1 + Σ increased_pct / 100)

Public API:
  scale_ailment_damage(base_damage, ailment_type, stats) -> float
"""

from __future__ import annotations

from app.domain.ailments import AilmentType
from app.domain.calculators.damage_type_router import DamageType, ailment_increased_stats
from app.engines.stat_engine import BuildStats


# Mapping from simulation AilmentType → router DamageType for the three
# damage-dealing ailments. SHOCK and FROSTBITE are utility ailments with
# no specific damage-type routing; they fall back to the generic pool.
_AILMENT_TO_DAMAGE_TYPE: dict[AilmentType, DamageType | None] = {
    AilmentType.BLEED:     DamageType.BLEED,
    AilmentType.IGNITE:    DamageType.IGNITE,
    AilmentType.POISON:    DamageType.POISON,
    AilmentType.SHOCK:     None,   # utility — no specific damage routing
    AilmentType.FROSTBITE: None,   # utility — no specific damage routing
}

# Generic stat pool applied when there is no specific DamageType routing.
_GENERIC_AILMENT_STATS: frozenset[str] = frozenset({
    "dot_damage_pct",
    "ailment_damage_pct",
})


def _stat_fields_for(ailment_type: AilmentType) -> frozenset[str]:
    damage_type = _AILMENT_TO_DAMAGE_TYPE[ailment_type]
    if damage_type is not None:
        return ailment_increased_stats(damage_type)
    return _GENERIC_AILMENT_STATS


def scale_ailment_damage(
    base_damage: float,
    ailment_type: AilmentType,
    stats: BuildStats,
) -> float:
    """
    Scale ``base_damage`` by all additive increased-damage stats applicable
    to ``ailment_type``.

    All matched stats are summed into one additive pool before applying:
        scaled = base_damage × (1 + total_increased_pct / 100)

    Returns base_damage unchanged if total bonus is 0 (no relevant stats set).
    """
    fields = _stat_fields_for(ailment_type)
    total_increased = sum(getattr(stats, f, 0.0) for f in fields)
    return base_damage * (1.0 + total_increased / 100.0)
