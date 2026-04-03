"""
H1 — Condition Model

A Condition represents a boolean predicate that can be evaluated against
simulation state. Conditions drive conditional modifiers, event triggers,
and health-threshold effects.

Supported condition_type values:
    target_health_pct  — target's current HP / max HP
    player_health_pct  — player's current HP / max HP
    buff_active        — named buff is present in active_buffs
    status_present     — named status effect is in active_status_effects
    time_elapsed       — simulation clock has passed threshold_value seconds

Supported comparison_operator values (for numeric types):
    lt  <     le  <=     eq  ==     ge  >=     gt  >
"""

from __future__ import annotations

from dataclasses import dataclass

VALID_TYPES = frozenset(
    {"target_health_pct", "player_health_pct", "buff_active", "status_present", "time_elapsed"}
)
VALID_OPERATORS = frozenset({"lt", "le", "eq", "ge", "gt"})


@dataclass(frozen=True)
class Condition:
    """
    Immutable condition descriptor.

    condition_id        — unique identifier (e.g. "below_50pct_hp")
    condition_type      — one of VALID_TYPES
    threshold_value     — numeric threshold; required for numeric types,
                          ignored for buff_active / status_present
    comparison_operator — one of VALID_OPERATORS; required for numeric types
    duration            — optional; used by TimeWindow (H11) to define a
                          window in which this condition stays active
    """
    condition_id:        str
    condition_type:      str
    threshold_value:     float | None = None
    comparison_operator: str          = "lt"
    duration:            float | None = None

    def __post_init__(self) -> None:
        if self.condition_type not in VALID_TYPES:
            raise ValueError(
                f"Invalid condition_type {self.condition_type!r}. "
                f"Must be one of: {sorted(VALID_TYPES)}"
            )
        _numeric = {"target_health_pct", "player_health_pct", "time_elapsed"}
        if self.condition_type in _numeric:
            if self.threshold_value is None:
                raise ValueError(
                    f"condition_type {self.condition_type!r} requires threshold_value"
                )
            if self.comparison_operator not in VALID_OPERATORS:
                raise ValueError(
                    f"Invalid comparison_operator {self.comparison_operator!r}. "
                    f"Must be one of: {sorted(VALID_OPERATORS)}"
                )
        if self.duration is not None and self.duration <= 0:
            raise ValueError("duration must be > 0 when specified")

    # ------------------------------------------------------------------
    # Comparison helpers
    # ------------------------------------------------------------------

    def evaluate_numeric(self, actual: float) -> bool:
        """
        Compare *actual* against threshold_value using comparison_operator.
        Returns True when the condition is satisfied.
        """
        t = self.threshold_value
        op = self.comparison_operator
        if op == "lt":  return actual < t   # type: ignore[operator]
        if op == "le":  return actual <= t  # type: ignore[operator]
        if op == "eq":  return actual == t  # type: ignore[operator]
        if op == "ge":  return actual >= t  # type: ignore[operator]
        if op == "gt":  return actual > t   # type: ignore[operator]
        raise ValueError(f"Unknown operator: {op!r}")  # unreachable after __post_init__

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "condition_id":        self.condition_id,
            "condition_type":      self.condition_type,
            "threshold_value":     self.threshold_value,
            "comparison_operator": self.comparison_operator,
            "duration":            self.duration,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Condition":
        return cls(
            condition_id=d["condition_id"],
            condition_type=d["condition_type"],
            threshold_value=d.get("threshold_value"),
            comparison_operator=d.get("comparison_operator", "lt"),
            duration=d.get("duration"),
        )
