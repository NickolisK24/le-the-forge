"""
J13 — Enemy Data Integration

Applies Phase J EnemyModel templates to multi-target encounters,
producing validated encounter configurations.
"""

from __future__ import annotations

from dataclasses import dataclass

from data.models.enemy_model import EnemyModel

__all__ = ["EnemyDataIntegration", "EncounterConfig", "EnemyValidationError"]


class EnemyValidationError(Exception):
    """Raised when an enemy template fails encounter validation."""


@dataclass
class EncounterConfig:
    """Validated encounter configuration derived from enemy templates."""

    enemies: list[EnemyModel]
    total_health: float
    max_armor: float
    avg_resistance: float  # averaged across all types and enemies
    notes: list[str]

    def to_dict(self) -> dict:
        return {
            "enemy_count": len(self.enemies),
            "total_health": self.total_health,
            "max_armor": self.max_armor,
            "avg_resistance": self.avg_resistance,
            "notes": self.notes,
            "enemies": [e.to_dict() for e in self.enemies],
        }


class EnemyDataIntegration:
    """
    Build and validate encounter configurations from :class:`EnemyModel` templates.
    """

    # Maximum number of enemies allowed in a single encounter
    MAX_ENEMIES = 50

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_encounter(self, templates: list[EnemyModel]) -> EncounterConfig:
        """
        Validate *templates* and produce an :class:`EncounterConfig`.

        Raises
        ------
        EnemyValidationError
            If any validation rule is violated.
        """
        if not templates:
            raise EnemyValidationError("Encounter must have at least one enemy.")
        if len(templates) > self.MAX_ENEMIES:
            raise EnemyValidationError(
                f"Encounter has {len(templates)} enemies; maximum is {self.MAX_ENEMIES}."
            )

        notes: list[str] = []
        total_health = sum(e.max_health for e in templates)
        max_armor = max(e.armor for e in templates)

        # Compute average resistance across all types + enemies
        all_res_values: list[float] = []
        for e in templates:
            all_res_values.extend(e.resistances.values())
        avg_res = sum(all_res_values) / len(all_res_values) if all_res_values else 0.0

        if max_armor > 5000:
            notes.append(f"Warning: max_armor={max_armor} is very high.")
        if avg_res > 75:
            notes.append(f"Warning: avg_resistance={avg_res:.1f}% is very high.")

        return EncounterConfig(
            enemies=list(templates),
            total_health=total_health,
            max_armor=max_armor,
            avg_resistance=round(avg_res, 2),
            notes=notes,
        )

    def scale_encounter(
        self, config: EncounterConfig, multiplier: float
    ) -> EncounterConfig:
        """
        Return a new :class:`EncounterConfig` with all enemy HP scaled by *multiplier*.
        """
        if multiplier <= 0:
            raise ValueError("multiplier must be > 0")
        scaled = [
            EnemyModel(
                enemy_id=e.enemy_id,
                max_health=e.max_health * multiplier,
                resistances=dict(e.resistances),
                armor=e.armor,
            )
            for e in config.enemies
        ]
        return self.build_encounter(scaled)
