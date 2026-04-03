"""
K8 — Piercing Logic

Determines whether a projectile can pass through a target and continue
traveling, decrementing its pierce counter on each pass-through.

A projectile with pierce_count == 0 is destroyed on its first hit.
Each pierce_count > 0 allows one additional hit before deactivation.
"""

from __future__ import annotations

from dataclasses import dataclass

from projectiles.models.projectile import Projectile


@dataclass(frozen=True)
class PierceResult:
    """Result of evaluating pierce logic for one projectile-target interaction."""

    pierced:      bool          # True if the projectile continues after this hit
    pierce_remaining: int       # pierce_count after this interaction
    target_id:    str           # target that was struck


class PierceLogic:
    """
    Evaluates and applies pierce for projectile hits.

    evaluate(projectile, target_id)
        → PierceResult

    apply(projectile, target_id)
        → PierceResult  (also mutates projectile state via record_hit)
    """

    def evaluate(self, projectile: Projectile, target_id: str) -> PierceResult:
        """
        Calculate pierce outcome without mutating the projectile.
        A pierce_count of 0 means the projectile stops; > 0 it continues.
        """
        pierced = projectile.pierce_count > 0
        remaining = max(-1, projectile.pierce_count - 1)
        return PierceResult(
            pierced=pierced,
            pierce_remaining=remaining,
            target_id=target_id,
        )

    def apply(self, projectile: Projectile, target_id: str) -> PierceResult:
        """
        Evaluate pierce AND record the hit on the projectile (mutating it).
        After this call, projectile.pierce_count is decremented and the
        projectile is deactivated if pierce_count would drop below 0.
        """
        result = self.evaluate(projectile, target_id)
        projectile.record_hit(target_id)
        return result

    @staticmethod
    def can_hit(projectile: Projectile, target_id: str) -> bool:
        """
        True if the projectile is able to hit *target_id* right now.
        A projectile cannot hit the same target twice and must be active.
        """
        return projectile.is_active and not projectile.has_hit(target_id)

    @staticmethod
    def remaining_pierce(projectile: Projectile) -> int:
        """How many more targets this projectile can hit (0 = only one remaining)."""
        return projectile.pierce_count
