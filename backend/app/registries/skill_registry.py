"""
Skill Registry — indexes all playable skills for O(1) validated lookup.

Replaces the hardcoded SKILL_STATS dict in combat_engine.py. Seeded from
backend/app/game_data/skills.json via the GameDataPipeline at app startup.

Usage:
    from flask import current_app
    registry = current_app.extensions["skill_registry"]
    stat_def = registry.get("Fireball")       # raises SkillNotFoundError if unknown
    names    = registry.names()               # list[str], for /api/ref/skills
"""

from __future__ import annotations
from app.engines.combat_engine import SkillStatDef
from app.utils.exceptions import ForgeError
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


class SkillNotFoundError(ForgeError):
    status_code = 404

    def __init__(self, skill_name: str) -> None:
        super().__init__(f"Unknown skill: {skill_name!r}")
        self.skill_name = skill_name


class SkillRegistry:
    """
    Indexed map of all skills loaded from skills.json.

    Constructed once in create_app() and stored on app.extensions.
    """

    def __init__(self, skills_data: dict) -> None:
        """
        Args:
            skills_data: dict mapping skill name → raw dict from skills.json.
                         Shape: {"base_damage": float, "level_scaling": float,
                                 "attack_speed": float, "scaling_stats": list,
                                 "is_spell": bool, ...}
        """
        self._skills: dict[str, SkillStatDef] = {}

        for name, raw in skills_data.items():
            self._skills[name] = SkillStatDef(
                base_damage=float(raw["base_damage"]),
                level_scaling=float(raw["level_scaling"]),
                attack_speed=float(raw["attack_speed"]),
                scaling_stats=list(raw.get("scaling_stats", [])),
                is_spell=bool(raw.get("is_spell", False)),
                is_melee=bool(raw.get("is_melee", False)),
                is_throwing=bool(raw.get("is_throwing", False)),
                is_bow=bool(raw.get("is_bow", False)),
            )

        log.info("skill_registry.initialized", count=len(self._skills))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, name: str) -> SkillStatDef:
        """Return the SkillStatDef for a skill name, or raise SkillNotFoundError."""
        stat_def = self._skills.get(name)
        if stat_def is None:
            raise SkillNotFoundError(name)
        return stat_def

    def names(self) -> list[str]:
        """Return all registered skill names, sorted."""
        return sorted(self._skills.keys())

    def all(self) -> dict[str, SkillStatDef]:
        """Return a copy of the full name → SkillStatDef mapping."""
        return dict(self._skills)

    def __contains__(self, name: str) -> bool:
        return name in self._skills

    def __len__(self) -> int:
        return len(self._skills)
