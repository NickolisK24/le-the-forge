"""Read-only v2 idol repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2IdolBundleError(ValueError):
    """Raised when v2 idol bundles are missing or invalid."""


class V2IdolRepository:
    """Read-only repository over generated v2 idol and idol-affix bundles."""

    def __init__(self, idol_bundle_path: str | Path, idol_affix_bundle_path: str | Path) -> None:
        self.idol_bundle_path = Path(idol_bundle_path)
        self.idol_affix_bundle_path = Path(idol_affix_bundle_path)
        self._idol_payload: dict[str, Any] | None = None
        self._affix_payload: dict[str, Any] | None = None
        self._idols: tuple[dict[str, Any], ...] = ()
        self._affixes: tuple[dict[str, Any], ...] = ()
        self._idols_by_id: dict[str, dict[str, Any]] = {}
        self._affixes_by_id: dict[str, dict[str, Any]] = {}

    def load(self) -> "V2IdolRepository":
        return self.load_payloads(
            _read_json(self.idol_bundle_path, "v2 idol bundle"),
            _read_json(self.idol_affix_bundle_path, "v2 idol affix bundle"),
        )

    def load_payloads(self, idol_payload: dict[str, Any], affix_payload: dict[str, Any]) -> "V2IdolRepository":
        idols = _records(idol_payload, "idols", "v2 idol bundle")
        affixes = _records(affix_payload, "idol_affixes", "v2 idol affix bundle")
        self._validate_idols(idols)
        self._validate_affixes(affixes)
        self._idol_payload = deepcopy(idol_payload)
        self._affix_payload = deepcopy(affix_payload)
        self._idols = tuple(deepcopy(record) for record in idols)
        self._affixes = tuple(deepcopy(record) for record in affixes)
        self._idols_by_id = {record["canonical_id"]: record for record in self._idols}
        self._affixes_by_id = {record["canonical_id"]: record for record in self._affixes}
        return self

    def list_idols(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._idols, limit=limit, offset=offset)

    def get_idol(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._idols_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_idols(
        self,
        *,
        query: str = "",
        shape: str = "",
        class_id: str = "",
        mastery: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._idols)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        if shape:
            expected = shape.strip().lower()
            records = [record for record in records if str(record.get("idol_shape", "")).lower() == expected]
        if class_id:
            expected = class_id.strip().lower()
            records = [record for record in records if expected in {str(value).lower() for value in record.get("class_restrictions") or []}]
        if mastery:
            expected = mastery.strip().lower()
            records = [record for record in records if expected in {str(value).lower() for value in record.get("mastery_restrictions") or []}]
        return _page(tuple(records), limit=limit, offset=offset)

    def list_affixes(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._affixes, limit=limit, offset=offset)

    def get_affix(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._affixes_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_affixes(
        self,
        *,
        query: str = "",
        idol_type: str = "",
        class_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._affixes)
        if query:
            needle = query.strip().lower()
            records = [record for record in records if needle in record["canonical_id"].lower() or needle in str(record.get("display_name", "")).lower()]
        if idol_type:
            expected = idol_type.strip().lower()
            records = [record for record in records if expected in {str(value).lower() for value in record.get("idol_type_restrictions") or []}]
        if class_id:
            expected = class_id.strip().lower()
            records = [record for record in records if expected in {str(value).lower() for value in record.get("class_restrictions") or []}]
        return _page(tuple(records), limit=limit, offset=offset)

    def count_idols(self) -> int:
        return len(self._idols)

    def count_affixes(self) -> int:
        return len(self._affixes)

    def debug_summary(self) -> dict[str, Any]:
        return {
            "idol_bundle_path": str(self.idol_bundle_path),
            "idol_affix_bundle_path": str(self.idol_affix_bundle_path),
            "idol_count": self.count_idols(),
            "idol_affix_count": self.count_affixes(),
            "idol_summary": deepcopy(self._idol_payload.get("summary", {}) if self._idol_payload else {}),
            "idol_affix_summary": deepcopy(self._affix_payload.get("summary", {}) if self._affix_payload else {}),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate_idols(records: list[Any]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            _validate_common(record, index, "Idol")
            canonical_id = record["canonical_id"]
            if canonical_id in seen:
                raise V2IdolBundleError(f"Duplicate canonical_id in v2 idol bundle: {canonical_id}")
            seen.add(canonical_id)
            dimensions = record.get("dimensions")
            if not isinstance(dimensions, dict) or not isinstance(dimensions.get("width"), int) or not isinstance(dimensions.get("height"), int):
                raise V2IdolBundleError(f"Idol {canonical_id} has invalid dimensions.")
            if not record.get("idol_shape"):
                raise V2IdolBundleError(f"Idol {canonical_id} is missing idol_shape.")

    @staticmethod
    def _validate_affixes(records: list[Any]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            _validate_common(record, index, "Idol affix")
            canonical_id = record["canonical_id"]
            if canonical_id in seen:
                raise V2IdolBundleError(f"Duplicate canonical_id in v2 idol affix bundle: {canonical_id}")
            seen.add(canonical_id)
            if record.get("affix_domain") != "idol" or str(canonical_id).startswith("affix:equipment:"):
                raise V2IdolBundleError(f"Idol affix {canonical_id} mixes idol and equipment domains.")
            if not isinstance(record.get("idol_type_restrictions"), list):
                raise V2IdolBundleError(f"Idol affix {canonical_id} has invalid idol_type_restrictions.")
            if not isinstance(record.get("tier_ranges"), list) or not record.get("tier_ranges"):
                raise V2IdolBundleError(f"Idol affix {canonical_id} is missing tier_ranges.")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2IdolBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2IdolBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str, label: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict) or not isinstance(records.get(key), list):
        raise V2IdolBundleError(f"{label} records.{key} must be a list.")
    return records[key]


def _validate_common(record: Any, index: int, label: str) -> None:
    if not isinstance(record, dict):
        raise V2IdolBundleError(f"{label} record {index} must be an object.")
    canonical_id = record.get("canonical_id")
    try:
        validate_canonical_id(canonical_id)
    except ValueError as exc:
        raise V2IdolBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
    provenance = record.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("source_path"):
        raise V2IdolBundleError(f"{label} {canonical_id} is missing provenance.source_path.")
    try:
        status = SupportStatus(str(record.get("support_status")))
    except ValueError as exc:
        raise V2IdolBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
    try:
        TrustLevel(str(record.get("trust_level")))
    except ValueError as exc:
        raise V2IdolBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
    if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
        raise V2IdolBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 6.")
    for modifier in record.get("modifier_rows") or []:
        if not isinstance(modifier, dict) or not modifier.get("provenance"):
            raise V2IdolBundleError(f"{label} {canonical_id} has modifier row without provenance.")
        if not modifier.get("support_status"):
            raise V2IdolBundleError(f"{label} {canonical_id} has modifier row without support_status.")


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
