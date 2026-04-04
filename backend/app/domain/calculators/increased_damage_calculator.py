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
from app.domain.calculators.damage_type_router import combined_increased_stats, tags_for_stats
from app.engines.stat_engine import BuildStats
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


def sum_increased_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """
    Sum all % increased damage bonuses for a skill into one additive pool.

    Uses the damage type router to determine which stat fields apply:
      - Each DamageType resolves to its own stat fields via _HIT_INCREASED_STATS.
        Elemental types (FIRE, COLD, LIGHTNING) automatically include
        elemental_damage_pct — no explicit check required.
      - SkillTags (SPELL, MINION) are resolved from scaling_stats via tags_for_stats.
      - Weapon-type bonuses (melee, throwing, bow) are added from SkillStatDef
        flags, since those don't appear in scaling_stats.
    """
    if not skill_def.damage_types:
        log.warning("sum_increased_damage.no_damage_types", scaling_stats=skill_def.scaling_stats)

    stat_fields = combined_increased_stats(
        skill_def.damage_types,
        tags_for_stats(skill_def.scaling_stats),
    )
    total = combine_additive_percents(*[getattr(stats, k, 0.0) for k in stat_fields])

    if skill_def.is_melee:
        total = combine_additive_percents(total, stats.melee_damage_pct)
    if skill_def.is_throwing:
        total = combine_additive_percents(total, stats.throwing_damage_pct)
    if skill_def.is_bow:
        total = combine_additive_percents(total, stats.bow_damage_pct)

    return total
