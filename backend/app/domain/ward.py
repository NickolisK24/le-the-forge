"""
Ward Decay Mechanics.

Ward is a secondary health pool that decays over time.

Formula:
    Ward_Lost/sec = 0.4 × (CurrentWard - Threshold) / (1 + 0.5 × WardRetention)

- Intelligence grants 4% Ward Retention per point (handled by stat engine)
- Ward Decay Threshold = floor below which ward does not decay
- Ward is NOT protected by Endurance
- Ward sits on top of health: damage hits ward first, overflow hits health

Public API:
    ward_decay_per_second(current_ward, threshold, ward_retention) -> float
    effective_ward_retention(base_retention, intelligence) -> float
"""

from __future__ import annotations

from app.constants.defense import (
    WARD_BASE_DECAY_RATE,
    INTELLIGENCE_WARD_RETENTION_PER_POINT,
)


def ward_decay_per_second(
    current_ward: float,
    threshold: float = 0.0,
    ward_retention: float = 0.0,
) -> float:
    """
    Calculate ward lost per second using the Last Epoch formula.

        Ward_Lost/sec = 0.4 × (CurrentWard - Threshold) / (1 + 0.5 × WardRetention)

    ward_retention is a percentage (e.g. 100 = 100% ward retention).
    Returns 0 if current_ward is at or below threshold.
    """
    effective_ward = current_ward - threshold
    if effective_ward <= 0:
        return 0.0
    retention_factor = 1.0 + 0.5 * (ward_retention / 100.0)
    return WARD_BASE_DECAY_RATE * effective_ward / retention_factor


def effective_ward_retention(
    base_retention: float,
    intelligence: float = 0.0,
) -> float:
    """
    Total ward retention including intelligence scaling.

    Intelligence grants 4% ward retention per point.
    """
    return base_retention + intelligence * INTELLIGENCE_WARD_RETENTION_PER_POINT
