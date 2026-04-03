"""
I3 — Target Spawn Templates

Pre-built encounter configurations that produce a TargetManager
populated with a specific group of TargetEntity objects.

Available templates:
    single_boss(hp)      — one high-HP target
    elite_pack(count, hp) — a few tough targets
    mob_swarm(count, hp)  — many low-HP targets
    custom(specs)         — arbitrary list of (id, hp, position)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from targets.models.target_entity import TargetEntity
from targets.target_manager import TargetManager


@dataclass(frozen=True)
class TargetSpec:
    """Specification for a single target in a template."""
    target_id: str
    max_health: float
    position_index: int = 0

    def __post_init__(self) -> None:
        if self.max_health <= 0:
            raise ValueError("max_health must be > 0")


def _build_manager(specs: Sequence[TargetSpec]) -> TargetManager:
    mgr = TargetManager()
    for spec in specs:
        mgr.spawn(TargetEntity(
            target_id=spec.target_id,
            max_health=spec.max_health,
            position_index=spec.position_index,
        ))
    return mgr


def single_boss(max_health: float = 100_000.0) -> TargetManager:
    """One target representing a powerful boss."""
    return _build_manager([TargetSpec("boss", max_health, 0)])


def elite_pack(count: int = 3, max_health: float = 30_000.0) -> TargetManager:
    """A small group of tough elite enemies."""
    if count < 1:
        raise ValueError("count must be >= 1")
    specs = [TargetSpec(f"elite_{i}", max_health, i) for i in range(count)]
    return _build_manager(specs)


def mob_swarm(count: int = 10, max_health: float = 5_000.0) -> TargetManager:
    """Many low-HP targets representing a mob pack."""
    if count < 1:
        raise ValueError("count must be >= 1")
    specs = [TargetSpec(f"mob_{i}", max_health, i) for i in range(count)]
    return _build_manager(specs)


def custom(specs: Sequence[TargetSpec]) -> TargetManager:
    """Build a manager from an arbitrary list of TargetSpec objects."""
    if not specs:
        raise ValueError("specs must not be empty")
    return _build_manager(specs)


# Named template registry for use in API / schema
TEMPLATES: dict[str, callable] = {
    "single_boss": single_boss,
    "elite_pack":  elite_pack,
    "mob_swarm":   mob_swarm,
}
