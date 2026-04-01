"""
Skill Registry — O(1) validated lookup over SkillStatDef domain objects.

Seeded from data/classes/skills.json via the GameDataPipeline (which
normalizes raw JSON → SkillStatDef) at app startup. The registry receives
pre-normalized domain objects; it does not do normalization itself.

Usage:
    from flask import current_app
    registry = current_app.extensions["skill_registry"]
    stat_def = registry.get("Fireball")       # raises SkillNotFoundError if unknown
    names    = registry.names()               # list[str], for /api/ref/skills
"""

from __future__ import annotations
from app.domain.skill import SkillStatDef
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

    Receives a pre-normalized dict[str, SkillStatDef] from the pipeline.
    Constructed once in create_app() and stored on app.extensions.
    """

    def __init__(self, skills: dict[str, SkillStatDef]) -> None:
        """
        Args:
            skills: mapping of skill name → SkillStatDef, already normalized
                    by the pipeline. No further normalization is done here.
        """
        self._skills: dict[str, SkillStatDef] = dict(skills)
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
