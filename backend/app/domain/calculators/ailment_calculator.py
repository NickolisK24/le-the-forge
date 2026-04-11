"""
Ailment Calculator — bleed, ignite, and poison DPS math.

Last Epoch ailment mechanics:
  - Each ailment has a flat base DPS per stack (not a % of hit damage)
  - Ignite: 40 fire DoT/s per stack, 3s duration
  - Bleed: 43 physical DoT/s per stack, 4s duration
  - Poison: 28 poison DoT/s per stack, 3s duration
  - Ailment chance >100% guarantees multiple stacks per hit:
    e.g. 235% = 2 guaranteed + 35% chance for 3rd
  - 60% reduced ailment effectiveness vs bosses
  - DoTs CANNOT critically strike

All functions accept primitive values or typed domain objects and return
computed values. No registry access. No Flask context. No I/O.
"""

from __future__ import annotations

import math

from app.constants.combat import (
    BLEED_BASE_DPS,
    BLEED_DURATION,
    IGNITE_BASE_DPS,
    IGNITE_DURATION,
    POISON_BASE_DPS,
    POISON_DURATION,
    BOSS_AILMENT_REDUCTION,
)
from app.domain.calculators.stat_calculator import apply_percent_bonus, combine_additive_percents
from app.domain.calculators.damage_type_router import DamageType, ailment_increased_stats
from app.engines.stat_engine import BuildStats


def ailment_stacks_per_hit(chance_pct: float) -> float:
    """
    Average stacks applied per hit given ailment chance percentage.

    Chance >100% guarantees multiple stacks:
      235% = 2 guaranteed + 35% chance for 3rd = 2.35 average stacks per hit
    """
    if chance_pct <= 0:
        return 0.0
    return chance_pct / 100.0


def ailment_stack_count(
    effective_as: float,
    chance_pct: float,
    duration: float,
) -> float:
    """
    Average number of active ailment stacks at steady state.

    stacks = hits_per_second × stacks_per_hit × duration
    """
    stacks_per_hit = ailment_stacks_per_hit(chance_pct)
    return effective_as * stacks_per_hit * duration


def calc_ailment_dps(
    hit_damage: float,
    effective_as: float,
    stats: BuildStats,
    *,
    is_boss: bool = False,
) -> tuple[int, int, int]:
    """
    Calculate per-ailment DPS using flat base damage per stack.

    Returns (bleed_dps, ignite_dps, poison_dps).

    Each ailment uses:
        stacks    = ailment_stack_count(effective_as, chance_pct, duration)
        base_dps  = AILMENT_BASE_DPS × stacks
        final_dps = base_dps × (1 + increased_ailment%)

    Boss reduction (60%) is applied as a final multiplier when is_boss=True.
    """
    boss_mult = 1.0 - BOSS_AILMENT_REDUCTION if is_boss else 1.0
    bleed_dps = ignite_dps = poison_dps = 0

    if stats.bleed_chance_pct > 0:
        stacks = ailment_stack_count(effective_as, stats.bleed_chance_pct, BLEED_DURATION)
        bleed_base = BLEED_BASE_DPS * stacks
        increased = combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.BLEED)])
        bleed_dps = round(apply_percent_bonus(bleed_base, increased) * boss_mult)

    if stats.ignite_chance_pct > 0:
        stacks = ailment_stack_count(effective_as, stats.ignite_chance_pct, IGNITE_DURATION)
        ignite_base = IGNITE_BASE_DPS * stacks
        increased = combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.IGNITE)])
        ignite_dps = round(apply_percent_bonus(ignite_base, increased) * boss_mult)

    if stats.poison_chance_pct > 0:
        stacks = ailment_stack_count(effective_as, stats.poison_chance_pct, POISON_DURATION)
        poison_base = POISON_BASE_DPS * stacks
        increased = combine_additive_percents(
            *[getattr(stats, k) for k in ailment_increased_stats(DamageType.POISON)])
        poison_dps = round(apply_percent_bonus(poison_base, increased) * boss_mult)

    return bleed_dps, ignite_dps, poison_dps
