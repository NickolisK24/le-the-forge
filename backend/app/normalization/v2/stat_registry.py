"""Read-only loader for the generated v2 stat registry."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class V2StatRegistryError(ValueError):
    """Raised when the generated v2 stat registry is missing or invalid."""


class V2StatRegistry:
    def __init__(self, registry_path: str | Path) -> None:
        self.registry_path = Path(registry_path)
        self._payload: dict[str, Any] | None = None
        self._records: tuple[dict[str, Any], ...] = ()
        self._by_id: dict[str, dict[str, Any]] = {}

    def load(self) -> "V2StatRegistry":
        if not self.registry_path.exists():
            raise FileNotFoundError(f"v2 stat registry not found: {self.registry_path}")
        try:
            payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise V2StatRegistryError(f"Invalid JSON in v2 stat registry {self.registry_path}: {exc}") from exc
        return self.load_payload(payload)

    def load_payload(self, payload: dict[str, Any]) -> "V2StatRegistry":
        records = payload.get("records", {}).get("stats") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise V2StatRegistryError("v2 stat registry records.stats must be a list.")
        seen: set[str] = set()
        for index, record in enumerate(records):
            stat_id = record.get("canonical_stat_id") if isinstance(record, dict) else None
            if not stat_id:
                raise V2StatRegistryError(f"Stat registry record {index} is missing canonical_stat_id.")
            if stat_id in seen:
                raise V2StatRegistryError(f"Duplicate canonical_stat_id in v2 stat registry: {stat_id}")
            seen.add(str(stat_id))
        self._payload = deepcopy(payload)
        self._records = tuple(deepcopy(record) for record in records)
        self._by_id = {record["canonical_stat_id"]: record for record in self._records}
        return self

    def list_stats(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in self._records[start:end]]

    def get_stat(self, stat_id: str) -> dict[str, Any] | None:
        record = self._by_id.get(stat_id)
        return deepcopy(record) if record else None

    def count(self) -> int:
        return len(self._records)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "source_path": str(self.registry_path),
            "stat_count": self.count(),
            "summary": deepcopy(self._payload.get("summary", {}) if self._payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }
