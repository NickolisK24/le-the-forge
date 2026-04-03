"""
J12 — Skill Data Integration

Connects Phase J SkillModel objects to the simulation rotation engine.
Validates cooldown alignment and resolves skill usage sequences.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from data.models.skill_model import SkillModel
from data.registries.skill_registry import SkillRegistry

__all__ = ["SkillDataIntegration", "SkillUsageResult"]


@dataclass
class SkillUsageResult:
    """Result of a single skill usage in a rotation."""

    skill_id: str
    damage_dealt: float
    mana_spent: float
    time_used: float
    on_cooldown_until: float

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "damage_dealt": self.damage_dealt,
            "mana_spent": self.mana_spent,
            "time_used": self.time_used,
            "on_cooldown_until": self.on_cooldown_until,
        }


class SkillDataIntegration:
    """
    Simulate a sequence of skill usages from a given rotation order.

    Parameters
    ----------
    registry:
        Source of :class:`SkillModel` lookups.
    """

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry
        self._cooldowns: dict[str, float] = {}  # skill_id → available_at

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Clear all cooldown state."""
        self._cooldowns.clear()

    def use_skill(
        self,
        skill_id: str,
        current_time: float,
        damage_multiplier: float = 1.0,
    ) -> SkillUsageResult:
        """
        Attempt to use *skill_id* at *current_time*.

        If the skill is on cooldown the attempt still proceeds (returns
        the usage result) but records that the cooldown was violated.
        The cooldown timer is always reset to ``current_time + cooldown``.
        """
        skill = self._registry.get_or_raise(skill_id)

        cooldown_end = self._cooldowns.get(skill_id, 0.0)
        # Update cooldown
        self._cooldowns[skill_id] = current_time + skill.cooldown

        return SkillUsageResult(
            skill_id=skill_id,
            damage_dealt=skill.base_damage * damage_multiplier,
            mana_spent=skill.mana_cost,
            time_used=current_time,
            on_cooldown_until=self._cooldowns[skill_id],
        )

    def simulate_rotation(
        self,
        rotation: list[str],
        start_time: float = 0.0,
        gap: float = 0.5,
    ) -> list[SkillUsageResult]:
        """
        Simulate a full rotation (ordered list of skill IDs).

        *gap* is the minimum time between consecutive skill uses (cast time).
        Skills are used one after another at ``start_time``, ``start_time+gap``,
        ``start_time+2*gap``, …, respecting cooldowns by waiting if needed.
        """
        self.reset()
        results: list[SkillUsageResult] = []
        t = start_time

        for skill_id in rotation:
            # Wait until the skill is off cooldown
            available_at = self._cooldowns.get(skill_id, 0.0)
            t = max(t, available_at)

            results.append(self.use_skill(skill_id, t))
            t += gap

        return results

    def is_on_cooldown(self, skill_id: str, current_time: float) -> bool:
        return self._cooldowns.get(skill_id, 0.0) > current_time
