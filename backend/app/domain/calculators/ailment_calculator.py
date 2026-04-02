"""
Ailment Calculator — bleed, ignite, and poison DPS math.

All functions accept primitive values or typed domain objects and return
computed values. No registry access. No Flask context. No I/O.
"""

from __future__ import annotations

from app.constants.combat import (
    BLEED_BASE_RATIO,
    BLEED_DURATION,
    IGNITE_DPS_RATIO,
    IGNITE_DURATION,
    POISON_DPS_RATIO,
    POISON_DURATION,
)
from app.domain.calculators.stat_calculator import apply_percent_bonus, combine_additive_percents
from app.domain.calculators.damage_type_router import DamageType, ailment_increased_stats
from app.engines.stat_engine import BuildStats


def ailment_stack_count(effective_as: float, chance: float, duration: float) -> float:
    """
    Average number of active ailment stacks at steady state.

    At steady state, new stacks arrive at proc_rate = effective_as × chance
    and each lives for duration seconds, so:
        stacks = proc_rate × duration = effective_as × chance × duration
    """
    return effective_as * chance * duration


def calc_ailment_dps(
    hit_damage: float,
    effective_as: float,
    stats: BuildStats,
) -> tuple[int, int, int]:
    """
    Calculate per-ailment DPS from proc chance, base hit, and DoT scaling.

    Returns (bleed_dps, ignite_dps, poison_dps).

    Each ailment uses the stack model:
        stacks       = ailment_stack_count(effective_as, chance, duration)
        per_stack_dps = hit_damage × per_stack_ratio
        base_dps     = per_stack_dps × stacks

    Base is then scaled by the ailment's additive increased pool.
    """
    bleed_dps = ignite_dps = poison_dps = 0

    if stats.bleed_chance_pct > 0:
        chance = min(1.0, stats.bleed_chance_pct / 100)
        stacks = ailment_stack_count(effective_as, chance, BLEED_DURATION)
        per_stack_dps = hit_damage * BLEED_BASE_RATIO / BLEED_DURATION
        bleed_base = per_stack_dps * stacks
        bleed_dps = round(apply_percent_bonus(bleed_base, combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.BLEED)])))

    if stats.ignite_chance_pct > 0:
        chance = min(1.0, stats.ignite_chance_pct / 100)
        stacks = ailment_stack_count(effective_as, chance, IGNITE_DURATION)
        per_stack_dps = hit_damage * IGNITE_DPS_RATIO
        ignite_base = per_stack_dps * stacks
        ignite_dps = round(apply_percent_bonus(ignite_base, combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.IGNITE)])))

    if stats.poison_chance_pct > 0:
        chance = min(1.0, stats.poison_chance_pct / 100)
        stacks = ailment_stack_count(effective_as, chance, POISON_DURATION)
        per_stack_dps = hit_damage * POISON_DPS_RATIO
        poison_base = per_stack_dps * stacks
        poison_dps = round(apply_percent_bonus(poison_base, combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.POISON)])))

    return bleed_dps, ignite_dps, poison_dps
