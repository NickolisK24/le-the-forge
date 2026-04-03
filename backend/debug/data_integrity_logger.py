"""
J15 — Data Integrity Logger

Tracks data mismatches, schema validation failures, and mapping errors
encountered during a data-loading pass.  Provides a structured log that
can be returned to API callers or persisted for debugging.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = ["DataIntegrityLogger", "IntegrityRecord", "Severity"]

_log = logging.getLogger(__name__)


class Severity(str, Enum):
    INFO    = "info"
    WARNING = "warning"
    ERROR   = "error"


@dataclass
class IntegrityRecord:
    """A single integrity-check entry."""

    severity:   Severity
    category:   str          # e.g. "skill", "affix", "enemy"
    item_id:    str          # which item triggered the record
    message:    str
    timestamp:  float = field(default_factory=time.time)
    context:    dict  = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "severity":  self.severity.value,
            "category":  self.category,
            "item_id":   self.item_id,
            "message":   self.message,
            "timestamp": self.timestamp,
            "context":   self.context,
        }


class DataIntegrityLogger:
    """
    Ring-buffer integrity logger for game-data loading passes.

    Parameters
    ----------
    max_entries:
        Maximum number of records to keep in the buffer (FIFO eviction).
    """

    def __init__(self, max_entries: int = 500) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max = max_entries
        self._buffer: deque[IntegrityRecord] = deque(maxlen=max_entries)

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        severity: Severity,
        category: str,
        item_id: str,
        message: str,
        context: dict | None = None,
    ) -> None:
        """Append a new record to the buffer."""
        rec = IntegrityRecord(
            severity=severity,
            category=category,
            item_id=item_id,
            message=message,
            context=context or {},
        )
        self._buffer.append(rec)

    def info(self, category: str, item_id: str, message: str, **ctx) -> None:
        self.record(Severity.INFO, category, item_id, message, ctx)

    def warning(self, category: str, item_id: str, message: str, **ctx) -> None:
        self.record(Severity.WARNING, category, item_id, message, ctx)

    def error(self, category: str, item_id: str, message: str, **ctx) -> None:
        self.record(Severity.ERROR, category, item_id, message, ctx)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def to_list(self, severity: Severity | None = None) -> list[dict]:
        """
        Return all records as dicts, optionally filtered by *severity*.
        """
        records = self._buffer
        if severity is not None:
            records = [r for r in records if r.severity == severity]
        return [r.to_dict() for r in records]

    def error_count(self) -> int:
        return sum(1 for r in self._buffer if r.severity == Severity.ERROR)

    def warning_count(self) -> int:
        return sum(1 for r in self._buffer if r.severity == Severity.WARNING)

    def has_errors(self) -> bool:
        return self.error_count() > 0

    def clear(self) -> None:
        self._buffer.clear()

    def summary(self) -> dict:
        return {
            "total": len(self._buffer),
            "errors": self.error_count(),
            "warnings": self.warning_count(),
            "infos": sum(1 for r in self._buffer if r.severity == Severity.INFO),
        }

    def dump_to_logger(self) -> None:
        """Write all buffered records to the Python logging system."""
        for rec in self._buffer:
            msg = f"[{rec.category}:{rec.item_id}] {rec.message}"
            if rec.severity == Severity.ERROR:
                _log.error(msg)
            elif rec.severity == Severity.WARNING:
                _log.warning(msg)
            else:
                _log.info(msg)
