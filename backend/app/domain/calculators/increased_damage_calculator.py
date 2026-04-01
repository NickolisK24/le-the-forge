"""
Increased Damage Calculator — additive % increased damage pool.

Rules:
- Pure computation only
- No registry access
- No Flask dependencies
"""

from __future__ import annotations

from app.domain.skill import SkillStatDef
from app.domain.calculators.stat_calculator import combine_additive_percents
from app.domain.calculators.damage_type_router import ELEMENTAL_TYPES
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


def sum_increased_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """
    Sum all % increased damage bonuses for a skill into one additive pool.

    Combines scaling stats, weapon-type bonuses, and elemental bonuses —
    all of which stack additively before any multiplicative more% is applied.
    """
    if not skill_def.damage_types:
        log.warning("sum_increased_damage.no_damage_types", scaling_stats=skill_def.scaling_stats)

    total = combine_additive_percents(*[getattr(stats, k, 0.0) for k in skill_def.scaling_stats])

    if skill_def.is_melee:
        total = combine_additive_percents(total, stats.melee_damage_pct)
    if skill_def.is_throwing:
        total = combine_additive_percents(total, stats.throwing_damage_pct)
    if skill_def.is_bow:
        total = combine_additive_percents(total, stats.bow_damage_pct)
    if any(dt in ELEMENTAL_TYPES for dt in skill_def.damage_types):
        total = combine_additive_percents(total, stats.elemental_damage_pct)

    return total
