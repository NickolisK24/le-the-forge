"""Compare legacy AffixRegistry data with the Forge-safe affix export.

Usage:
    python scripts/compare_forge_safe_affixes.py --export-path path/to/forge_safe_canonical_affixes.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app import create_app
from data.repositories.forge_safe_affix_repository import ForgeSafeAffixRepository


def _legacy_records(app) -> dict[str, dict[str, Any]]:
    registry = app.extensions["affix_registry"]
    result = {}
    for affix in registry.all():
        affix_id = str(affix.affix_id if affix.affix_id is not None else affix.name)
        result[affix_id] = {
            "id": affix_id,
            "name": affix.name,
            "source_type": affix.affix_type,
            "item_types": list(affix.applicable_to),
        }
    return result


def compare(export_path: str | Path, env: str = "development") -> dict[str, Any]:
    app = create_app(env)
    with app.app_context():
        legacy = _legacy_records(app)
    forge = {record.id: record.to_catalog_dict() for record in ForgeSafeAffixRepository(export_path).all()}

    legacy_ids = set(legacy)
    forge_ids = set(forge)
    matching_ids = sorted(legacy_ids & forge_ids)
    name_mismatches = [
        {"id": affix_id, "legacy": legacy[affix_id]["name"], "forge_safe": forge[affix_id]["name"]}
        for affix_id in matching_ids
        if legacy[affix_id]["name"] != forge[affix_id]["name"]
    ]
    source_type_mismatches = [
        {"id": affix_id, "legacy": legacy[affix_id].get("source_type"), "forge_safe": forge[affix_id].get("source_type")}
        for affix_id in matching_ids
        if legacy[affix_id].get("source_type") != forge[affix_id].get("source_type")
    ]
    item_type_mismatches = [
        {"id": affix_id, "legacy": legacy[affix_id].get("item_types", []), "forge_safe": forge[affix_id].get("item_types", [])}
        for affix_id in matching_ids
        if sorted(legacy[affix_id].get("item_types", [])) != sorted(forge[affix_id].get("item_types", []))
    ]
    return {
        "total_counts": {"legacy": len(legacy), "forge_safe": len(forge), "matching_ids": len(matching_ids)},
        "forge_safe_not_legacy": sorted(forge_ids - legacy_ids),
        "legacy_not_forge_safe": sorted(legacy_ids - forge_ids),
        "matching_ids": matching_ids,
        "name_mismatches": name_mismatches,
        "source_type_mismatches": source_type_mismatches,
        "item_type_mismatches": item_type_mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-path", required=True)
    parser.add_argument("--env", default="development")
    args = parser.parse_args()
    print(json.dumps(compare(args.export_path, args.env), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
