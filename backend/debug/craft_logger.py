from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
import time


@dataclass
class CraftLogEntry:
    event_type: str   # "craft", "fracture", "success", "failure", "glyph", "rune"
    item_id: str | None
    action_type: str | None
    fp_before: int
    fp_after: int
    instability: int
    metadata: dict
    timestamp: float = field(default_factory=time.time)


class CraftLogger:
    def __init__(self, capacity: int = 2000):
        self._entries: deque[CraftLogEntry] = deque(maxlen=capacity)

    def log_craft(self, item_id: str, action_type: str, fp_before: int, fp_after: int,
                  instability: int, metadata: dict | None = None) -> None:
        self._entries.append(CraftLogEntry("craft", item_id, action_type, fp_before, fp_after, instability, metadata or {}))

    def log_fracture(self, item_id: str, fracture_type: str, fp_remaining: int, instability: int) -> None:
        self._entries.append(CraftLogEntry("fracture", item_id, None, fp_remaining, fp_remaining, instability,
                                           {"fracture_type": fracture_type}))

    def log_success(self, item_id: str, score: float, fp_spent: int, total_crafts: int) -> None:
        self._entries.append(CraftLogEntry("success", item_id, None, 0, 0, 0,
                                           {"score": score, "fp_spent": fp_spent, "crafts": total_crafts}))

    def log_failure(self, item_id: str, reason: str, fp_spent: int) -> None:
        self._entries.append(CraftLogEntry("failure", item_id, None, 0, 0, 0,
                                           {"reason": reason, "fp_spent": fp_spent}))

    def log_glyph(self, item_id: str, glyph_type: str, fp_before: int, fp_after: int) -> None:
        self._entries.append(CraftLogEntry("glyph", item_id, glyph_type, fp_before, fp_after, 0, {}))

    def log_rune(self, item_id: str, rune_type: str, affix_affected: str | None) -> None:
        self._entries.append(CraftLogEntry("rune", item_id, rune_type, 0, 0, 0,
                                           {"affix_affected": affix_affected}))

    def get_entries(self, event_type: str | None = None, item_id: str | None = None) -> list[CraftLogEntry]:
        entries = list(self._entries)
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        if item_id:
            entries = [e for e in entries if e.item_id == item_id]
        return entries

    def summary(self) -> dict:
        entries = list(self._entries)
        by_type = {}
        for e in entries:
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
        fractures = by_type.get("fracture", 0)
        successes = by_type.get("success", 0)
        total_crafts = by_type.get("craft", 0)
        return {"total_entries": len(entries), "by_type": by_type,
                "fracture_rate": fractures / max(total_crafts, 1),
                "success_count": successes}

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)
