"""
K4 — Projectile Manager

Maintains all active Projectile instances for one simulation tick cycle.
Handles spawning, bulk advancement, and cleanup of expired projectiles.
"""

from __future__ import annotations

from projectiles.models.projectile import Projectile


class ProjectileManager:
    """
    Central registry for in-flight projectiles.

    spawn(projectile)       — register a new projectile
    get(projectile_id)      — retrieve by id (KeyError if missing)
    advance_all(delta)      — advance every active projectile by delta seconds
    active_projectiles()    — list of all currently active projectiles
    all_projectiles()       — list of all projectiles (including inactive)
    deactivate(id)          — force-deactivate a projectile
    clear_inactive()        — remove all inactive projectiles; returns count removed
    reset()                 — remove all projectiles
    active_count            — number of active projectiles
    total_count             — number of registered projectiles (active + inactive)
    """

    def __init__(self) -> None:
        self._projectiles: dict[str, Projectile] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def spawn(self, projectile: Projectile) -> None:
        """Register *projectile*. Raises ValueError if id already exists."""
        if projectile.projectile_id in self._projectiles:
            raise ValueError(
                f"Projectile '{projectile.projectile_id}' already registered"
            )
        self._projectiles[projectile.projectile_id] = projectile

    def deactivate(self, projectile_id: str) -> None:
        """Force-deactivate a projectile (no-op if not found)."""
        p = self._projectiles.get(projectile_id)
        if p is not None:
            p.deactivate()

    def advance_all(self, delta: float) -> None:
        """Advance all active projectiles by *delta* seconds."""
        for p in self._projectiles.values():
            if p.is_active:
                p.advance(delta)

    def clear_inactive(self) -> int:
        """
        Remove all inactive projectiles from the registry.
        Returns the number of projectiles removed.
        """
        inactive = [pid for pid, p in self._projectiles.items() if not p.is_active]
        for pid in inactive:
            del self._projectiles[pid]
        return len(inactive)

    def reset(self) -> None:
        self._projectiles.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, projectile_id: str) -> Projectile:
        try:
            return self._projectiles[projectile_id]
        except KeyError:
            raise KeyError(f"Projectile '{projectile_id}' not found")

    def active_projectiles(self) -> list[Projectile]:
        return [p for p in self._projectiles.values() if p.is_active]

    def all_projectiles(self) -> list[Projectile]:
        return list(self._projectiles.values())

    @property
    def active_count(self) -> int:
        return sum(1 for p in self._projectiles.values() if p.is_active)

    @property
    def total_count(self) -> int:
        return len(self._projectiles)

    def snapshot(self) -> list[dict]:
        """Return serialised snapshots of all active projectiles."""
        return [p.to_dict() for p in self.active_projectiles()]
