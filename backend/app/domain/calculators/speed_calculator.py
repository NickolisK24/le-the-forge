"""
Speed Calculator — effective attack/cast speed math.

All functions accept primitive values or typed domain objects and return
computed values. No registry access. No Flask context. No I/O.
"""

from __future__ import annotations

from app.domain.skill import SkillStatDef
from app.domain.skill_modifiers import SkillModifiers
from app.engines.stat_engine import BuildStats


def effective_attack_speed(
    skill_def: SkillStatDef,
    stats: BuildStats,
    sm: SkillModifiers,
) -> float:
    """
    Effective attacks (or casts) per second for a skill.

    Routing:
      Spells    → apply cast_speed bonus
      Throwing  → apply throwing_attack_speed bonus
      Otherwise → apply attack_speed_pct bonus

    Formula: base_attack_speed × (1 + sum_of_applicable_bonuses / 100)
    """
    cast_speed_bonus = (stats.cast_speed + sm.cast_speed_pct) / 100 if skill_def.is_spell else 0.0
    attack_speed_bonus = (stats.attack_speed_pct + sm.attack_speed_pct) / 100 if not skill_def.is_spell else 0.0
    throw_speed_bonus = stats.throwing_attack_speed / 100 if skill_def.is_throwing else 0.0
    return skill_def.attack_speed * (1 + cast_speed_bonus + attack_speed_bonus + throw_speed_bonus)
