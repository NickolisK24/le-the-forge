from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class VisLogEntry:
    event_type: str       # "cache_hit", "cache_miss", "generated", "error", "export"
    simulation_key: str | None
    component: str        # "timeline", "heatmap", "replay", "report", "summary"
    duration_ms: float
    metadata: dict
    timestamp: float = field(default_factory=time.time)


class VisualizationLogger:
    def __init__(self, capacity: int = 500) -> None:
        self._entries: deque[VisLogEntry] = deque(maxlen=capacity)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _append(
        self,
        event_type: str,
        simulation_key: str | None,
        component: str,
        duration_ms: float,
        metadata: dict,
    ) -> None:
        self._entries.append(
            VisLogEntry(
                event_type=event_type,
                simulation_key=simulation_key,
                component=component,
                duration_ms=duration_ms,
                metadata=metadata,
            )
        )

    def log_cache_hit(self, simulation_key: str, component: str) -> None:
        """Record a cache hit event."""
        self._append("cache_hit", simulation_key, component, 0.0, {})

    def log_cache_miss(self, simulation_key: str, component: str) -> None:
        """Record a cache miss event."""
        self._append("cache_miss", simulation_key, component, 0.0, {})

    def log_generated(
        self,
        simulation_key: str,
        component: str,
        duration_ms: float,
        metadata: dict | None = None,
    ) -> None:
        """Record a successful visualization generation event."""
        self._append("generated", simulation_key, component, duration_ms, metadata or {})

    def log_error(
        self,
        simulation_key: str | None,
        component: str,
        error: str,
    ) -> None:
        """Record an error event."""
        self._append("error", simulation_key, component, 0.0, {"error": error})

    def log_export(
        self,
        simulation_key: str,
        format: str,
        size_bytes: int,
    ) -> None:
        """Record a report export event."""
        self._append(
            "export",
            simulation_key,
            "report",
            0.0,
            {"format": format, "size_bytes": size_bytes},
        )

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_entries(
        self,
        event_type: str | None = None,
        component: str | None = None,
    ) -> list[VisLogEntry]:
        """
        Return log entries optionally filtered by *event_type* and/or
        *component*.  Both filters are ANDed together.
        """
        results: list[VisLogEntry] = []
        for entry in self._entries:
            if event_type is not None and entry.event_type != event_type:
                continue
            if component is not None and entry.component != component:
                continue
            results.append(entry)
        return results

    def summary(self) -> dict:
        """
        Return aggregate statistics::

            {
                "total_entries": int,
                "by_type": {event_type: count, ...},
                "by_component": {component: count, ...},
                "avg_generation_ms": float,  # mean duration_ms for "generated" events
            }
        """
        by_type: dict[str, int] = {}
        by_component: dict[str, int] = {}
        generated_durations: list[float] = []

        for entry in self._entries:
            by_type[entry.event_type] = by_type.get(entry.event_type, 0) + 1
            by_component[entry.component] = by_component.get(entry.component, 0) + 1
            if entry.event_type == "generated":
                generated_durations.append(entry.duration_ms)

        avg_generation_ms = (
            sum(generated_durations) / len(generated_durations)
            if generated_durations
            else 0.0
        )

        return {
            "total_entries": len(self._entries),
            "by_type": by_type,
            "by_component": by_component,
            "avg_generation_ms": avg_generation_ms,
        }

    def clear(self) -> None:
        """Remove all log entries."""
        self._entries.clear()
