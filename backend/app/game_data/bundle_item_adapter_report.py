"""Developer-only proposed adapter report for bundle item_types migration."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from pathlib import Path
from typing import Any

from app.game_data.bundle_compat import resolve_bundle_dir


BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent

READINESS_READY = "Ready candidate"
READINESS_NEEDS_ADAPTER = "Needs adapter"
READINESS_NEEDS_REVIEW = "Needs review"
READINESS_NOT_COMPARABLE = "Not comparable"
READINESS_DEFERRED = "Deferred"
READINESS_UNSAFE = "Unsafe"

MATCH_BASE_TYPE_ID = "base_type_id"
MATCH_EXACT_SLUG = "exact_slug"
MATCH_GAME_TYPE = "game_type"
MATCH_NORMALIZED_NAME = "normalized_name"
MATCH_MANUAL_REVIEW = "manual_review"
MATCH_NONE = "none"

PRODUCTION_DATA_SEGMENTS = {
    ("data", "items"),
    ("backend", "app", "constants"),
    ("frontend", "src", "constants"),
}


@dataclass
class AdapterRecord:
    forge_item_type: str | None
    forge_slot: str | None
    bundle_item_type_id: str | None
    bundle_base_type_id: int | None
    match_method: str
    readiness: str
    confidence: str
    production_safe: bool = False
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "forge_item_type": self.forge_item_type,
            "forge_slot": self.forge_slot,
            "bundle_item_type_id": self.bundle_item_type_id,
            "bundle_base_type_id": self.bundle_base_type_id,
            "match_method": self.match_method,
            "readiness": self.readiness,
            "confidence": self.confidence,
            "production_safe": self.production_safe,
            "notes": self.notes,
        }


@dataclass
class AdapterReport:
    bundle_dir: str
    bundle_item_types_count: int
    forge_static_item_type_count: int
    forge_item_type_id_count: int
    forge_base_type_mapping_count: int
    adapter_records: list[AdapterRecord]
    unmapped_forge_types: list[str]
    unmapped_bundle_item_types: list[dict[str, Any]]
    subtype_identity_risk: str | None
    readiness_counts: dict[str, int]
    match_method_counts: dict[str, int]
    safety_warnings: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_dir": self.bundle_dir,
            "bundle_item_types_count": self.bundle_item_types_count,
            "forge_static_item_type_count": self.forge_static_item_type_count,
            "forge_item_type_id_count": self.forge_item_type_id_count,
            "forge_base_type_mapping_count": self.forge_base_type_mapping_count,
            "adapter_record_count": len(self.adapter_records),
            "adapter_records": [record.to_dict() for record in self.adapter_records],
            "unmapped_forge_types": self.unmapped_forge_types,
            "unmapped_bundle_item_types": self.unmapped_bundle_item_types,
            "subtype_identity_risk": self.subtype_identity_risk,
            "readiness_counts": self.readiness_counts,
            "readiness_summary": self.readiness_counts,
            "match_method_counts": self.match_method_counts,
            "match_method_summary": self.match_method_counts,
            "safety_warnings": self.safety_warnings,
            "recommendation": self.recommendation,
        }


def generate_adapter_report(bundle_dir: str | Path | None = None) -> AdapterReport:
    resolved_bundle_dir = resolve_bundle_dir(bundle_dir)
    bundle_item_types = _load_bundle_item_types(resolved_bundle_dir)
    forge_sources = load_forge_mapping_sources()
    return build_adapter_report(bundle_item_types, forge_sources, resolved_bundle_dir)


def build_adapter_report(
    bundle_item_types: list[dict[str, Any]],
    forge_sources: dict[str, Any],
    bundle_dir: Path | str = "",
) -> AdapterReport:
    by_base_type_id = {
        record.get("base_type_id"): record
        for record in bundle_item_types
        if isinstance(record.get("base_type_id"), int)
    }
    by_id = {
        record.get("id"): record
        for record in bundle_item_types
        if isinstance(record.get("id"), str)
    }
    by_normalized_name = {
        _slug(record.get("name")): record
        for record in bundle_item_types
        if record.get("name")
    }

    static_item_types = forge_sources.get("data_item_types") or []
    static_by_id = {
        record.get("id"): record
        for record in static_item_types
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    forge_item_type_ids = set(forge_sources.get("item_type_ids") or [])
    forge_slots = forge_sources.get("item_type_to_slot") or {}
    base_type_map = forge_sources.get("base_type_id_to_item_type_id") or {}

    records: list[AdapterRecord] = []
    mapped_bundle_ids: set[str] = set()
    mapped_forge_types: set[str] = set()

    for base_type_id, forge_type in sorted(base_type_map.items(), key=lambda item: int(item[0])):
        bundle_record = by_base_type_id.get(int(base_type_id))
        if bundle_record is None:
            records.append(
                AdapterRecord(
                    forge_item_type=forge_type,
                    forge_slot=forge_slots.get(forge_type),
                    bundle_item_type_id=None,
                    bundle_base_type_id=int(base_type_id),
                    match_method=MATCH_BASE_TYPE_ID,
                    readiness=READINESS_NOT_COMPARABLE,
                    confidence="Unknown",
                    notes=["Forge has a base_type_id mapping, but the bundle has no matching item_type record."],
                )
            )
            mapped_forge_types.add(forge_type)
            continue

        bundle_id = bundle_record.get("id")
        readiness = READINESS_READY if bundle_id == forge_type else READINESS_NEEDS_ADAPTER
        notes = ["ID-backed match through BASE_TYPE_ID_TO_ITEM_TYPE_ID."]
        if readiness == READINESS_NEEDS_ADAPTER:
            notes.append("Forge slug differs from bundle item_type.id; adapter translation is required.")
        records.append(
            AdapterRecord(
                forge_item_type=forge_type,
                forge_slot=forge_slots.get(forge_type),
                bundle_item_type_id=bundle_id,
                bundle_base_type_id=int(base_type_id),
                match_method=MATCH_BASE_TYPE_ID,
                readiness=readiness,
                confidence="Verified",
                notes=notes,
            )
        )
        mapped_bundle_ids.add(str(bundle_id))
        mapped_forge_types.add(str(forge_type))

    for forge_type in sorted(forge_item_type_ids | set(static_by_id)):
        if forge_type in mapped_forge_types:
            continue
        bundle_record = by_id.get(forge_type)
        if bundle_record:
            readiness = READINESS_NEEDS_REVIEW
            match_method = MATCH_EXACT_SLUG
            confidence = "Partial"
            notes = ["Slug matches, but there is no base_type_id-backed mapping."]
        else:
            static_record = static_by_id.get(forge_type, {})
            bundle_record = by_normalized_name.get(_slug(static_record.get("name")))
            readiness = READINESS_NEEDS_REVIEW if bundle_record else READINESS_NOT_COMPARABLE
            match_method = MATCH_NORMALIZED_NAME if bundle_record else MATCH_NONE
            confidence = "Partial" if bundle_record else "Unknown"
            notes = (
                ["Normalized name match only; not production-authoritative."]
                if bundle_record
                else ["No bundle item_type match found from ID or normalized name."]
            )
        records.append(
            AdapterRecord(
                forge_item_type=forge_type,
                forge_slot=forge_slots.get(forge_type),
                bundle_item_type_id=bundle_record.get("id") if bundle_record else None,
                bundle_base_type_id=bundle_record.get("base_type_id") if bundle_record else None,
                match_method=match_method,
                readiness=readiness,
                confidence=confidence,
                notes=notes,
            )
        )
        mapped_forge_types.add(forge_type)
        if bundle_record:
            mapped_bundle_ids.add(str(bundle_record.get("id")))

    unmapped_bundle = []
    for record in bundle_item_types:
        bundle_id = record.get("id")
        if bundle_id in mapped_bundle_ids:
            continue
        readiness = _unmapped_bundle_readiness(record)
        unmapped_bundle.append(
            {
                "bundle_item_type_id": bundle_id,
                "bundle_base_type_id": record.get("base_type_id"),
                "name": record.get("name"),
                "category": record.get("category"),
                "readiness": readiness,
            }
        )
        records.append(
            AdapterRecord(
                forge_item_type=None,
                forge_slot=None,
                bundle_item_type_id=bundle_id,
                bundle_base_type_id=record.get("base_type_id"),
                match_method=MATCH_MANUAL_REVIEW if readiness == READINESS_NEEDS_REVIEW else MATCH_NONE,
                readiness=readiness,
                confidence="Unknown" if readiness == READINESS_DEFERRED else "Partial",
                notes=["Bundle item_type has no current Forge mapping."],
            )
        )

    subtype_map = forge_sources.get("subtype_id_to_item_type_id") or {}
    subtype_risk = None
    if subtype_map:
        subtype_risk = (
            "Forge subtype_id-only mapping is non-empty. Do not use it for adapter records; "
            "subtype_id is scoped by base_type_id."
        )

    readiness_counts = _count_by(records, "readiness")
    match_method_counts = _count_by(records, "match_method")
    unmapped_forge = sorted(
        record.forge_item_type
        for record in records
        if record.forge_item_type and record.bundle_item_type_id is None
    )
    safety_warnings = [
        "production_safe is false for every proposed adapter record.",
        "This report is diagnostic-only and does not activate bundle-backed production loading.",
    ]
    if subtype_risk:
        safety_warnings.append(subtype_risk)

    return AdapterReport(
        bundle_dir=str(bundle_dir),
        bundle_item_types_count=len(bundle_item_types),
        forge_static_item_type_count=len(static_item_types) if isinstance(static_item_types, list) else 0,
        forge_item_type_id_count=len(forge_item_type_ids),
        forge_base_type_mapping_count=len(base_type_map),
        adapter_records=records,
        unmapped_forge_types=unmapped_forge,
        unmapped_bundle_item_types=unmapped_bundle,
        subtype_identity_risk=subtype_risk,
        readiness_counts=readiness_counts,
        match_method_counts=match_method_counts,
        safety_warnings=safety_warnings,
        recommendation=(
            "Review Needs adapter and Deferred records manually, then add tests for accepted "
            "item type mappings before any production loader migration."
        ),
    )


def assert_report_safety_invariants(report: AdapterReport) -> tuple[list[str], list[str]]:
    """Return developer diagnostic invariant errors and warnings for a report."""
    errors: list[str] = []
    warnings: list[str] = []

    if any(record.production_safe for record in report.adapter_records):
        errors.append("All adapter records must keep production_safe=false.")
    if any(record.match_method == "subtype_id" for record in report.adapter_records):
        errors.append("Adapter records must not use subtype_id-only matching.")
    if not report.adapter_records:
        errors.append("Adapter report produced no records.")
    if report.readiness_counts.get(READINESS_READY, 0) < 1:
        errors.append("Expected at least one Ready candidate mapping.")
    if report.readiness_counts.get(READINESS_NEEDS_ADAPTER, 0) < 1:
        errors.append("Expected at least one Needs adapter mapping.")
    if (
        report.readiness_counts.get(READINESS_DEFERRED, 0)
        + report.readiness_counts.get(READINESS_NEEDS_REVIEW, 0)
        < 1
    ):
        errors.append("Expected at least one Deferred or Needs review mapping.")
    if not report.readiness_counts:
        errors.append("Missing readiness counts.")
    if not report.match_method_counts:
        errors.append("Missing match method counts.")
    if "subtype_id" in report.match_method_counts:
        errors.append("Match method summary must not include subtype_id.")

    if not report.unmapped_forge_types:
        warnings.append("No unmapped Forge item types were reported.")

    return errors, warnings


def load_forge_mapping_sources() -> dict[str, Any]:
    sources: dict[str, Any] = {}
    item_types_path = REPO_ROOT / "data" / "items" / "item_types.json"
    if item_types_path.exists():
        sources["data_item_types"] = json.loads(item_types_path.read_text(encoding="utf-8"))

    from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
    from app.constants.game_type_to_item_type_id import GAME_TYPE_TO_ITEM_TYPE_ID
    from app.constants.item_type_ids import ITEM_TYPE_IDS
    from app.constants.item_type_to_slot import ITEM_TYPE_TO_SLOT
    from app.constants.sub_type_id_to_item_type_id import SUBTYPE_ID_TO_ITEM_TYPE_ID

    sources["base_type_id_to_item_type_id"] = dict(BASE_TYPE_ID_TO_ITEM_TYPE_ID)
    sources["game_type_to_item_type_id"] = dict(GAME_TYPE_TO_ITEM_TYPE_ID)
    sources["item_type_ids"] = list(ITEM_TYPE_IDS)
    sources["item_type_to_slot"] = dict(ITEM_TYPE_TO_SLOT)
    sources["subtype_id_to_item_type_id"] = dict(SUBTYPE_ID_TO_ITEM_TYPE_ID)
    return sources


def render_adapter_report(report: AdapterReport) -> str:
    lines = [
        "# Bundle Item Adapter Map Report",
        "",
        f"Bundle path: `{report.bundle_dir}`",
        "",
        "## Summary",
        "",
        f"- Bundle item_types: {report.bundle_item_types_count}",
        f"- Forge static item types: {report.forge_static_item_type_count}",
        f"- Forge item type IDs: {report.forge_item_type_id_count}",
        f"- Forge base_type_id mappings: {report.forge_base_type_mapping_count}",
        f"- Adapter records: {len(report.adapter_records)}",
        "- production_safe: false for every proposed record",
        "",
        "## Readiness Counts",
        "",
        *_format_counts(report.readiness_counts),
        "",
        "## Match Method Counts",
        "",
        *_format_counts(report.match_method_counts),
        "",
        "## Unmapped Forge Types",
        "",
        *_format_list(report.unmapped_forge_types),
        "",
        "## Unmapped Bundle Item Types",
        "",
        *_format_bundle_unmapped(report.unmapped_bundle_item_types),
        "",
        "## Subtype Identity Risk",
        "",
        report.subtype_identity_risk or "No active subtype_id-only mapping was detected.",
        "",
        "## Safety Warnings",
        "",
        *_format_list(report.safety_warnings),
        "",
        "## Proposed Adapter Records",
        "",
    ]
    for record in report.adapter_records:
        lines.append(
            f"- forge={record.forge_item_type or 'null'} slot={record.forge_slot or 'null'} "
            f"bundle={record.bundle_item_type_id or 'null'} base_type_id={record.bundle_base_type_id} "
            f"method={record.match_method} readiness={record.readiness} confidence={record.confidence} "
            "production_safe=false"
        )
        for note in record.notes:
            lines.append(f"  - {note}")
    lines.extend(["", "## Recommendation", "", report.recommendation, ""])
    return "\n".join(lines)


def validate_output_path(path: Path) -> None:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return
    parts = tuple(part.lower() for part in relative.parts)
    for segment in PRODUCTION_DATA_SEGMENTS:
        if parts[: len(segment)] == segment:
            raise ValueError(f"Refusing to write adapter report into production data path: {path}")


def _load_bundle_item_types(bundle_dir: Path) -> list[dict[str, Any]]:
    path = bundle_dir / "families" / "item_types.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing bundle item_types file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("family") != "item_types":
        raise ValueError("families/item_types.json must be an object with family=item_types")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("families/item_types.json records must be a list")
    return [record for record in records if isinstance(record, dict)]


def _unmapped_bundle_readiness(record: dict[str, Any]) -> str:
    category = record.get("category")
    if category == "non_equipment":
        return READINESS_DEFERRED
    return READINESS_NEEDS_REVIEW


def _slug(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")


def _count_by(records: list[AdapterRecord], field_name: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = getattr(record, field_name)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _format_counts(counts: dict[str, int]) -> list[str]:
    if not counts:
        return ["- none"]
    return [f"- {key}: {value}" for key, value in counts.items()]


def _format_list(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- {value}" for value in values[:20]]


def _format_bundle_unmapped(values: list[dict[str, Any]]) -> list[str]:
    if not values:
        return ["- none"]
    return [
        f"- {item['bundle_item_type_id']} (base_type_id={item['bundle_base_type_id']}, readiness={item['readiness']})"
        for item in values[:20]
    ]
