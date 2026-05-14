"""Developer-only validation for reviewed bundle item type mapping fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_CATEGORIES = ("accepted", "needs_adapter", "needs_review", "deferred", "unsafe")
REQUIRED_ENTRY_FIELDS = (
    "forge_item_type",
    "forge_slot",
    "bundle_item_type_id",
    "bundle_base_type_id",
    "match_method",
    "confidence",
    "production_safe",
    "reason",
    "notes",
)


def load_mapping_review_fixture(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_mapping_review_fixture(fixture: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if fixture.get("fixture") != "bundle_item_type_mapping_review":
        errors.append("fixture must be bundle_item_type_mapping_review.")
    if fixture.get("production_safe") is not False:
        errors.append("fixture production_safe must be false.")

    categories = fixture.get("categories")
    if not isinstance(categories, dict):
        return ["categories must be an object."], warnings

    for category in REQUIRED_CATEGORIES:
        if category not in categories:
            errors.append(f"Missing category: {category}")
        elif not isinstance(categories[category], list):
            errors.append(f"Category must be a list: {category}")

    for category, entries in categories.items():
        if category not in REQUIRED_CATEGORIES or not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            location = f"{category}[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{location} must be an object.")
                continue
            for field in REQUIRED_ENTRY_FIELDS:
                if field not in entry:
                    errors.append(f"{location} missing field: {field}")
            if entry.get("production_safe") is not False:
                errors.append(f"{location} production_safe must be false.")
            if entry.get("match_method") == "subtype_id":
                errors.append(f"{location} must not use subtype_id-only matching.")
            if not isinstance(entry.get("notes"), list):
                errors.append(f"{location} notes must be a list.")

            if category == "accepted":
                if entry.get("match_method") != "base_type_id":
                    errors.append(f"{location} accepted mappings must be base_type_id-backed.")
                if entry.get("forge_item_type") != entry.get("bundle_item_type_id"):
                    errors.append(f"{location} accepted mappings must not require slug translation.")
            if category == "needs_adapter" and entry.get("match_method") != "base_type_id":
                errors.append(f"{location} needs_adapter mappings should be ID-backed adapter decisions.")
            if category == "needs_review" and entry.get("match_method") in {"normalized_name", "exact_slug"}:
                warnings.append(f"{location} is advisory and must stay out of accepted until reviewed.")

    accepted_forge_types = {
        entry.get("forge_item_type")
        for entry in categories.get("accepted", [])
        if isinstance(entry, dict)
    }
    if "spear" in accepted_forge_types:
        errors.append("spear must not be accepted without a proven bundle mapping.")

    return errors, warnings
