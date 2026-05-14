"""Developer-only LE Tools import context diagnostics for bundle item type resolution."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
from app.game_data.bundle_item_type_dry_run_resolver import (
    BundleItemTypeDryRunResolver,
    STATUS_DEFERRED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
)


STATUS_KEYS = [
    STATUS_RESOLVED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_DEFERRED,
    STATUS_UNRESOLVED,
]

ITEM_TYPE_FIELDS = ("item_type", "itemType", "itemTypeId", "type")
BASE_TYPE_FIELDS = ("base_type_id", "baseTypeID", "baseTypeId", "baseType", "base_type")
SUBTYPE_FIELDS = ("subtype_id", "subTypeID", "subTypeId", "sub_type_id")
SLOT_FIELDS = ("slot", "slotName", "equipmentSlot")


@dataclass(frozen=True)
class LeToolsContextInput:
    slot: str | None
    forge_item_type: str | None
    base_type_id: int | None
    subtype_id: int | None
    source_index: int
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "slot": self.slot,
            "forge_item_type": self.forge_item_type,
            "base_type_id": self.base_type_id,
            "subtype_id": self.subtype_id,
            "source_index": self.source_index,
            "source": self.source,
        }


BUILT_IN_SAMPLE_ITEMS: list[dict[str, Any]] = [
    {"slot": "helmet", "item_type": "helm", "baseTypeID": 0, "name": "Resolved helm sample"},
    {"slot": "weapon", "item_type": "axe", "name": "Missing weapon context sample"},
    {"slot": "idol", "item_type": "idol_1x1", "name": "Missing idol context sample"},
    {"slot": "weapon", "item_type": "spear", "baseTypeID": 14, "name": "Review-only spear sample"},
    {"slot": "unknown", "item_type": "unknown_type", "name": "Unresolved item type sample"},
]


def build_le_tools_import_context_report(
    payload: Any | None = None,
    source: str = "sample",
    resolver: BundleItemTypeDryRunResolver | None = None,
) -> dict[str, Any]:
    """Build a read-only context report from LE Tools import-like item records."""

    resolver = resolver or BundleItemTypeDryRunResolver()
    records = extract_import_item_records(payload if payload is not None else BUILT_IN_SAMPLE_ITEMS)
    inputs = [_context_input_from_record(record, index, source) for index, record in enumerate(records)]
    items = []
    status_counts = {status: 0 for status in STATUS_KEYS}
    context_gaps: list[dict[str, Any]] = []

    for item in inputs:
        resolution = resolver.resolve(
            item.forge_item_type or "",
            base_type_id=item.base_type_id,
            subtype_id=item.subtype_id,
        )
        status_counts[resolution.status] = status_counts.get(resolution.status, 0) + 1
        warnings = list(resolution.warnings)
        notes = list(resolution.notes)

        if item.subtype_id is not None and item.base_type_id is None:
            warnings.append("subtype_id is present without base_type_id; this is not sufficient context.")
        if item.forge_item_type is None:
            warnings.append("No item_type-like field was found; name-only matching is not attempted.")
        if resolution.status in {STATUS_NEEDS_CONTEXT, STATUS_NEEDS_REVIEW, STATUS_UNRESOLVED}:
            context_gaps.append(
                {
                    "source_index": item.source_index,
                    "slot": item.slot,
                    "forge_item_type": item.forge_item_type,
                    "base_type_id": item.base_type_id,
                    "status": resolution.status,
                    "warnings": warnings,
                }
            )

        items.append(
            {
                "slot": item.slot,
                "forge_item_type": item.forge_item_type,
                "base_type_id": item.base_type_id,
                "subtype_id_present": item.subtype_id is not None,
                "resolver_status": resolution.status,
                "bundle_item_type_id": resolution.bundle_item_type_id,
                "production_safe": False,
                "warnings": warnings,
                "notes": notes,
            }
        )

    return {
        "production_safe": False,
        "source": source,
        "total_items": len(inputs),
        "status_counts": status_counts,
        "items": items,
        "context_gaps": context_gaps,
        "recommendations": _recommendations(status_counts, context_gaps),
    }


def load_payload(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extract_import_item_records(payload: Any) -> list[dict[str, Any]]:
    """Extract likely gear/item dictionaries without mutating the input payload."""

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    for key in ("gear", "equipment", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            return [item for item in value.values() if isinstance(item, dict)]

    build_data = payload.get("build_data")
    if isinstance(build_data, dict):
        records = extract_import_item_records(build_data)
        if records:
            return records

    return [payload] if _looks_like_item_record(payload) else []


def render_le_tools_import_context_report(report: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Import Context Dry-Run Report",
        "",
        "- production_safe: false",
        f"- source: {report['source']}",
        f"- total items: {report['total_items']}",
        "",
        "## Resolver Status Counts",
        "",
    ]
    for status, count in report["status_counts"].items():
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Items", ""])
    if not report["items"]:
        lines.append("- none")
    for item in report["items"]:
        lines.append(
            "- slot={slot} forge={forge} base_type_id={base} status={status} bundle={bundle}".format(
                slot=item["slot"] or "null",
                forge=item["forge_item_type"] or "null",
                base=item["base_type_id"] if item["base_type_id"] is not None else "null",
                status=item["resolver_status"],
                bundle=item["bundle_item_type_id"] or "null",
            )
        )
        for warning in item["warnings"]:
            lines.append(f"  - warning: {warning}")

    lines.extend(["", "## Context Gaps", ""])
    if not report["context_gaps"]:
        lines.append("- none")
    for gap in report["context_gaps"]:
        lines.append(
            f"- index={gap['source_index']} slot={gap['slot'] or 'null'} "
            f"forge={gap['forge_item_type'] or 'null'} status={gap['status']}"
        )

    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.append("")
    return "\n".join(lines)


def _context_input_from_record(record: dict[str, Any], index: int, source: str) -> LeToolsContextInput:
    base_type_id = _first_int(record, BASE_TYPE_FIELDS)
    subtype_id = _first_int(record, SUBTYPE_FIELDS)
    forge_item_type = _first_str(record, ITEM_TYPE_FIELDS)
    if forge_item_type is None and base_type_id is not None:
        forge_item_type = BASE_TYPE_ID_TO_ITEM_TYPE_ID.get(base_type_id)
    return LeToolsContextInput(
        slot=_first_str(record, SLOT_FIELDS),
        forge_item_type=_normalize_item_type(forge_item_type),
        base_type_id=base_type_id,
        subtype_id=subtype_id,
        source_index=index,
        source=source,
    )


def _looks_like_item_record(record: dict[str, Any]) -> bool:
    fields = set(record)
    return bool(fields.intersection(ITEM_TYPE_FIELDS + BASE_TYPE_FIELDS + SUBTYPE_FIELDS + SLOT_FIELDS))


def _first_int(record: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value)
    return None


def _first_str(record: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _normalize_item_type(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def _recommendations(status_counts: dict[str, int], context_gaps: list[dict[str, Any]]) -> list[str]:
    recommendations = [
        "Keep this report developer-only; it does not change LE Tools importer output.",
        "Keep production_safe=false until a separate migration defines consumer behavior.",
    ]
    if status_counts.get(STATUS_NEEDS_CONTEXT, 0):
        recommendations.append("Thread base_type_id into diagnostic inputs before resolving collapsed item type slugs.")
    if status_counts.get(STATUS_NEEDS_REVIEW, 0):
        recommendations.append("Review needs_review item types before adding translations.")
    if status_counts.get(STATUS_UNRESOLVED, 0):
        recommendations.append("Do not resolve unknown or name-only records by guessing.")
    if context_gaps:
        recommendations.append("Treat context gaps as warnings; do not silently fall back to slug/name matching.")
    return recommendations
