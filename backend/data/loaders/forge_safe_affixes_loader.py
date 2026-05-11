"""Loader for Forge-safe canonical affix exports.

The export is intentionally consumed as read-only data.  This loader refuses
records that are not explicitly marked ``safety.forge_safe=true`` and also
refuses records marked ``production_safe=true`` because that flag is not part of
Forge's current consumption contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ForgeSafeAffixLoadError(RuntimeError):
    """Raised when the Forge-safe export cannot be loaded safely."""


@dataclass(frozen=True)
class ForgeSafeAffixRecord:
    id: str
    name: str
    source_type: str | None
    item_types: tuple[str, ...]
    raw: dict[str, Any]

    def to_catalog_dict(self) -> dict[str, Any]:
        safety = self.raw.get("safety") if isinstance(self.raw.get("safety"), dict) else {}
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type,
            "item_types": list(self.item_types),
            "data_source": "forge_safe",
            "safety": {"forge_safe": bool(safety.get("forge_safe"))},
            "production_consumer": False,
            "raw": self.raw,
        }


class ForgeSafeAffixLoader:
    """Load and validate canonical Forge-safe affix exports."""

    def __init__(self, export_path: str | Path) -> None:
        self.export_path = Path(export_path)

    def load(self) -> list[ForgeSafeAffixRecord]:
        if not self.export_path:
            raise ForgeSafeAffixLoadError("Forge-safe affix export path is not configured")
        if not self.export_path.exists():
            raise ForgeSafeAffixLoadError(f"Forge-safe affix export not found: {self.export_path}")

        try:
            payload = json.loads(self.export_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ForgeSafeAffixLoadError(f"Invalid Forge-safe affix JSON: {exc}") from exc
        except OSError as exc:
            raise ForgeSafeAffixLoadError(f"Could not read Forge-safe affix export: {exc}") from exc

        records_payload = self._extract_records(payload)
        records: list[ForgeSafeAffixRecord] = []
        rejected_production_safe = 0
        for raw in records_payload:
            if not isinstance(raw, dict):
                continue
            if raw.get("production_safe") is True:
                rejected_production_safe += 1
                continue
            safety = raw.get("safety") if isinstance(raw.get("safety"), dict) else {}
            if safety.get("forge_safe") is not True:
                continue
            affix_id = self._first_string(raw, "id", "affix_id", "canonical_id")
            name = self._first_string(raw, "name", "display_name")
            if not affix_id or not name:
                continue
            records.append(
                ForgeSafeAffixRecord(
                    id=affix_id,
                    name=name,
                    source_type=self._first_string(raw, "source_type", "type", "affix_type") or None,
                    item_types=tuple(self._item_types(raw)),
                    raw=dict(raw),
                )
            )

        if rejected_production_safe:
            # Clean failure: the current contract explicitly excludes these records.
            raise ForgeSafeAffixLoadError(
                f"Forge-safe export contains {rejected_production_safe} production_safe=true record(s), which are not accepted"
            )
        return records

    @staticmethod
    def _extract_records(payload: Any) -> list[Any]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("affixes", "records", "data", "canonical_affixes"):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        raise ForgeSafeAffixLoadError("Forge-safe affix export must be a list or contain an affixes/records/data list")

    @staticmethod
    def _first_string(raw: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, int):
                return str(value)
        return ""

    @staticmethod
    def _item_types(raw: dict[str, Any]) -> list[str]:
        for key in ("item_types", "applicable_to", "rolls_on_item_types"):
            value = raw.get(key)
            if isinstance(value, list):
                return [str(v) for v in value if str(v)]
            if isinstance(value, str) and value.strip():
                return [value.strip()]
        return []
