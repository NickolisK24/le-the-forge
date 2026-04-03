"""
H15 — Conditional Debug Logger

Provides structured debug logging for the conditional mechanics engine.
Captures which conditions were evaluated, which modifiers fired, what
stat deltas were computed, and what damage adjustment resulted.

Logging is zero-cost when disabled (guard flag).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from state.state_engine import SimulationState
from modifiers.models.conditional_modifier import ConditionalModifier

logger = logging.getLogger(__name__)


@dataclass
class ConditionalLogEntry:
    """One evaluation record from the conditional engine."""
    tick_time:            float
    state_snapshot:       dict
    evaluated_modifiers:  list[dict] = field(default_factory=list)   # {modifier_id, active, reason}
    stat_deltas:          dict[str, float] = field(default_factory=dict)
    base_damage:          float = 0.0
    adjusted_damage:      float = 0.0

    def summary(self) -> str:
        active = [e["modifier_id"] for e in self.evaluated_modifiers if e["active"]]
        return (
            f"t={self.tick_time:.3f}s  "
            f"damage {self.base_damage:.1f}→{self.adjusted_damage:.1f}  "
            f"active=[{', '.join(active)}]  "
            f"deltas={self.stat_deltas}"
        )


class ConditionalLogger:
    """
    Attach to the conditional engine to record evaluation details.

    Usage::
        clog = ConditionalLogger(enabled=True, max_entries=500)
        # ... after each engine.evaluate() call:
        clog.record(tick_time, state, modifiers, stat_deltas, base, adjusted)
        clog.dump_to_logger()
    """

    def __init__(self, enabled: bool = True, max_entries: int = 1000) -> None:
        self.enabled = enabled
        self.max_entries = max_entries
        self._entries: list[ConditionalLogEntry] = []

    def record(
        self,
        tick_time: float,
        state: SimulationState,
        modifiers: list[ConditionalModifier],
        stat_deltas: dict[str, float],
        base_damage: float,
        adjusted_damage: float,
        active_ids: list[str] | None = None,
    ) -> None:
        """Capture one evaluation frame. No-op when disabled."""
        if not self.enabled:
            return
        if len(self._entries) >= self.max_entries:
            self._entries.pop(0)

        active_set = set(active_ids or [])
        evaluated = [
            {
                "modifier_id": m.modifier_id,
                "active":      m.modifier_id in active_set,
                "stat_target": m.stat_target,
                "value":       m.value,
                "type":        m.modifier_type,
            }
            for m in modifiers
        ]
        entry = ConditionalLogEntry(
            tick_time=tick_time,
            state_snapshot=state.snapshot(),
            evaluated_modifiers=evaluated,
            stat_deltas=stat_deltas,
            base_damage=base_damage,
            adjusted_damage=adjusted_damage,
        )
        self._entries.append(entry)

    def entries(self) -> list[ConditionalLogEntry]:
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def dump_to_logger(self) -> None:
        """Write all entries to Python's logging at DEBUG level."""
        for entry in self._entries:
            logger.debug("[conditional] %s", entry.summary())

    def to_list(self) -> list[dict]:
        """Serialise all entries to plain dicts (for API responses)."""
        return [
            {
                "tick_time":       e.tick_time,
                "base_damage":     e.base_damage,
                "adjusted_damage": e.adjusted_damage,
                "stat_deltas":     e.stat_deltas,
                "active_modifiers": [
                    m["modifier_id"] for m in e.evaluated_modifiers if m["active"]
                ],
            }
            for e in self._entries
        ]
