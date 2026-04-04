"""
I5 — Target Selection Engine

Selects one or more targets from the alive pool based on a named strategy.

Modes:
    nearest        — lowest position_index
    random         — uniform random choice
    lowest_health  — target with least current_health
    highest_health — target with most current_health
    all_targets    — every alive target
"""

from __future__ import annotations

import random as _random
from typing import Sequence

from targets.models.target_entity import TargetEntity

VALID_MODES = frozenset(
    {"nearest", "random", "lowest_health", "highest_health", "all_targets"}
)


class TargetSelector:
    """
    select(mode, targets, rng) → list[TargetEntity]

    Returns a non-empty list of selected targets (single-item for all
    single-target modes; full list for all_targets).
    Raises ValueError for an empty pool or unknown mode.
    """

    def select(
        self,
        mode: str,
        targets: Sequence[TargetEntity],
        rng: _random.Random | None = None,
    ) -> list[TargetEntity]:
        alive = [t for t in targets if t.is_alive]
        if not alive:
            raise ValueError("No alive targets available for selection")
        if mode not in VALID_MODES:
            raise ValueError(f"Unknown selection mode {mode!r}. "
                             f"Must be one of: {sorted(VALID_MODES)}")

        if mode == "all_targets":
            return list(alive)

        if mode == "nearest":
            return [min(alive, key=lambda t: t.position_index)]

        if mode == "lowest_health":
            return [min(alive, key=lambda t: t.current_health)]

        if mode == "highest_health":
            return [max(alive, key=lambda t: t.current_health)]

        if mode == "random":
            _rng = rng or _random.Random()
            return [_rng.choice(alive)]

        raise ValueError(f"Unhandled mode: {mode!r}")  # unreachable
