"""
Spawn Controller (Step 103).

Handles timed spawning of additional enemies (adds/waves) during an encounter.

  SpawnWave         — a named wave: time to spawn + list of EncounterEnemy
  SpawnController   — scheduled waves; tick(time) fires due waves and returns
                      newly-spawned enemies for registration with TargetManager
"""

from __future__ import annotations

from dataclasses import dataclass, field

from encounter.enemy import EncounterEnemy


@dataclass
class SpawnWave:
    """A scheduled wave of enemies."""
    name:       str
    spawn_time: float
    enemies:    list[EncounterEnemy] = field(default_factory=list)
    spawned:    bool = False

    def __post_init__(self) -> None:
        if self.spawn_time < 0:
            raise ValueError(f"spawn_time must be >= 0, got {self.spawn_time}")


class SpawnController:
    """
    Manages scheduled spawn waves.

    tick(time) returns enemies from all waves due by *time*
    that have not yet been spawned. Spawned enemies are reset()
    to full health before being returned (fresh spawn).
    """

    def __init__(self, waves: list[SpawnWave] | None = None) -> None:
        self._waves: list[SpawnWave] = sorted(
            waves or [], key=lambda w: w.spawn_time
        )

    def add_wave(self, wave: SpawnWave) -> None:
        self._waves.append(wave)
        self._waves.sort(key=lambda w: w.spawn_time)

    def tick(self, time: float) -> list[EncounterEnemy]:
        """
        Fire all waves due at or before *time*.

        Each enemy in a newly-spawned wave is reset() before being returned.
        Returns the combined list of freshly-spawned enemies.
        """
        spawned: list[EncounterEnemy] = []
        for wave in self._waves:
            if not wave.spawned and wave.spawn_time <= time:
                wave.spawned = True
                for enemy in wave.enemies:
                    enemy.reset()
                spawned.extend(wave.enemies)
        return spawned

    def pending_waves(self) -> list[SpawnWave]:
        return [w for w in self._waves if not w.spawned]

    def spawned_waves(self) -> list[SpawnWave]:
        return [w for w in self._waves if w.spawned]

    def wave_count(self) -> int:
        return len(self._waves)

    def reset(self) -> None:
        """Mark all waves as un-spawned (for re-running the encounter)."""
        for wave in self._waves:
            wave.spawned = False
