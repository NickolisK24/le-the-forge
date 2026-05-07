"""Developer-only LE Tools import context sidecar builder."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.game_data.bundle_item_type_dry_run_resolver import (
    BundleItemTypeDryRunResolver,
    STATUS_DEFERRED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
)
from app.game_data.le_tools_import_stage_context_report import (
    DEFAULT_STAGE_FIXTURE,
    load_stage_fixture,
)
from app.routes.import_route import _map_let_build


STATUS_KEYS = [
    STATUS_RESOLVED,
    STATUS_NEEDS_CONTEXT,
    STATUS_NEEDS_REVIEW,
    STATUS_DEFERRED,
    STATUS_UNRESOLVED,
]
ITEM_TYPE_KEYS = ("item_type", "itemType", "itemTypeId", "type")
BASE_TYPE_KEYS = ("baseTypeID", "baseTypeId", "base_type_id", "baseType", "id")
SUBTYPE_KEYS = ("subTypeID", "subTypeId", "subtype_id", "sub_type_id")
SOURCE_ITEM_ID_KEYS = ("id", "source_item_id", "itemId", "item_id")


def build_sidecar_from_fixture(
    fixture_path: str | Path = DEFAULT_STAGE_FIXTURE,
    resolver: BundleItemTypeDryRunResolver | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Build a sidecar from the offline stage fixture and return copied mapped gear."""

    fixture = load_stage_fixture(fixture_path)
    return build_sidecar_from_build_info(fixture["build_info"], fixture=fixture, resolver=resolver)


def build_sidecar_from_build_info(
    build_info: dict[str, Any],
    fixture: dict[str, Any] | None = None,
    resolver: BundleItemTypeDryRunResolver | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run the existing mapper, copy output, and build a diagnostic-only sidecar."""

    resolver = resolver or BundleItemTypeDryRunResolver()
    build_info_copy = deepcopy(build_info)
    mapped = _map_let_build(build_info_copy)
    mapped_gear = deepcopy(mapped.get("gear") or [])
    raw_records = _raw_equipment_records(build_info)
    sidecar = build_sidecar_from_records(
        raw_records=raw_records,
        mapped_gear=mapped_gear,
        resolver=resolver,
        fixture=fixture,
    )
    return sidecar, mapped_gear


def build_sidecar_from_records(
    raw_records: list[dict[str, Any]],
    mapped_gear: list[dict[str, Any]],
    resolver: BundleItemTypeDryRunResolver | None = None,
    fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a sidecar from raw/source records and copied mapped gear records."""

    resolver = resolver or BundleItemTypeDryRunResolver()
    items: list[dict[str, Any]] = []
    for index, raw_record in enumerate(deepcopy(raw_records)):
        mapped_record = deepcopy(mapped_gear[index]) if index < len(mapped_gear) else {}
        items.append(_build_item(index, raw_record, mapped_record, resolver))

    sidecar = {
        "production_safe": False,
        "source": "le_tools_import_diagnostic",
        "importer": "lastepochtools",
        "build_id": _fixture_build_id(fixture),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "items": items,
        "summary": _summary(items),
    }
    errors = validate_sidecar(sidecar)
    if errors:
        raise ValueError("; ".join(errors))
    return sidecar


def validate_sidecar(sidecar: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if sidecar.get("production_safe") is not False:
        errors.append("top-level production_safe must be false")
    items = sidecar.get("items")
    if not isinstance(items, list):
        return errors + ["items must be a list"]

    for item in items:
        index = item.get("index")
        if not isinstance(index, int):
            errors.append("every item must have integer index")
        if "slot" not in item:
            errors.append(f"item {index} missing slot")
        resolver = item.get("resolver") or {}
        context = item.get("context") or {}
        raw = item.get("raw") or {}
        mapped = item.get("mapped") or {}
        if resolver.get("production_safe") is not False:
            errors.append(f"item {index} resolver.production_safe must be false")
        for label, value in (
            ("raw.base_type_id", raw.get("base_type_id")),
            ("raw.subtype_id", raw.get("subtype_id")),
            ("mapped.base_type_id", mapped.get("base_type_id")),
            ("mapped.subtype_id", mapped.get("subtype_id")),
        ):
            if value is not None and not isinstance(value, int):
                errors.append(f"item {index} {label} must be number/null")
        if context.get("subtype_only") and resolver.get("status") == STATUS_RESOLVED:
            errors.append(f"item {index} subtype_only record resolved")
        if not context.get("has_raw_item_type_signal") and resolver.get("status") == STATUS_RESOLVED:
            errors.append(f"item {index} name-only record resolved")
        if raw.get("item_type") == "spear" and resolver.get("status") == STATUS_RESOLVED:
            errors.append(f"item {index} spear resolved")
        if (
            raw.get("item_type") in {"axe", "mace", "sword", "idol_1x1"}
            and raw.get("base_type_id") is None
            and mapped.get("base_type_id") is None
            and resolver.get("status") != STATUS_NEEDS_CONTEXT
        ):
            errors.append(f"item {index} collapsed slug missing base_type_id must need context")

    expected = _summary(items)
    actual = sidecar.get("summary") or {}
    for key, value in expected.items():
        if actual.get(key) != value:
            errors.append(f"summary {key}={actual.get(key)} does not match expected {value}")
    return errors


def render_sidecar_report(sidecar: dict[str, Any]) -> str:
    lines = [
        "# LE Tools Import Context Sidecar Report",
        "",
        "- production_safe: false",
        f"- source: {sidecar['source']}",
        f"- importer: {sidecar['importer']}",
        f"- build_id: {sidecar['build_id'] or 'null'}",
        f"- generated_at: {sidecar['generated_at']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in sidecar["summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Items", ""])
    for item in sidecar["items"]:
        lines.append(
            "- index={index} slot={slot} raw_type={raw_type} raw_base={raw_base} "
            "mapped_base={mapped_base} status={status} bundle={bundle}".format(
                index=item["index"],
                slot=item["slot"] or "null",
                raw_type=item["raw"]["item_type"] or "null",
                raw_base=item["raw"]["base_type_id"],
                mapped_base=item["mapped"]["base_type_id"],
                status=item["resolver"]["status"],
                bundle=item["resolver"]["bundle_item_type_id"] or "null",
            )
        )
        for warning in item["resolver"]["warnings"]:
            lines.append(f"  - warning: {warning}")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Sidecar is developer-only and production_safe remains false.",
            "- Production importer output is copied for diagnostics and not mutated.",
            "- subtype_id alone and name-only records do not resolve.",
            "- Missing base_type_id for collapsed item type slugs remains needs_context.",
            "",
            "## What This Proves",
            "",
            "- Raw and mapped import context can be preserved in one diagnostic object.",
            "- The existing importer path preserves mapped base_type_id for ID-backed records.",
            "- Resolver decisions can be attached without changing importer output.",
            "",
            "## What Remains Unresolved",
            "",
            "- Fixture is synthetic/offline and not a live LET capture.",
            "- Mapped production output still does not expose item_type context.",
            "- No production or non-production consumer is activated by this report.",
            "",
        ]
    )
    return "\n".join(lines)


def sidecar_to_json(sidecar: dict[str, Any]) -> str:
    return json.dumps(sidecar, indent=2, sort_keys=True)


def _build_item(
    index: int,
    raw_record: dict[str, Any],
    mapped_record: dict[str, Any],
    resolver: BundleItemTypeDryRunResolver,
) -> dict[str, Any]:
    raw_item_type = _normalize_item_type(_first_str(raw_record, ITEM_TYPE_KEYS))
    raw_base_type_id = _first_int(raw_record, BASE_TYPE_KEYS)
    raw_subtype_id = _first_int(raw_record, SUBTYPE_KEYS)
    mapped_base_type_id = _first_int(mapped_record, ("base_type_id", "baseTypeID"))
    mapped_subtype_id = _first_int(mapped_record, ("subtype_id", "subTypeID"))
    resolution = resolver.resolve(
        raw_item_type or "",
        base_type_id=mapped_base_type_id,
        subtype_id=raw_subtype_id or mapped_subtype_id,
    )
    has_raw_item_type = raw_item_type is not None
    has_base_type_id = raw_base_type_id is not None or mapped_base_type_id is not None
    has_subtype_id = raw_subtype_id is not None or mapped_subtype_id is not None
    mapped_has_item_type = any(key in mapped_record for key in ITEM_TYPE_KEYS)

    return {
        "index": index,
        "slot": mapped_record.get("slot") or raw_record.get("slot"),
        "raw": {
            "item_type": raw_item_type,
            "base_type_id": raw_base_type_id,
            "subtype_id": raw_subtype_id,
            "name": raw_record.get("name"),
            "source_item_id": _first_value(raw_record, SOURCE_ITEM_ID_KEYS),
        },
        "mapped": {
            "slot": mapped_record.get("slot"),
            "base_type_id": mapped_base_type_id,
            "subtype_id": mapped_subtype_id,
            "has_item_type": mapped_has_item_type,
            "mapped_item_id": mapped_record.get("item_id") or mapped_record.get("id"),
            "mapped_name": mapped_record.get("item_name") or mapped_record.get("name"),
        },
        "resolver": {
            "status": resolution.status,
            "bundle_item_type_id": resolution.bundle_item_type_id,
            "match_source": resolution.match_source,
            "production_safe": False,
            "warnings": resolution.warnings,
            "notes": resolution.notes,
        },
        "context": {
            "has_base_type_id": has_base_type_id,
            "has_subtype_id": has_subtype_id,
            "subtype_only": has_subtype_id and not has_base_type_id,
            "has_raw_item_type_signal": has_raw_item_type,
            "requires_test_pairing": has_raw_item_type and not mapped_has_item_type,
        },
    }


def _raw_equipment_records(build_info: dict[str, Any]) -> list[dict[str, Any]]:
    raw = build_info.get("equipment") or build_info.get("gear") or build_info.get("items") or []
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        return [item for item in raw.values() if isinstance(item, dict)]
    return []


def _summary(items: list[dict[str, Any]]) -> dict[str, int]:
    status_counts = {status: 0 for status in STATUS_KEYS}
    for item in items:
        status = item["resolver"]["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "total_items": len(items),
        STATUS_RESOLVED: status_counts[STATUS_RESOLVED],
        STATUS_NEEDS_CONTEXT: status_counts[STATUS_NEEDS_CONTEXT],
        STATUS_NEEDS_REVIEW: status_counts[STATUS_NEEDS_REVIEW],
        STATUS_DEFERRED: status_counts[STATUS_DEFERRED],
        STATUS_UNRESOLVED: status_counts[STATUS_UNRESOLVED],
        "raw_with_base_type_id": sum(1 for item in items if item["raw"]["base_type_id"] is not None),
        "mapped_with_base_type_id": sum(1 for item in items if item["mapped"]["base_type_id"] is not None),
        "mapped_missing_item_type": sum(1 for item in items if not item["mapped"]["has_item_type"]),
        "requires_test_pairing": sum(1 for item in items if item["context"]["requires_test_pairing"]),
        "raw_with_subtype_only": sum(
            1
            for item in items
            if item["raw"]["subtype_id"] is not None and item["raw"]["base_type_id"] is None
        ),
    }


def _fixture_build_id(fixture: dict[str, Any] | None) -> str | None:
    if not fixture:
        return None
    value = fixture.get("fixture")
    return str(value) if value else None


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


def _first_value(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in record:
            return record.get(key)
    return None


def _normalize_item_type(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().lower().replace(" ", "_").replace("-", "_")
