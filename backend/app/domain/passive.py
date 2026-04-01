"""
Typed return shapes for passive and skill-tree resolvers.

Using TypedDict here (not dataclasses) because these are structured return
values from resolver functions — they don't need equality, copying, or
any object behaviour. TypedDict gives type safety without overhead.
"""

from __future__ import annotations
from typing import TypedDict


class SpecialEffect(TypedDict):
    node_id: str
    node_name: str
    key: str
    value: str


class PassiveStats(TypedDict):
    """Return type of passive_stat_resolver.resolve_passive_stats()."""

    additive: dict[str, float]         # field_name → accumulated flat value
    special_effects: list[SpecialEffect]


class SkillTreeStats(TypedDict):
    """Return type of skill_tree_resolver.resolve_skill_tree_stats()."""

    skill_name: str
    build_stat_bonuses: dict[str, float]   # BuildStats field_name → bonus
    skill_modifiers: dict[str, float]      # per-skill multipliers (more_damage_pct, etc.)
    special_effects: list[SpecialEffect]
