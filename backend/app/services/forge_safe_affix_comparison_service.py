"""Read-only legacy-vs-Forge-safe affix comparison diagnostics.

This module intentionally does not register Forge-safe data with production
registries or route planner, crafting, stat resolution, or simulation through
the bundle. It only compares immutable snapshots for migration planning.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from data.repositories.forge_safe_affix_bundle_repository import ForgeSafeAffixBundleRepository


DEFAULT_LIMIT = 50
MAX_LIMIT = 500


@dataclass(frozen=True)
class CompareOptions:
    include_details: bool = False
    limit: int = DEFAULT_LIMIT


def compare_legacy_to_forge_safe_bundle(
    bundle_path: str,
    *,
    options: CompareOptions | None = None,
) -> dict[str, Any]:
    """Compare legacy Forge affixes against a validated Forge-safe bundle."""

    opts = options or CompareOptions()
    limit = max(0, min(opts.limit, MAX_LIMIT))

    legacy_records = [_legacy_summary(record) for record in _load_legacy_affix_records()]
    bundle_repository = ForgeSafeAffixBundleRepository(bundle_path).load()
    bundle_records = [
        _bundle_summary(bundle_repository, record)
        for record in bundle_repository.list_affixes(limit=bundle_repository.count_affixes())
    ]

    legacy_by_id = _index_by_affix_id(legacy_records)
    bundle_by_id = _index_by_affix_id(bundle_records)
    legacy_ids = set(legacy_by_id)
    bundle_ids = set(bundle_by_id)
    matched_ids = sorted(legacy_ids & bundle_ids, key=_sort_key)

    missing_in_legacy = [bundle_by_id[affix_id] for affix_id in sorted(bundle_ids - legacy_ids, key=_sort_key)]
    missing_in_bundle = [legacy_by_id[affix_id] for affix_id in sorted(legacy_ids - bundle_ids, key=_sort_key)]

    differences = []
    difference_counts = {
        "slot": 0,
        "tier": 0,
        "stat_key": 0,
        "modifier_count": 0,
        "structure": 0,
        "safety": 0,
    }
    for affix_id in matched_ids:
        legacy = legacy_by_id[affix_id]
        bundle = bundle_by_id[affix_id]
        difference = _compare_record(affix_id, legacy, bundle)
        if not difference:
            continue
        for difference_type in difference["difference_types"]:
            difference_counts[difference_type] += 1
        differences.append(difference)

    summary = {
        "legacy_affix_count": len(legacy_records),
        "bundle_affix_count": len(bundle_records),
        "matched_count": len(matched_ids),
        "missing_in_legacy_count": len(missing_in_legacy),
        "missing_in_bundle_count": len(missing_in_bundle),
        "slot_difference_count": difference_counts["slot"],
        "tier_difference_count": difference_counts["tier"],
        "stat_key_difference_count": difference_counts["stat_key"],
        "modifier_count_difference_count": difference_counts["modifier_count"],
        "structural_difference_count": difference_counts["structure"],
        "safety_difference_count": difference_counts["safety"],
        "difference_count": len(differences),
    }

    return {
        "summary": summary,
        "missing_in_legacy": _bounded(missing_in_legacy, limit),
        "missing_in_bundle": _bounded(missing_in_bundle, limit),
        "differences": _bounded(differences, limit),
        "metadata": {
            "source": "legacy_vs_forge_safe_bundle",
            "legacy_source": "data/items/affixes.json with /api/ref/affixes craftable-type filtering",
            "bundle_source": str(bundle_path),
            "read_only": True,
            "experimental": True,
            "production_consumer": False,
            "production_safe": False,
            "match_strategy": "exact_affix_id",
            "match_strategy_notes": [
                "Legacy affixes expose numeric affix_id.",
                "Forge-safe bundle affixes expose numeric affix_id from source provenance.",
                "No fuzzy matching is performed.",
            ],
            "include_details": opts.include_details,
            "limit": limit,
            "truncated": {
                "missing_in_legacy": len(missing_in_legacy) > limit,
                "missing_in_bundle": len(missing_in_bundle) > limit,
                "differences": len(differences) > limit,
            },
            "comparison_categories": [
                "identity",
                "slot_item_applicability",
                "tier_value_structure",
                "modifier_stat_routing",
                "safety_provenance",
            ],
        },
    }


def _legacy_summary(record: dict[str, Any]) -> dict[str, Any]:
    tiers = [_legacy_tier_summary(tier) for tier in record.get("tiers") or []]
    return {
        "affix_id": record.get("affix_id"),
        "id": record.get("id"),
        "name": record.get("name"),
        "display_name": record.get("name"),
        "source_type": record.get("rolls_on"),
        "type": record.get("type"),
        "slots": _normalize_string_list(record.get("applicable_to")),
        "class_requirement": record.get("class_requirement"),
        "tags": _normalize_string_list(record.get("tags")),
        "tier_count": len(tiers),
        "tiers": tiers,
        "tier_numbers": [tier["tier"] for tier in tiers],
        "has_malformed_tiers": any(tier["malformed"] for tier in tiers),
        "stat_keys": _normalize_string_list([record.get("stat_key")]),
        "modifier_type": record.get("modifier_type"),
        "modifier_count": 1 if record.get("stat_key") else 0,
        "safety": {
            "forge_safe": None,
            "production_safe": None,
            "source": "legacy",
        },
        "provenance": {
            "source_path": "data/items/affixes.json",
        },
    }


def _load_legacy_affix_records() -> list[dict[str, Any]]:
    """Load the same legacy JSON source used by /api/ref/affixes.

    The production endpoint transforms records and omits raw numeric affix_id.
    The diagnostic keeps that raw field for exact identity matching while
    preserving the endpoint's craftable-type filter and type normalization.
    """

    affixes_path = Path(__file__).resolve().parents[3] / "data" / "items" / "affixes.json"
    raw_records = json.loads(affixes_path.read_text(encoding="utf-8"))
    type_normalize = {"experimental": "prefix", "personal": "prefix"}
    records = []
    for record in raw_records:
        raw_type = record.get("type", "")
        if raw_type not in ("prefix", "suffix", "experimental", "personal"):
            continue
        normalized = dict(record)
        normalized["type"] = type_normalize.get(raw_type, raw_type)
        tags = list(normalized.get("tags", []))
        if raw_type in type_normalize and raw_type not in tags:
            tags.append(raw_type)
        normalized["tags"] = tags
        records.append(normalized)
    return records


def _bundle_summary(
    repository: ForgeSafeAffixBundleRepository,
    record: dict[str, Any],
) -> dict[str, Any]:
    source_identity = _source_affix_identity(record)
    modifiers = repository.get_modifiers_for_affix(source_identity)
    modifier_keys = sorted({
        value
        for modifier in modifiers
        for value in _modifier_key_candidates(modifier)
        if value
    })
    tiers = [_bundle_tier_summary(tier) for tier in record.get("tier_data") or []]
    safety = record.get("safety") if isinstance(record.get("safety"), dict) else {}
    return {
        "affix_id": record.get("affix_id"),
        "id": source_identity,
        "name": record.get("affix_name"),
        "display_name": record.get("display_name") or record.get("affix_name"),
        "source_type": record.get("source_type"),
        "type": _bundle_affix_type(record),
        "slots": _normalize_string_list(record.get("eligible_item_types")),
        "class_requirement": None,
        "tags": _normalize_string_list(record.get("tags")),
        "tier_count": len(tiers),
        "tiers": tiers,
        "tier_numbers": [tier["tier"] for tier in tiers],
        "has_malformed_tiers": any(tier["malformed"] for tier in tiers),
        "stat_keys": modifier_keys,
        "modifier_ids": sorted(str(modifier.get("modifier_id")) for modifier in modifiers),
        "modifier_count": len(modifiers),
        "modifier_references": record.get("modifier_references") or [],
        "safety": {
            "forge_safe": safety.get("forge_safe"),
            "production_safe": safety.get("production_safe"),
            "export_policy": safety.get("export_policy"),
        },
        "provenance": record.get("provenance") if isinstance(record.get("provenance"), dict) else {},
    }


def _compare_record(affix_id: str, legacy: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any] | None:
    difference_types = []
    notes = []

    if _casefold(legacy.get("name")) != _casefold(bundle.get("name")):
        difference_types.append("structure")
        notes.append("Affix names differ for the same affix_id.")

    if _normalize_for_compare(legacy["source_type"]) != _normalize_for_compare(bundle["source_type"]):
        difference_types.append("structure")
        notes.append("Source/category differs.")

    if legacy["slots"] != bundle["slots"]:
        difference_types.append("slot")
        notes.append("Legacy and bundle item applicability use different slot vocabularies or values.")

    if legacy["tier_numbers"] != bundle["tier_numbers"] or legacy["has_malformed_tiers"] != bundle["has_malformed_tiers"]:
        difference_types.append("tier")
        notes.append("Tier count, tier numbers, or malformed tier signal differs.")
    elif legacy["tiers"] != bundle["tiers"]:
        difference_types.append("tier")
        notes.append("Tier min/max values differ. This is expected until value-scale policy is explicitly validated.")

    if legacy["stat_keys"] != bundle["stat_keys"]:
        difference_types.append("stat_key")
        notes.append("Legacy stat_key namespace differs from bundle modifier property/modifier namespace.")

    if legacy["modifier_count"] != bundle["modifier_count"]:
        difference_types.append("modifier_count")
        notes.append("Legacy single stat_key count differs from Forge-safe modifier count.")

    if bundle["safety"].get("forge_safe") is not True or bundle["safety"].get("production_safe") is not False:
        difference_types.append("safety")
        notes.append("Bundle safety flags are not in the expected forge_safe=true, production_safe=false state.")

    if not difference_types:
        return None

    compact = {
        "affix_id": affix_id,
        "legacy": _compact_record(legacy),
        "bundle": _compact_record(bundle),
        "difference_types": difference_types,
        "migration_risk": _migration_risk(difference_types),
        "notes": notes,
    }
    return compact


def _compact_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_id": record.get("affix_id"),
        "id": record.get("id"),
        "name": record.get("name"),
        "source_type": record.get("source_type"),
        "type": record.get("type"),
        "slots": record.get("slots"),
        "class_requirement": record.get("class_requirement"),
        "tier_count": record.get("tier_count"),
        "tier_numbers": record.get("tier_numbers"),
        "has_malformed_tiers": record.get("has_malformed_tiers"),
        "stat_keys": record.get("stat_keys"),
        "modifier_ids": record.get("modifier_ids", []),
        "modifier_count": record.get("modifier_count"),
        "safety": record.get("safety"),
        "provenance": record.get("provenance"),
    }


def _legacy_tier_summary(tier: dict[str, Any]) -> dict[str, Any]:
    minimum = tier.get("min")
    maximum = tier.get("max")
    return {
        "tier": tier.get("tier"),
        "min": minimum,
        "max": maximum,
        "malformed": _is_malformed_range(minimum, maximum),
    }


def _bundle_tier_summary(tier: dict[str, Any]) -> dict[str, Any]:
    minimum = tier.get("minRoll")
    maximum = tier.get("maxRoll")
    return {
        "tier": tier.get("tier"),
        "min": minimum,
        "max": maximum,
        "malformed": _is_malformed_range(minimum, maximum),
    }


def _modifier_key_candidates(modifier: dict[str, Any]) -> list[str]:
    values = []
    for key in ("property", "modifier_type", "modifier_id"):
        if modifier.get(key):
            values.append(str(modifier[key]))
    for reference in modifier.get("modifier_references") or []:
        if not isinstance(reference, dict):
            continue
        property_name = reference.get("property")
        modifier_type = reference.get("modifierType")
        tags = reference.get("tags") or []
        parts = [str(value) for value in [modifier_type, property_name, *tags] if value]
        if parts:
            values.append(":".join(parts))
    return values


def _bundle_affix_type(record: dict[str, Any]) -> str | None:
    categories = _normalize_string_list(record.get("categories"))
    if "PREFIX" in categories:
        return "prefix"
    if "SUFFIX" in categories:
        return "suffix"
    return None


def _index_by_affix_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed = {}
    for record in records:
        affix_id = record.get("affix_id")
        if affix_id is None or affix_id == "":
            continue
        indexed[str(affix_id)] = record
    return indexed


def _bounded(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return records[:limit]


def _migration_risk(difference_types: list[str]) -> str:
    high_risk = {"stat_key", "modifier_count", "tier", "safety"}
    if any(value in high_risk for value in difference_types):
        return "high"
    if "slot" in difference_types:
        return "medium"
    return "low"


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    return sorted(str(item) for item in value if item not in (None, ""))


def _normalize_for_compare(value: Any) -> str:
    return str(value or "").strip().lower()


def _casefold(value: Any) -> str:
    return str(value or "").casefold()


def _is_malformed_range(minimum: Any, maximum: Any) -> bool:
    try:
        return float(minimum) > float(maximum)
    except (TypeError, ValueError):
        return False


def _source_affix_identity(record: dict[str, Any]) -> str:
    provenance = record.get("provenance")
    if isinstance(provenance, dict) and provenance.get("source_affix_identity"):
        return str(provenance["source_affix_identity"])
    return ""


def _sort_key(value: str) -> tuple[int, Any]:
    try:
        return (0, int(value))
    except ValueError:
        return (1, value)
