"""
Skill Calculator — pure skill computation functions.

Rules:
- Pure computation only
- No registry access
- No Flask dependencies
- Accept typed domain objects when possible
"""

from __future__ import annotations

from app.domain.skill import SkillStatDef
from app.domain.calculators.stat_calculator import combine_additive_percents
from app.engines.stat_engine import BuildStats

_ELEMENTAL_STATS = frozenset({"fire_damage_pct", "cold_damage_pct", "lightning_damage_pct"})


def sum_flat_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """Sum all flat added damage relevant to a skill's attack type."""
    total = 0.0
    if skill_def.is_spell:
        total += (stats.added_spell_damage + stats.added_spell_fire +
                  stats.added_spell_cold + stats.added_spell_lightning +
                  stats.added_spell_necrotic + stats.added_spell_void)
    if skill_def.is_melee:
        total += (stats.added_melee_physical + stats.added_melee_fire +
                  stats.added_melee_cold + stats.added_melee_lightning +
                  stats.added_melee_void + stats.added_melee_necrotic)
    if skill_def.is_throwing:
        total += (stats.added_throw_physical + stats.added_throw_fire +
                  stats.added_throw_cold)
    if skill_def.is_bow:
        total += stats.added_bow_physical + stats.added_bow_fire
    return total


def sum_increased_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """
    Sum all % increased damage bonuses for a skill into one additive pool.

    Combines scaling stats, weapon-type bonuses, and elemental bonuses —
    all of which stack additively before any multiplicative more% is applied.
    """
    total = combine_additive_percents(*[getattr(stats, k, 0.0) for k in skill_def.scaling_stats])

    if skill_def.is_melee:
        total = combine_additive_percents(total, stats.melee_damage_pct)
    if skill_def.is_throwing:
        total = combine_additive_percents(total, stats.throwing_damage_pct)
    if skill_def.is_bow:
        total = combine_additive_percents(total, stats.bow_damage_pct)
    if _ELEMENTAL_STATS.intersection(skill_def.scaling_stats):
        total = combine_additive_percents(total, stats.elemental_damage_pct)

    return total
