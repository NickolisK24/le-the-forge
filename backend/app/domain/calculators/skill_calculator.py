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
from app.domain.calculators.damage_type_router import DamageType
from app.engines.stat_engine import BuildStats


def scale_skill_damage(
    base: float,
    scaling: float,
    level: int,
    damage_types: tuple[DamageType, ...] = (),
) -> dict[DamageType, float]:
    """
    Apply level scaling and distribute the total evenly across damage types.

    Returns a dict mapping each DamageType to its portion of the scaled total.
    For a single-type skill the dict has one entry equal to the full scaled value.
    For multi-type skills each entry is total / n, so the sum is always preserved.

    Returns an empty dict when damage_types is empty — callers must fall back
    to the untyped total (e.g. for spell-only skills pending data migration).
    """
    total = base * (1 + scaling * (level - 1))
    if not damage_types:
        return {}
    per_type = total / len(damage_types)
    return {dt: per_type for dt in damage_types}


def hits_per_cast(added: int) -> int:
    """Total hits per cast: base 1 plus any spec-tree additions."""
    return max(1, 1 + added)


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
