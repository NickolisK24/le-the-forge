"""Read-only loader for the generated v2 modifier registry."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class V2ModifierRegistryError(ValueError):
    """Raised when the generated v2 modifier registry is missing or invalid."""


class V2ModifierRegistry:
    def __init__(self, registry_path: str | Path) -> None:
        self.registry_path = Path(registry_path)
        self._payload: dict[str, Any] | None = None
        self._records: tuple[dict[str, Any], ...] = ()
        self._by_id: dict[str, dict[str, Any]] = {}

    def load(self) -> "V2ModifierRegistry":
        if not self.registry_path.exists():
            raise FileNotFoundError(f"v2 modifier registry not found: {self.registry_path}")
        try:
            payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise V2ModifierRegistryError(f"Invalid JSON in v2 modifier registry {self.registry_path}: {exc}") from exc
        return self.load_payload(payload)

    def load_payload(self, payload: dict[str, Any]) -> "V2ModifierRegistry":
        records = payload.get("records", {}).get("modifiers") if isinstance(payload, dict) else None
        if not isinstance(records, list):
            raise V2ModifierRegistryError("v2 modifier registry records.modifiers must be a list.")
        seen: set[str] = set()
        for index, record in enumerate(records):
            modifier_id = record.get("canonical_modifier_id") if isinstance(record, dict) else None
            if not modifier_id:
                raise V2ModifierRegistryError(f"Modifier registry record {index} is missing canonical_modifier_id.")
            if modifier_id in seen:
                raise V2ModifierRegistryError(f"Duplicate canonical_modifier_id in v2 modifier registry: {modifier_id}")
            seen.add(str(modifier_id))
            if not record.get("source_type"):
                raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is missing source_type.")
            if not record.get("source_id"):
                raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is missing source_id.")
            if not record.get("operation"):
                raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is missing operation.")
            if not record.get("value_scale_status"):
                raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is missing value_scale_status.")
            if not isinstance(record.get("provenance"), dict) or not record["provenance"]:
                raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is missing provenance.")
            if record.get("stable_calculable") is True:
                if record.get("value_scale_status") != "planner_normalized":
                    raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is stable with unsafe value scale.")
                if record.get("source_identity_status") in {"ambiguous", "unresolved"}:
                    raise V2ModifierRegistryError(f"Modifier registry record {modifier_id} is stable with unresolved source identity.")
        self._payload = deepcopy(payload)
        self._records = tuple(deepcopy(record) for record in records)
        self._by_id = {record["canonical_modifier_id"]: record for record in self._records}
        return self

    def list_modifiers(
        self,
        *,
        source_type: str = "",
        stat_id: str = "",
        stable_calculable: bool | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._records)
        if source_type:
            expected = source_type.lower()
            records = [record for record in records if str(record.get("source_type", "")).lower() == expected]
        if stat_id:
            expected = stat_id.lower()
            records = [record for record in records if str(record.get("stat_id", "")).lower() == expected]
        if stable_calculable is not None:
            records = [record for record in records if record.get("stable_calculable") is stable_calculable]
        start = max(0, offset)
        end = None if limit is None else start + max(0, limit)
        return [deepcopy(record) for record in records[start:end]]

    def get_modifier(self, modifier_id: str) -> dict[str, Any] | None:
        record = self._by_id.get(modifier_id)
        return deepcopy(record) if record else None

    def count(self) -> int:
        return len(self._records)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "source_path": str(self.registry_path),
            "modifier_count": self.count(),
            "summary": deepcopy(self._payload.get("summary", {}) if self._payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }
