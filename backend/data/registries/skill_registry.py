"""J4 — Skill Registry"""

from data.models.skill_model import SkillModel

__all__ = ["SkillRegistry"]


class SkillRegistry:
    """
    Indexed lookup table for :class:`SkillModel` objects.

    Parameters
    ----------
    skills:
        Iterable of :class:`SkillModel` instances to index.
    """

    def __init__(self, skills) -> None:
        self._by_id: dict[str, SkillModel] = {s.skill_id: s for s in skills}

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, skill_id: str) -> SkillModel | None:
        """Return the skill or ``None`` if not found."""
        return self._by_id.get(skill_id)

    def get_or_raise(self, skill_id: str) -> SkillModel:
        """Return the skill or raise :exc:`KeyError`."""
        skill = self.get(skill_id)
        if skill is None:
            raise KeyError(f"Unknown skill: {skill_id!r}")
        return skill

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def all(self) -> list[SkillModel]:
        return list(self._by_id.values())

    def ids(self) -> list[str]:
        return list(self._by_id.keys())

    def count(self) -> int:
        return len(self._by_id)

    def __len__(self) -> int:
        return self.count()
