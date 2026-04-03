"""
J11 — Stat Data Integration

Bridges the Phase J data layer (SkillModel, EnemyModel) with the Phase H
SimulationState, injecting real stat values into state fields.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from data.models.skill_model import SkillModel
from data.models.enemy_model import EnemyModel

if TYPE_CHECKING:
    from state.state_engine import SimulationState

__all__ = ["StatDataIntegration", "StatInjectionResult"]


class StatInjectionResult:
    """Captures the outcome of a stat injection pass."""

    def __init__(
        self,
        skill_damage: float,
        enemy_armor: float,
        effective_damage: float,
        notes: list[str] | None = None,
    ) -> None:
        self.skill_damage = skill_damage
        self.enemy_armor = enemy_armor
        self.effective_damage = effective_damage
        self.notes: list[str] = notes or []

    def to_dict(self) -> dict:
        return {
            "skill_damage": self.skill_damage,
            "enemy_armor": self.enemy_armor,
            "effective_damage": self.effective_damage,
            "notes": self.notes,
        }


class StatDataIntegration:
    """
    Inject real stat values from game-data models into a SimulationState
    and compute effective damage.

    Parameters
    ----------
    skill:
        The attacking skill providing base damage.
    enemy:
        The defending enemy providing armor/resistances.
    """

    def __init__(self, skill: SkillModel, enemy: EnemyModel) -> None:
        self._skill = skill
        self._enemy = enemy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def inject(self, state: "SimulationState") -> StatInjectionResult:
        """
        Apply skill base_damage and enemy armor to *state*.

        Steps:
        1. Write ``skill.base_damage`` into ``state.stat_cache["base_damage"]``
        2. Write ``enemy.armor``       into ``state.stat_cache["enemy_armor"]``
        3. Compute effective damage after armor reduction
        4. Return a :class:`StatInjectionResult` with the results

        The simplified armor reduction formula is:
            effective_damage = base_damage × (1 − armor / (armor + 300))
        """
        notes: list[str] = []

        base = self._skill.base_damage
        armor = self._enemy.armor

        # Write into the state's stat_cache (a plain dict on SimulationState)
        if hasattr(state, "stat_cache"):
            state.stat_cache["base_damage"] = base
            state.stat_cache["enemy_armor"] = armor
        else:
            notes.append("state has no stat_cache attribute; values not written")

        # Armor reduction: reduction_pct = armor / (armor + 300)
        reduction_pct = armor / (armor + 300) if armor > 0 else 0.0
        effective = base * (1.0 - reduction_pct)

        # Apply resistances for a default damage type of "physical"
        phys_res = self._enemy.resistance("physical")
        if phys_res > 0:
            effective *= 1.0 - min(phys_res / 100.0, 1.0)
            notes.append(f"physical resistance {phys_res}% applied")

        return StatInjectionResult(
            skill_damage=base,
            enemy_armor=armor,
            effective_damage=round(effective, 4),
            notes=notes,
        )

    def scale_with_level(
        self, state: "SimulationState", level: int
    ) -> StatInjectionResult:
        """
        Scale base damage by player level (simple +1% per level above 1).
        """
        scale = 1.0 + max(0, level - 1) * 0.01
        original_base = self._skill.base_damage
        # Temporarily substitute a scaled version
        scaled_skill = SkillModel(
            skill_id=self._skill.skill_id,
            base_damage=original_base * scale,
            cooldown=self._skill.cooldown,
            mana_cost=self._skill.mana_cost,
            tags=self._skill.tags,
        )
        orig = self._skill
        object.__setattr__(self, "_skill", scaled_skill)
        result = self.inject(state)
        object.__setattr__(self, "_skill", orig)
        return result
