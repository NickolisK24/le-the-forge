"""Read-only diagnostics for bundle item_types/base_items migration planning."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import re
from pathlib import Path
from typing import Any

from app.game_data.bundle_compat import DEFAULT_BUNDLE_DIR, BUNDLE_DIR_ENV, resolve_bundle_dir


STATUS_PASS = "PASS"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"
MAX_EXAMPLES = 10

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent


@dataclass
class Finding:
    status: str
    message: str
    examples: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "examples": self.examples[:MAX_EXAMPLES],
        }


@dataclass
class ItemDiffResult:
    status: str = STATUS_PASS
    bundle_dir: str = ""
    bundle_item_types_count: int = 0
    bundle_base_items_count: int = 0
    forge_sources_inspected: list[str] = field(default_factory=list)
    comparison_methods: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    item_type_summary: dict[str, Any] = field(default_factory=dict)
    base_item_summary: dict[str, Any] = field(default_factory=dict)
    subtype_identity_risks: list[str] = field(default_factory=list)
    recommendation: str = (
        "Keep this diagnostic read-only. Add a developer diff adapter before migrating "
        "any production Forge item loaders."
    )

    def add(self, status: str, message: str, examples: list[Any] | None = None) -> None:
        self.findings.append(Finding(status, message, examples or []))
        if status == STATUS_FAIL:
            self.status = STATUS_FAIL
        elif status == STATUS_WARN and self.status != STATUS_FAIL:
            self.status = STATUS_WARN

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "bundle_dir": self.bundle_dir,
            "bundle_item_types_count": self.bundle_item_types_count,
            "bundle_base_items_count": self.bundle_base_items_count,
            "forge_sources_inspected": self.forge_sources_inspected,
            "comparison_methods": self.comparison_methods,
            "findings": [finding.to_dict() for finding in self.findings],
            "item_type_summary": self.item_type_summary,
            "base_item_summary": self.base_item_summary,
            "subtype_identity_risks": self.subtype_identity_risks,
            "recommendation": self.recommendation,
        }


def run_item_bundle_diff(bundle_dir: str | Path | None = None) -> ItemDiffResult:
    resolved_bundle_dir = resolve_bundle_dir(bundle_dir)
    result = ItemDiffResult(bundle_dir=str(resolved_bundle_dir))

    bundle = _load_bundle(resolved_bundle_dir, result)
    if bundle is None:
        return result

    forge = _load_forge_sources(result)
    _compare_item_types(bundle, forge, result)
    _compare_base_items(bundle, forge, result)
    _inspect_subtype_identity_risk(forge, result)
    return result


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_bundle(bundle_dir: Path, result: ItemDiffResult) -> dict[str, Any] | None:
    item_types_path = bundle_dir / "families" / "item_types.json"
    base_items_path = bundle_dir / "families" / "base_items.json"
    for path in (item_types_path, base_items_path):
        if not path.exists():
            result.add(STATUS_FAIL, f"Missing bundle family file: {path}")
            return None

    try:
        item_types = _read_json(item_types_path)
        base_items = _read_json(base_items_path)
        manifest = _read_json(bundle_dir / "manifest.json") if (bundle_dir / "manifest.json").exists() else None
        metadata = _read_json(bundle_dir / "metadata.json") if (bundle_dir / "metadata.json").exists() else None
    except json.JSONDecodeError as exc:
        result.add(STATUS_FAIL, f"Invalid JSON while loading bundle item families: {exc}")
        return None
    except OSError as exc:
        result.add(STATUS_FAIL, f"Could not read bundle item families: {exc}")
        return None

    if not isinstance(item_types, dict) or item_types.get("family") != "item_types":
        result.add(STATUS_FAIL, "families/item_types.json must be an object with family=item_types.")
        return None
    if not isinstance(base_items, dict) or base_items.get("family") != "base_items":
        result.add(STATUS_FAIL, "families/base_items.json must be an object with family=base_items.")
        return None

    item_type_records = item_types.get("records")
    base_item_records = base_items.get("records")
    if not isinstance(item_type_records, list):
        result.add(STATUS_FAIL, "families/item_types.json records must be a list.")
        return None
    if not isinstance(base_item_records, list):
        result.add(STATUS_FAIL, "families/base_items.json records must be a list.")
        return None

    result.bundle_item_types_count = len(item_type_records)
    result.bundle_base_items_count = len(base_item_records)
    _validate_bundle_ids(item_type_records, base_item_records, result)

    return {
        "item_types": item_type_records,
        "base_items": base_item_records,
        "manifest": manifest,
        "metadata": metadata,
    }


def _validate_bundle_ids(
    item_type_records: list[dict[str, Any]],
    base_item_records: list[dict[str, Any]],
    result: ItemDiffResult,
) -> None:
    item_type_ids = _duplicates([record.get("id") for record in item_type_records])
    if item_type_ids:
        result.add(STATUS_FAIL, "Duplicate bundle item_type IDs found.", item_type_ids)

    base_item_ids = _duplicates([record.get("id") for record in base_item_records])
    if base_item_ids:
        result.add(STATUS_FAIL, "Duplicate bundle base_item IDs found.", base_item_ids)

    composite_keys = [
        (record.get("base_type_id"), record.get("subtype_id"))
        for record in base_item_records
    ]
    duplicate_composites = _duplicates(composite_keys)
    if duplicate_composites:
        result.add(STATUS_FAIL, "Duplicate bundle base_type_id/subtype_id composite IDs found.", duplicate_composites)

    subtype_ids = [record.get("subtype_id") for record in base_item_records]
    repeated_subtypes = _duplicates(subtype_ids)
    if repeated_subtypes:
        result.add(
            STATUS_PASS,
            "Bundle subtype_id values repeat across base types as expected; composite identity is required.",
            repeated_subtypes[:MAX_EXAMPLES],
        )


def _load_forge_sources(result: ItemDiffResult) -> dict[str, Any]:
    sources: dict[str, Any] = {}

    item_types_path = REPO_ROOT / "data" / "items" / "item_types.json"
    base_items_path = REPO_ROOT / "data" / "items" / "base_items.json"
    if item_types_path.exists():
        sources["data_item_types"] = _safe_json(item_types_path, result)
    if base_items_path.exists():
        sources["data_base_items"] = _safe_json(base_items_path, result)

    result.forge_sources_inspected.extend(
        [
            "data/items/item_types.json",
            "data/items/base_items.json",
            "backend/app/constants/base_type_id_to_item_type_id.py",
            "backend/app/constants/item_type_ids.py",
            "backend/app/constants/item_type_to_slot.py",
            "backend/app/constants/sub_type_id_to_item_type_id.py",
            "backend/app/constants/game_type_to_item_type_id.py",
        ]
    )

    try:
        from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
        from app.constants.item_type_ids import ITEM_TYPE_IDS
        from app.constants.item_type_to_slot import ITEM_TYPE_TO_SLOT
        from app.constants.sub_type_id_to_item_type_id import SUBTYPE_ID_TO_ITEM_TYPE_ID
        from app.constants.game_type_to_item_type_id import GAME_TYPE_TO_ITEM_TYPE_ID

        sources["base_type_id_to_item_type_id"] = dict(BASE_TYPE_ID_TO_ITEM_TYPE_ID)
        sources["item_type_ids"] = list(ITEM_TYPE_IDS)
        sources["item_type_to_slot"] = dict(ITEM_TYPE_TO_SLOT)
        sources["subtype_id_to_item_type_id"] = dict(SUBTYPE_ID_TO_ITEM_TYPE_ID)
        sources["game_type_to_item_type_id"] = dict(GAME_TYPE_TO_ITEM_TYPE_ID)
    except Exception as exc:  # pragma: no cover - defensive diagnostic path
        result.add(STATUS_WARN, f"Could not import Forge item constants: {exc}")

    return sources


def _safe_json(path: Path, result: ItemDiffResult) -> Any | None:
    try:
        return _read_json(path)
    except Exception as exc:
        result.add(STATUS_WARN, f"Could not read Forge source {path}: {exc}")
        return None


def _compare_item_types(bundle: dict[str, Any], forge: dict[str, Any], result: ItemDiffResult) -> None:
    bundle_types = bundle["item_types"]
    forge_item_types = forge.get("data_item_types") or []
    forge_type_ids = set(forge.get("item_type_ids") or [])
    base_type_map = forge.get("base_type_id_to_item_type_id") or {}

    result.comparison_methods.append(
        "item_types: exact Forge static slug comparison plus base_type_id mapping when available."
    )

    bundle_ids = {record.get("id") for record in bundle_types}
    static_ids = {
        record.get("id")
        for record in forge_item_types
        if isinstance(record, dict)
    }
    mapped_bundle = {
        record.get("base_type_id"): base_type_map.get(record.get("base_type_id"))
        for record in bundle_types
    }
    comparable = {
        base_type_id: mapped
        for base_type_id, mapped in mapped_bundle.items()
        if mapped
    }
    unmapped = {
        record.get("base_type_id"): record.get("id")
        for record in bundle_types
        if record.get("base_type_id") not in comparable
    }

    static_missing_from_bundle = sorted(static_ids - bundle_ids - set(comparable.values()))
    bundle_not_in_static = sorted(
        record.get("id")
        for record in bundle_types
        if record.get("id") not in static_ids and comparable.get(record.get("base_type_id")) not in static_ids
    )

    if unmapped:
        result.add(
            STATUS_WARN,
            "Some bundle item_types have no Forge base_type_id mapping; these are likely non-equipment or unmigrated types.",
            [{"base_type_id": key, "bundle_id": value} for key, value in list(unmapped.items())[:MAX_EXAMPLES]],
        )
    if static_missing_from_bundle:
        result.add(
            STATUS_WARN,
            "Forge static item type IDs are not directly present in bundle IDs or base_type mappings.",
            static_missing_from_bundle,
        )
    if bundle_not_in_static:
        result.add(
            STATUS_WARN,
            "Bundle item type IDs do not directly match Forge static IDs; migration needs an adapter/diff map.",
            bundle_not_in_static[:MAX_EXAMPLES],
        )

    result.item_type_summary = {
        "bundle_count": len(bundle_types),
        "forge_data_item_types_count": len(forge_item_types) if isinstance(forge_item_types, list) else None,
        "forge_item_type_ids_count": len(forge_type_ids),
        "base_type_map_count": len(base_type_map),
        "base_type_mapped_bundle_count": len(comparable),
        "unmapped_bundle_base_type_count": len(unmapped),
        "static_missing_from_bundle_count": len(static_missing_from_bundle),
        "bundle_not_in_static_count": len(bundle_not_in_static),
    }


def _compare_base_items(bundle: dict[str, Any], forge: dict[str, Any], result: ItemDiffResult) -> None:
    bundle_base_items = bundle["base_items"]
    forge_base_items = forge.get("data_base_items") or {}
    result.comparison_methods.append(
        "base_items: name/type comparison only for current Forge data; base_type_id/subtype_id are not present in data/items/base_items.json."
    )

    bundle_names = {_norm_name(record.get("name")) for record in bundle_base_items if record.get("name")}
    forge_records = _flatten_forge_base_items(forge_base_items)
    forge_names = {_norm_name(record.get("name")) for record in forge_records if record.get("name")}

    bundle_missing_in_forge = sorted(bundle_names - forge_names)
    forge_missing_in_bundle = sorted(forge_names - bundle_names)
    duplicate_bundle_names = _duplicates([_norm_name(record.get("name")) for record in bundle_base_items if record.get("name")])
    duplicate_forge_names = _duplicates([_norm_name(record.get("name")) for record in forge_records if record.get("name")])

    if forge_records and not any("base_type_id" in record or "subtype_id" in record for record in forge_records):
        result.add(
            STATUS_WARN,
            "Current Forge base_items source lacks base_type_id/subtype_id; precise composite comparison is not possible.",
        )
    if bundle_missing_in_forge:
        result.add(
            STATUS_WARN,
            "Bundle has base item names not present in current Forge data. This is expected with the larger canonical source.",
            bundle_missing_in_forge[:MAX_EXAMPLES],
        )
    if forge_missing_in_bundle:
        result.add(
            STATUS_WARN,
            "Current Forge base item names are not present in the bundle by normalized name. Name-only matching is approximate.",
            forge_missing_in_bundle[:MAX_EXAMPLES],
        )
    if duplicate_bundle_names:
        result.add(STATUS_WARN, "Bundle has duplicate normalized base item names; IDs remain composite.", duplicate_bundle_names)
    if duplicate_forge_names:
        result.add(STATUS_WARN, "Current Forge data has duplicate normalized base item names.", duplicate_forge_names)

    result.base_item_summary = {
        "bundle_count": len(bundle_base_items),
        "forge_flat_count": len(forge_records),
        "name_overlap_count": len(bundle_names & forge_names),
        "bundle_missing_in_forge_count": len(bundle_missing_in_forge),
        "forge_missing_in_bundle_count": len(forge_missing_in_bundle),
        "duplicate_bundle_name_count": len(duplicate_bundle_names),
        "duplicate_forge_name_count": len(duplicate_forge_names),
        "precise_composite_comparison": False,
    }


def _inspect_subtype_identity_risk(forge: dict[str, Any], result: ItemDiffResult) -> None:
    subtype_map = forge.get("subtype_id_to_item_type_id") or {}
    if subtype_map:
        message = (
            "Forge has a non-empty subtype_id-only mapping. Since subtype_id is scoped by base_type_id, "
            "this is a migration risk unless every use also carries base_type_id context."
        )
        result.subtype_identity_risks.append(message)
        result.add(STATUS_WARN, message)
    else:
        result.add(
            STATUS_PASS,
            "Forge subtype_id-only constant map is empty; no active flat subtype identity table was detected.",
        )


def _flatten_forge_base_items(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for item_type, entries in value.items():
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict):
                        records.append({"item_type": item_type, **entry})
    elif isinstance(value, list):
        records = [entry for entry in value if isinstance(entry, dict)]
    return records


def _duplicates(values: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    duplicates: list[Any] = []
    for value in values:
        key = _hashable(value)
        if key in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(key)
    return duplicates


def _hashable(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((key, _hashable(val)) for key, val in value.items()))
    if isinstance(value, list):
        return tuple(_hashable(item) for item in value)
    return value


def _norm_name(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()

