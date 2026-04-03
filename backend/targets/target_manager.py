"""
I2 — Target Collection Manager

Maintains the set of active TargetEntities for an encounter.
Handles spawning, retrieval, death removal, and reset.
"""

from __future__ import annotations

from targets.models.target_entity import TargetEntity


class TargetManager:
    """
    Central registry of targets for one simulation run.

    spawn(target)          — register a new target
    get(target_id)         — look up by id (raises KeyError if not found)
    remove(target_id)      — explicitly remove a target
    remove_dead()          — purge all targets with current_health == 0
    alive_targets()        — list of living targets
    all_targets()          — list of all registered targets
    alive_count            — number of living targets
    reset()                — remove all targets
    """

    def __init__(self) -> None:
        self._targets: dict[str, TargetEntity] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def spawn(self, target: TargetEntity) -> None:
        """Register *target*. Raises ValueError if target_id already exists."""
        if target.target_id in self._targets:
            raise ValueError(f"Target '{target.target_id}' already registered")
        self._targets[target.target_id] = target

    def remove(self, target_id: str) -> None:
        """Remove target by id. No-op if not present."""
        self._targets.pop(target_id, None)

    def remove_dead(self) -> list[str]:
        """
        Remove all dead (current_health == 0) targets.
        Returns list of removed target_ids.
        """
        dead = [tid for tid, t in self._targets.items() if not t.is_alive]
        for tid in dead:
            del self._targets[tid]
        return dead

    def reset(self) -> None:
        self._targets.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, target_id: str) -> TargetEntity:
        try:
            return self._targets[target_id]
        except KeyError:
            raise KeyError(f"Target '{target_id}' not found")

    def alive_targets(self) -> list[TargetEntity]:
        return [t for t in self._targets.values() if t.is_alive]

    def all_targets(self) -> list[TargetEntity]:
        return list(self._targets.values())

    @property
    def alive_count(self) -> int:
        return sum(1 for t in self._targets.values() if t.is_alive)

    @property
    def total_count(self) -> int:
        return len(self._targets)

    def is_cleared(self) -> bool:
        """True when all registered targets are dead."""
        return self.alive_count == 0
