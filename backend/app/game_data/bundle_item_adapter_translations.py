"""Developer-only validation for bundle item type adapter translation fixtures."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_FIELDS = (
    "fixture",
    "purpose",
    "production_safe",
    "source_review",
    "source_fixture",
    "bundle_id",
    "rules",
    "translations",
)

REQUIRED_TRANSLATION_FIELDS = (
    "forge_item_type",
    "forge_slot",
    "bundle_item_type_id",
    "bundle_base_type_id",
    "translation_type",
    "required_context",
    "confidence",
    "production_safe",
    "source",
    "reason",
    "notes",
)

NAME_ONLY_SOURCES = {"name", "normalized_name", "exact_slug", "name_only"}


def load_adapter_translations_fixture(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_adapter_translations(path: str | Path) -> list[dict[str, Any]]:
    fixture = load_adapter_translations_fixture(path)
    errors, _warnings = validate_adapter_translations_fixture(fixture)
    if errors:
        raise ValueError("; ".join(errors))
    return deepcopy(fixture["translations"])


def validate_adapter_translations_fixture(fixture: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in fixture:
            errors.append(f"Missing top-level field: {field}")
    if fixture.get("fixture") != "bundle_item_type_adapter_translations":
        errors.append("fixture must be bundle_item_type_adapter_translations.")
    if fixture.get("production_safe") is not False:
        errors.append("fixture production_safe must be false.")
    if not isinstance(fixture.get("rules"), list):
        errors.append("rules must be a list.")

    translations = fixture.get("translations")
    if not isinstance(translations, list):
        errors.append("translations must be a list.")
        return errors, warnings

    seen: dict[tuple[str, int], str] = {}
    for index, translation in enumerate(translations):
        location = f"translations[{index}]"
        if not isinstance(translation, dict):
            errors.append(f"{location} must be an object.")
            continue
        for field in REQUIRED_TRANSLATION_FIELDS:
            if field not in translation:
                errors.append(f"{location} missing field: {field}")

        required_context = translation.get("required_context")
        if not isinstance(required_context, list):
            errors.append(f"{location} required_context must be a list.")
            required_context = []
        if "base_type_id" not in required_context:
            errors.append(f"{location} must require base_type_id context.")
        if required_context == ["subtype_id"]:
            errors.append(f"{location} must not require only subtype_id context.")
        if "subtype_id" in required_context and "base_type_id" not in required_context:
            errors.append(f"{location} must not use subtype_id without base_type_id context.")

        if translation.get("production_safe") is not False:
            errors.append(f"{location} production_safe must be false.")
        if translation.get("forge_item_type") == "spear":
            errors.append(f"{location} must not define a spear translation.")
        if translation.get("source") in NAME_ONLY_SOURCES:
            errors.append(f"{location} must not use name-only or slug-only source.")
        if translation.get("match_method") == "subtype_id":
            errors.append(f"{location} must not use subtype_id-only matching.")
        if not isinstance(translation.get("notes"), list):
            errors.append(f"{location} notes must be a list.")

        forge_item_type = translation.get("forge_item_type")
        base_type_id = translation.get("bundle_base_type_id")
        bundle_item_type_id = translation.get("bundle_item_type_id")
        if isinstance(forge_item_type, str) and isinstance(base_type_id, int):
            key = (forge_item_type, base_type_id)
            previous = seen.get(key)
            if previous and previous != bundle_item_type_id:
                errors.append(
                    f"{location} conflicts with another translation for "
                    f"{forge_item_type} + base_type_id {base_type_id}."
                )
            seen[key] = str(bundle_item_type_id)

    return errors, warnings
