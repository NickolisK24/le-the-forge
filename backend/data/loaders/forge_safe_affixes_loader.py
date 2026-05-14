"""Controlled loader for Forge-safe canonical affix exports.

This loader is intentionally isolated from production affix systems. It reads
the Forge-safe canonical affix export produced by last-epoch-data and validates
that every accepted record carries the explicit record-level safety flag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ForgeSafeAffixExport",
    "ForgeSafeAffixLoader",
    "ForgeSafeAffixLoaderError",
]


REQUIRED_TOP_LEVEL_FIELDS = ("records", "summary", "export_policy")
REQUIRED_RECORD_FIELDS = ("affix_id", "source_type", "safety")
REQUIRED_SAFETY_FIELDS = ("forge_safe", "export_policy")


class ForgeSafeAffixLoaderError(ValueError):
    """Raised when a Forge-safe affix export cannot be loaded safely."""


@dataclass(frozen=True)
class ForgeSafeAffixExport:
    """Validated Forge-safe affix export payload."""

    records: tuple[dict[str, Any], ...]
    count: int
    warnings: tuple[str, ...]
    source_path: Path
    summary: dict[str, Any]
    export_policy: str | None


class ForgeSafeAffixLoader:
    """Load and validate a Forge-safe canonical affix export JSON file."""

    def load(self, path: str | Path) -> ForgeSafeAffixExport:
        source_path = Path(path)
        payload = self._read_json(source_path)
        return self.load_payload(payload, source_path=source_path)

    def load_payload(
        self,
        payload: dict[str, Any],
        *,
        source_path: str | Path = "<memory>",
    ) -> ForgeSafeAffixExport:
        if not isinstance(payload, dict):
            raise ForgeSafeAffixLoaderError("Forge-safe affix export must be a JSON object.")

        self._validate_top_level(payload)
        records = payload["records"]
        summary = payload["summary"]
        if not isinstance(records, list):
            raise ForgeSafeAffixLoaderError("Forge-safe affix export field 'records' must be a list.")
        if not isinstance(summary, dict):
            raise ForgeSafeAffixLoaderError("Forge-safe affix export field 'summary' must be an object.")

        if payload.get("production_safe") is True:
            raise ForgeSafeAffixLoaderError("Forge-safe affix export must not set top-level production_safe=true.")

        warnings = self._summary_warnings(summary, records)
        self._validate_records(records)
        return ForgeSafeAffixExport(
            records=tuple(records),
            count=len(records),
            warnings=tuple(warnings),
            source_path=Path(source_path),
            summary=dict(summary),
            export_policy=payload.get("export_policy"),
        )

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Forge-safe affix export not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ForgeSafeAffixLoaderError(f"Invalid JSON in Forge-safe affix export {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise ForgeSafeAffixLoaderError(f"Forge-safe affix export must be a JSON object: {path}")
        return data

    @staticmethod
    def _validate_top_level(payload: dict[str, Any]) -> None:
        missing = [field for field in REQUIRED_TOP_LEVEL_FIELDS if field not in payload]
        if missing:
            raise ForgeSafeAffixLoaderError(
                "Forge-safe affix export is missing required top-level fields: "
                + ", ".join(missing)
            )

    @staticmethod
    def _summary_warnings(summary: dict[str, Any], records: list[Any]) -> list[str]:
        warnings: list[str] = []
        exported_count = summary.get("exported_affix_records")
        if exported_count is not None and exported_count != len(records):
            warnings.append(
                "summary.exported_affix_records="
                f"{exported_count} does not match loaded record count {len(records)}."
            )
        if summary.get("forge_safe_records_only") is False:
            warnings.append("summary.forge_safe_records_only is false; records are still validated individually.")
        if summary.get("production_safe") is True:
            raise ForgeSafeAffixLoaderError("Forge-safe affix summary must not set production_safe=true.")
        return warnings

    @staticmethod
    def _validate_records(records: list[Any]) -> None:
        seen_affix_ids: set[Any] = set()
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ForgeSafeAffixLoaderError(f"Record {index} must be an object.")
            missing = [field for field in REQUIRED_RECORD_FIELDS if field not in record]
            if missing:
                raise ForgeSafeAffixLoaderError(
                    f"Record {index} is missing required fields: {', '.join(missing)}."
                )

            affix_id = record["affix_id"]
            if affix_id is None or affix_id == "":
                raise ForgeSafeAffixLoaderError(f"Record {index} has an empty affix_id.")
            if affix_id in seen_affix_ids:
                raise ForgeSafeAffixLoaderError(f"Duplicate affix_id in Forge-safe affix export: {affix_id}")
            seen_affix_ids.add(affix_id)

            if not record.get("source_type"):
                raise ForgeSafeAffixLoaderError(f"Record {index} is missing source_type.")
            if record.get("production_safe") is True:
                raise ForgeSafeAffixLoaderError(f"Record {index} must not set production_safe=true.")

            safety = record["safety"]
            if not isinstance(safety, dict):
                raise ForgeSafeAffixLoaderError(f"Record {index} safety metadata must be an object.")
            safety_missing = [field for field in REQUIRED_SAFETY_FIELDS if field not in safety]
            if safety_missing:
                raise ForgeSafeAffixLoaderError(
                    f"Record {index} safety metadata is missing required fields: {', '.join(safety_missing)}."
                )
            if safety.get("forge_safe") is not True:
                raise ForgeSafeAffixLoaderError(f"Record {index} must have safety.forge_safe=true.")
            if safety.get("production_safe") is True:
                raise ForgeSafeAffixLoaderError(f"Record {index} safety metadata must not set production_safe=true.")
            if not safety.get("export_policy"):
                raise ForgeSafeAffixLoaderError(f"Record {index} is missing safety.export_policy.")
