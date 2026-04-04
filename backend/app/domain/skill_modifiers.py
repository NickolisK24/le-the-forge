"""
SkillModifiers — typed container for per-skill spec-tree modifiers.

These are modifiers that apply only to a specific skill's damage calculation,
distinct from build-wide stats in BuildStats. Produced by skill_tree_resolver
and consumed by combat_engine.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SkillModifiers:
    """
    Per-skill modifiers from the spec tree.

    All values are percent-point unless noted (e.g. 50.0 = 50%).
    """
    more_damage_pct: float = 0.0        # multiplicative 'more' damage
    added_hits_per_cast: int = 0        # extra projectiles / chains
    attack_speed_pct: float = 0.0       # skill-specific attack speed
    cast_speed_pct: float = 0.0         # skill-specific cast speed
    crit_chance_pct: float = 0.0        # skill-specific crit chance
    crit_multiplier_pct: float = 0.0    # skill-specific crit multiplier
