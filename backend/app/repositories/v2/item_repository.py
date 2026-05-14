"""Read-only v2 canonical item base and implicit repository."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.data_contracts import SupportStatus, TrustLevel, validate_canonical_id


class V2ItemBundleError(ValueError):
    """Raised when v2 item bundles are missing or invalid."""


class V2ItemRepository:
    """Read-only repository over generated v2 item base and implicit bundles."""

    def __init__(self, base_bundle_path: str | Path, implicit_bundle_path: str | Path) -> None:
        self.base_bundle_path = Path(base_bundle_path)
        self.implicit_bundle_path = Path(implicit_bundle_path)
        self._base_payload: dict[str, Any] | None = None
        self._implicit_payload: dict[str, Any] | None = None
        self._bases: tuple[dict[str, Any], ...] = ()
        self._implicits: tuple[dict[str, Any], ...] = ()
        self._bases_by_id: dict[str, dict[str, Any]] = {}
        self._implicits_by_id: dict[str, dict[str, Any]] = {}
        self._implicits_by_base_id: dict[str, tuple[dict[str, Any], ...]] = {}

    def load(self) -> "V2ItemRepository":
        base_payload = _read_json(self.base_bundle_path, "v2 item base bundle")
        implicit_payload = _read_json(self.implicit_bundle_path, "v2 item implicit bundle")
        return self.load_payloads(base_payload, implicit_payload)

    def load_payloads(
        self,
        base_payload: dict[str, Any],
        implicit_payload: dict[str, Any],
    ) -> "V2ItemRepository":
        bases = _records(base_payload, "item_bases", "v2 item base bundle")
        implicits = _records(implicit_payload, "implicits", "v2 item implicit bundle")
        self._validate_bases(bases)
        self._validate_implicits(implicits, {record["canonical_id"] for record in bases})
        self._base_payload = deepcopy(base_payload)
        self._implicit_payload = deepcopy(implicit_payload)
        self._bases = tuple(deepcopy(record) for record in bases)
        self._implicits = tuple(deepcopy(record) for record in implicits)
        self._bases_by_id = {record["canonical_id"]: record for record in self._bases}
        self._implicits_by_id = {record["canonical_id"]: record for record in self._implicits}
        grouped: dict[str, list[dict[str, Any]]] = {}
        for record in self._implicits:
            grouped.setdefault(str(record.get("item_base_id")), []).append(record)
        self._implicits_by_base_id = {key: tuple(values) for key, values in grouped.items()}
        return self

    def list_bases(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._bases, limit=limit, offset=offset)

    def get_base(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._bases_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def filter_bases(
        self,
        *,
        query: str = "",
        slot: str = "",
        item_type: str = "",
        class_id: str = "",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        records = list(self._bases)
        if query:
            needle = query.strip().lower()
            records = [
                record for record in records
                if needle in record["canonical_id"].lower()
                or needle in str(record.get("display_name", "")).lower()
                or needle in str(record.get("source_id", "")).lower()
            ]
        if slot:
            expected = slot.strip().lower()
            records = [record for record in records if str(record.get("slot", "")).lower() == expected]
        if item_type:
            expected = item_type.strip().lower()
            records = [record for record in records if str(record.get("item_type", "")).lower() == expected]
        if class_id:
            expected = class_id.strip().lower()
            records = [
                record for record in records
                if expected in {str(value).lower() for value in record.get("class_restrictions") or []}
            ]
        return _page(tuple(records), limit=limit, offset=offset)

    def list_implicits(self, *, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        return _page(self._implicits, limit=limit, offset=offset)

    def get_implicit(self, canonical_id: str) -> dict[str, Any] | None:
        record = self._implicits_by_id.get(canonical_id)
        return deepcopy(record) if record else None

    def get_implicits_for_base(self, base_id: str) -> list[dict[str, Any]]:
        return [deepcopy(record) for record in self._implicits_by_base_id.get(base_id, ())]

    def count_bases(self) -> int:
        return len(self._bases)

    def count_implicits(self) -> int:
        return len(self._implicits)

    def debug_summary(self) -> dict[str, Any]:
        base_summary = self._base_payload.get("summary", {}) if self._base_payload else {}
        implicit_summary = self._implicit_payload.get("summary", {}) if self._implicit_payload else {}
        return {
            "base_bundle_path": str(self.base_bundle_path),
            "implicit_bundle_path": str(self.implicit_bundle_path),
            "item_base_count": self.count_bases(),
            "implicit_count": self.count_implicits(),
            "base_summary": deepcopy(base_summary),
            "implicit_summary": deepcopy(implicit_summary),
            "production_consumer": False,
            "production_safe": False,
        }

    @staticmethod
    def _validate_bases(records: list[Any]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            _validate_common(record, index, "Item base")
            canonical_id = record["canonical_id"]
            if canonical_id in seen:
                raise V2ItemBundleError(f"Duplicate canonical_id in v2 item base bundle: {canonical_id}")
            seen.add(canonical_id)
            if not record.get("item_category"):
                raise V2ItemBundleError(f"Item base {canonical_id} is missing item_category.")
            if not record.get("item_type"):
                raise V2ItemBundleError(f"Item base {canonical_id} is missing item_type.")
            if record.get("slot") is not None and not isinstance(record.get("slot"), str):
                raise V2ItemBundleError(f"Item base {canonical_id} has invalid slot.")
            if not isinstance(record.get("requirements"), dict):
                raise V2ItemBundleError(f"Item base {canonical_id} has invalid requirements.")
            if not isinstance(record.get("implicit_ids"), list):
                raise V2ItemBundleError(f"Item base {canonical_id} has invalid implicit_ids.")

    @staticmethod
    def _validate_implicits(records: list[Any], base_ids: set[str]) -> None:
        seen: set[str] = set()
        for index, record in enumerate(records):
            _validate_common(record, index, "Implicit")
            canonical_id = record["canonical_id"]
            if canonical_id in seen:
                raise V2ItemBundleError(f"Duplicate canonical_id in v2 item implicit bundle: {canonical_id}")
            seen.add(canonical_id)
            if record.get("item_base_id") not in base_ids:
                raise V2ItemBundleError(f"Implicit {canonical_id} references missing item base: {record.get('item_base_id')}")
            if not isinstance(record.get("modifier_references"), list):
                raise V2ItemBundleError(f"Implicit {canonical_id} has invalid modifier_references.")
            for modifier in record.get("modifier_rows") or []:
                if not isinstance(modifier, dict) or not modifier.get("provenance"):
                    raise V2ItemBundleError(f"Implicit {canonical_id} has modifier row without provenance.")
                if not modifier.get("support_status"):
                    raise V2ItemBundleError(f"Implicit {canonical_id} has modifier row without support_status.")
                if modifier.get("stable_calculable") is True:
                    raise V2ItemBundleError(f"Implicit {canonical_id} has stable-calculable modifier row.")


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise V2ItemBundleError(f"Invalid JSON in {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise V2ItemBundleError(f"{label} must be a JSON object.")
    return payload


def _records(payload: dict[str, Any], key: str, label: str) -> list[Any]:
    records = payload.get("records")
    if not isinstance(records, dict):
        raise V2ItemBundleError(f"{label} records must be an object.")
    values = records.get(key)
    if not isinstance(values, list):
        raise V2ItemBundleError(f"{label} records.{key} must be a list.")
    return values


def _validate_common(record: Any, index: int, label: str) -> None:
    if not isinstance(record, dict):
        raise V2ItemBundleError(f"{label} record {index} must be an object.")
    canonical_id = record.get("canonical_id")
    try:
        validate_canonical_id(canonical_id)
    except ValueError as exc:
        raise V2ItemBundleError(f"{label} record {index} has invalid canonical_id: {exc}") from exc
    if not record.get("display_name"):
        raise V2ItemBundleError(f"{label} {canonical_id} is missing display_name.")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict) or not provenance.get("source_path"):
        raise V2ItemBundleError(f"{label} {canonical_id} is missing provenance.source_path.")
    try:
        status = SupportStatus(str(record.get("support_status")))
    except ValueError as exc:
        raise V2ItemBundleError(f"{label} {canonical_id} has invalid support_status.") from exc
    try:
        trust_level = TrustLevel(str(record.get("trust_level")))
    except ValueError as exc:
        raise V2ItemBundleError(f"{label} {canonical_id} has invalid trust_level.") from exc
    if trust_level in {TrustLevel.GAME_EXTRACTED, TrustLevel.GENERATED_FROM_GAME_DATA}:
        if not provenance.get("source_id") and not record.get("source_id"):
            raise V2ItemBundleError(f"{label} {canonical_id} is missing source reference.")
    if record.get("stable_calculable") is True or status == SupportStatus.TRUSTED:
        raise V2ItemBundleError(f"{label} {canonical_id} is not approved for stable calculation in Phase 4.")


def _page(records: tuple[dict[str, Any], ...], *, limit: int | None, offset: int) -> list[dict[str, Any]]:
    start = max(0, offset)
    end = None if limit is None else start + max(0, limit)
    return [deepcopy(record) for record in records[start:end]]
