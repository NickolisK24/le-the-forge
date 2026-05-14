"""Developer-only raw vs mapped LE Tools import context diagnostics."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from app.game_data.le_tools_import_context_report import (
    build_le_tools_import_context_report,
)
from app.routes.import_route import _map_let_build


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STAGE_FIXTURE = (
    BACKEND_ROOT / "tests" / "fixtures" / "le_tools_offline_buildinfo_stage_context_sample.json"
)
BASE_TYPE_KEYS = ("baseTypeID", "baseTypeId", "base_type_id", "baseType", "id")
SUBTYPE_KEYS = ("subTypeID", "subTypeId", "subtype_id", "sub_type_id")
ITEM_TYPE_KEYS = ("item_type", "itemType", "itemTypeId", "type")


def load_stage_fixture(path: str | Path = DEFAULT_STAGE_FIXTURE) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("build_info"), dict):
        raise ValueError("Stage fixture must be an object with build_info object.")
    return data


def build_stage_context_report(
    fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fixture = fixture or load_stage_fixture()
    build_info = deepcopy(fixture["build_info"])
    raw_records = _raw_equipment_records(build_info)
    mapped = _map_let_build(deepcopy(build_info))
    mapped_gear = mapped.get("gear") or []
    diagnostic_input = _diagnostic_input(raw_records, mapped_gear)
    resolver_report = build_le_tools_import_context_report(
        diagnostic_input,
        source="stage_context_mapped_copy",
    )
    records = [
        _record_report(index, raw, mapped_gear[index] if index < len(mapped_gear) else {}, resolver_item)
        for index, (raw, resolver_item) in enumerate(zip(raw_records, resolver_report["items"]))
    ]
    return {
        "production_safe": False,
        "fixture": fixture.get("fixture"),
        "fixture_source": fixture.get("source"),
        "importer_accepted_fixture": isinstance(mapped, dict),
        "mapped_output_shape_changed": False,
        "test_only_pairing_used": True,
        "total_items": len(records),
        "stage_summary": _stage_summary(records),
        "resolver_status_counts": resolver_report["status_counts"],
        "records": records,
        "recommendations": _recommendations(records),
    }


def render_stage_context_report(report: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Import Stage Context Report",
        "",
        "- production_safe: false",
        f"- fixture: `{report['fixture']}`",
        f"- fixture source: {report['fixture_source']}",
        f"- importer accepted fixture directly: {str(report['importer_accepted_fixture']).lower()}",
        f"- test-only pairing used: {str(report['test_only_pairing_used']).lower()}",
        f"- total items: {report['total_items']}",
        "",
        "## Stage Summary",
        "",
    ]
    for key, value in report["stage_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Resolver Status Counts", ""])
    for key, value in report["resolver_status_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Records", ""])
    for record in report["records"]:
        lines.append(
            "- index={index} slot={slot} raw_base={raw_base} mapped_base={mapped_base} "
            "mapped_item_type={mapped_item_type} status={status} bundle={bundle}".format(
                index=record["index"],
                slot=record["slot"] or "null",
                raw_base=record["raw_base_type_id"],
                mapped_base=record["mapped_base_type_id"],
                mapped_item_type=str(record["mapped_has_item_type"]).lower(),
                status=record["resolver_status"],
                bundle=record["bundle_item_type_id"] or "null",
            )
        )
        for warning in record["warnings"]:
            lines.append(f"  - warning: {warning}")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.append("")
    return "\n".join(lines)


def _raw_equipment_records(build_info: dict[str, Any]) -> list[dict[str, Any]]:
    raw = build_info.get("equipment") or build_info.get("gear") or build_info.get("items") or []
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        return [item for item in raw.values() if isinstance(item, dict)]
    return []


def _diagnostic_input(raw_records: list[dict[str, Any]], mapped_gear: list[dict[str, Any]]) -> list[dict[str, Any]]:
    copied = []
    for index, raw in enumerate(raw_records):
        mapped = deepcopy(mapped_gear[index]) if index < len(mapped_gear) else {}
        copied.append(
            {
                "slot": mapped.get("slot") or raw.get("slot"),
                "item_type": _first_str(raw, ITEM_TYPE_KEYS),
                "base_type_id": mapped.get("base_type_id"),
                "subtype_id": _first_int(raw, SUBTYPE_KEYS),
                "name": mapped.get("item_name") or raw.get("name"),
            }
        )
    return copied


def _record_report(
    index: int,
    raw: dict[str, Any],
    mapped: dict[str, Any],
    resolver_item: dict[str, Any],
) -> dict[str, Any]:
    raw_base_type_id = _first_int(raw, BASE_TYPE_KEYS)
    mapped_base_type_id = mapped.get("base_type_id")
    raw_item_type = _first_str(raw, ITEM_TYPE_KEYS)
    mapped_has_item_type = any(key in mapped for key in ITEM_TYPE_KEYS)
    return {
        "index": index,
        "slot": mapped.get("slot") or raw.get("slot"),
        "raw_item_type": raw_item_type,
        "raw_has_base_type_id": raw_base_type_id is not None,
        "raw_base_type_id": raw_base_type_id,
        "raw_has_subtype_id": _first_int(raw, SUBTYPE_KEYS) is not None,
        "mapped_has_base_type_id": mapped_base_type_id is not None,
        "mapped_base_type_id": mapped_base_type_id,
        "mapped_has_item_type": mapped_has_item_type,
        "test_pairing_needed": bool(raw_item_type and not mapped_has_item_type),
        "resolver_status": resolver_item["resolver_status"],
        "bundle_item_type_id": resolver_item["bundle_item_type_id"],
        "production_safe": False,
        "warnings": resolver_item["warnings"],
        "notes": _record_notes(raw, mapped, resolver_item),
    }


def _stage_summary(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "raw_with_base_type_id": sum(1 for record in records if record["raw_has_base_type_id"]),
        "mapped_with_base_type_id": sum(1 for record in records if record["mapped_has_base_type_id"]),
        "raw_missing_base_type_id": sum(1 for record in records if not record["raw_has_base_type_id"]),
        "mapped_missing_item_type": sum(1 for record in records if not record["mapped_has_item_type"]),
        "needs_test_only_pairing": sum(1 for record in records if record["test_pairing_needed"]),
        "raw_with_subtype_only": sum(
            1
            for record in records
            if record["raw_has_subtype_id"] and not record["raw_has_base_type_id"]
        ),
    }


def _recommendations(records: list[dict[str, Any]]) -> list[str]:
    recommendations = [
        "Keep this comparison developer-only; production importer output is unchanged.",
        "Thread base_type_id and reviewed item type context explicitly before any non-production consumer uses bundle IDs.",
        "Do not use subtype_id alone or name-only matching for canonical item type resolution.",
    ]
    if any(record["test_pairing_needed"] for record in records):
        recommendations.append("Mapped output preserving base_type_id is useful, but item_type context still needs an explicit diagnostic source.")
    if any(record["resolver_status"] == "needs_context" for record in records):
        recommendations.append("Records missing baseTypeID must remain needs_context.")
    if any(record["resolver_status"] == "needs_review" for record in records):
        recommendations.append("Review spear or other blocked aliases before adding translations.")
    return recommendations


def _record_notes(raw: dict[str, Any], mapped: dict[str, Any], resolver_item: dict[str, Any]) -> list[str]:
    notes = []
    if _first_str(raw, ITEM_TYPE_KEYS) and not any(key in mapped for key in ITEM_TYPE_KEYS):
        notes.append("Raw item_type is available only through test-only pairing; mapped output does not expose it.")
    if _first_int(raw, SUBTYPE_KEYS) is not None and _first_int(raw, BASE_TYPE_KEYS) is None:
        notes.append("Raw subtype_id is present without baseTypeID and is not sufficient context.")
    if resolver_item["resolver_status"] == "resolved":
        notes.append("Resolved through developer-only dry-run resolver.")
    return notes


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
