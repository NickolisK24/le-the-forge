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
from app.engines.stat_engine import BuildStats


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
