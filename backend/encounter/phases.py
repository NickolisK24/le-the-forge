"""
Phase System Framework (Step 100).

Introduces boss phase transitions triggered by health thresholds or time.

  PhaseTransitionType — trigger type (health pct or elapsed time)
  PhaseModifiers      — stat adjustments active during a phase
  EncounterPhase      — one phase: id, trigger, duration cap, modifiers
  PhaseController     — evaluates phase transitions; applies modifiers
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class PhaseTransitionType(enum.Enum):
    HEALTH_BELOW  = "health_below"   # trigger when health_pct <= threshold
    TIME_ELAPSED  = "time_elapsed"   # trigger when elapsed_time >= threshold


@dataclass(frozen=True)
class PhaseModifiers:
    """Stat deltas active while an EncounterPhase is running."""
    damage_bonus_pct:    float = 0.0   # additive % damage increase
    speed_bonus_pct:     float = 0.0   # additive % speed increase
    defense_bonus_pct:   float = 0.0   # additive % incoming-damage reduction
    extra_tag:           str   = ""    # arbitrary label for state checks


@dataclass(frozen=True)
class EncounterPhase:
    """A single named phase in an encounter."""
    phase_id:          str
    transition_type:   PhaseTransitionType
    threshold:         float              # hp_pct (0–100) or elapsed seconds
    modifiers:         PhaseModifiers     = field(default_factory=PhaseModifiers)
    max_duration:      float              = -1.0  # -1 = unlimited

    def __post_init__(self) -> None:
        if self.threshold < 0:
            raise ValueError(f"threshold must be >= 0, got {self.threshold}")


class PhaseController:
    """
    Manages phase transitions for an encounter.

    Phases are tested in order; the first matching phase that has not
    yet been entered becomes the active phase.
    """

    def __init__(self, phases: list[EncounterPhase]) -> None:
        self._phases:       list[EncounterPhase] = list(phases)
        self._active_phase: EncounterPhase | None = None
        self._phase_start:  float = 0.0
        self._entered:      set[str] = set()

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, health_pct: float, elapsed_time: float) -> bool:
        """
        Check whether a new phase should activate.

        Returns True if a phase transition occurred.
        """
        for phase in self._phases:
            if phase.phase_id in self._entered:
                continue
            triggered = (
                (phase.transition_type is PhaseTransitionType.HEALTH_BELOW
                 and health_pct <= phase.threshold)
                or
                (phase.transition_type is PhaseTransitionType.TIME_ELAPSED
                 and elapsed_time >= phase.threshold)
            )
            if triggered:
                self._active_phase = phase
                self._phase_start  = elapsed_time
                self._entered.add(phase.phase_id)
                return True
        return False

    # ------------------------------------------------------------------
    # Active phase queries
    # ------------------------------------------------------------------

    @property
    def active_phase(self) -> EncounterPhase | None:
        return self._active_phase

    @property
    def active_modifiers(self) -> PhaseModifiers:
        if self._active_phase is None:
            return PhaseModifiers()
        return self._active_phase.modifiers

    def phase_elapsed(self, current_time: float) -> float:
        """Seconds since the active phase started."""
        if self._active_phase is None:
            return 0.0
        return max(0.0, current_time - self._phase_start)

    def is_phase_expired(self, current_time: float) -> bool:
        """True if active phase has exceeded its max_duration."""
        if self._active_phase is None:
            return False
        if self._active_phase.max_duration < 0:
            return False
        return self.phase_elapsed(current_time) >= self._active_phase.max_duration

    def reset(self) -> None:
        """Clear all phase state."""
        self._active_phase = None
        self._phase_start  = 0.0
        self._entered.clear()
