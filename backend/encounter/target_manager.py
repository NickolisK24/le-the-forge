"""
Encounter Target Manager (Step 98).

Tracks active targets in an encounter and handles target selection
and cleanup of defeated enemies.

  TargetManager
    - active_targets          — list of living EncounterEnemy
    - primary_target_index    — index into active_targets for the current target
    - select_primary()        — returns the current primary target (or None)
    - switch_target(index)    — change the primary target by index
    - remove_dead_targets()   — purge defeated enemies; adjust index
    - add_target(enemy)       — register a new enemy
    - all_dead                — True when no enemies remain alive

Primary target selection rules:
  - Primary target is the enemy at primary_target_index.
  - Index is clamped to valid range after removal.
  - If all enemies are dead, select_primary() returns None.
"""

from __future__ import annotations

from encounter.enemy import EncounterEnemy


class TargetManager:
    """
    Manages the list of active enemies and primary target selection.

    Usage:
        mgr = TargetManager(enemies)
        primary = mgr.select_primary()
        mgr.remove_dead_targets()
    """

    def __init__(self, enemies: list[EncounterEnemy] | None = None) -> None:
        self._targets: list[EncounterEnemy] = list(enemies or [])
        self._primary_index: int = 0

    # ------------------------------------------------------------------
    # Target list management
    # ------------------------------------------------------------------

    def add_target(self, enemy: EncounterEnemy) -> None:
        """Register a new enemy into the active target list."""
        self._targets.append(enemy)

    def remove_dead_targets(self) -> list[EncounterEnemy]:
        """
        Remove all dead enemies from the active list.

        Adjusts primary_target_index to remain valid.
        Returns the list of removed (dead) enemies.
        """
        alive   = [e for e in self._targets if e.is_alive]
        removed = [e for e in self._targets if not e.is_alive]
        self._targets = alive
        # Clamp index to valid range
        if self._targets:
            self._primary_index = min(self._primary_index, len(self._targets) - 1)
        else:
            self._primary_index = 0
        return removed

    # ------------------------------------------------------------------
    # Target selection
    # ------------------------------------------------------------------

    def select_primary(self) -> EncounterEnemy | None:
        """Return the current primary target, or None if no targets remain."""
        if not self._targets:
            return None
        return self._targets[self._primary_index]

    def switch_target(self, index: int) -> None:
        """
        Set the primary target to *index*.

        Raises IndexError if index is out of range.
        """
        if not self._targets:
            raise IndexError("No active targets to switch to")
        if index < 0 or index >= len(self._targets):
            raise IndexError(
                f"Target index {index} out of range (0–{len(self._targets)-1})"
            )
        self._primary_index = index

    def switch_to_lowest_health(self) -> None:
        """Switch primary target to the enemy with the lowest current_health."""
        if not self._targets:
            return
        self._primary_index = min(
            range(len(self._targets)),
            key=lambda i: self._targets[i].current_health,
        )

    def switch_to_highest_health(self) -> None:
        """Switch primary target to the enemy with the highest current_health."""
        if not self._targets:
            return
        self._primary_index = max(
            range(len(self._targets)),
            key=lambda i: self._targets[i].current_health,
        )

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    @property
    def primary_target_index(self) -> int:
        return self._primary_index

    @property
    def active_targets(self) -> list[EncounterEnemy]:
        """Read-only view of the current target list."""
        return list(self._targets)

    @property
    def target_count(self) -> int:
        return len(self._targets)

    @property
    def alive_count(self) -> int:
        return sum(1 for e in self._targets if e.is_alive)

    @property
    def all_dead(self) -> bool:
        return all(not e.is_alive for e in self._targets) if self._targets else True
