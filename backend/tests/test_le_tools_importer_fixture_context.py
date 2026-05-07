from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from app.game_data.le_tools_import_context_report import (
    build_le_tools_import_context_report,
    load_payload,
)
from app.routes.import_route import _map_let_build


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "le_tools_offline_buildinfo_equipment_sample.json"


def _load_build_info() -> dict:
    return load_payload(FIXTURE_PATH)["build_info"]


def _diagnostic_context_from_mapped_gear(mapped_gear: list[dict], build_info: dict) -> list[dict]:
    """Build a diagnostic-only copy; do not mutate importer output."""

    raw_equipment = build_info.get("equipment") or []
    copied: list[dict] = []
    for index, item in enumerate(deepcopy(mapped_gear)):
        source_raw = raw_equipment[index] if index < len(raw_equipment) and isinstance(raw_equipment[index], dict) else {}
        raw = item.get("_raw") if isinstance(item.get("_raw"), dict) else {}
        raw = {**source_raw, **raw}
        copied_item = {
            "slot": item.get("slot"),
            "base_type_id": item.get("base_type_id"),
            "subtype_id": raw.get("subTypeID"),
            "item_type": raw.get("item_type"),
            "name": item.get("item_name") or raw.get("name"),
        }
        copied.append(copied_item)
    return copied


def test_offline_buildinfo_fixture_maps_without_network_and_preserves_output_shape():
    build_info = _load_build_info()

    with patch("app.services.importers.lastepochtools_importer._requests.get") as mock_get:
        mapped = _map_let_build(build_info)

    mock_get.assert_not_called()
    assert mapped["_import_meta"]["source"] == "lastepochtools"
    assert mapped["_import_meta"]["gear_count"] == 14
    assert len(mapped["gear"]) == 14
    for item in mapped["gear"]:
        assert {"slot", "base_type_id", "item_name", "rarity", "affixes"}.issubset(item)
        assert "item_type" not in item
        assert "bundle_item_type_id" not in item


def test_context_report_against_copied_mapped_output_resolves_and_warns_safely():
    build_info = _load_build_info()
    mapped = _map_let_build(build_info)
    original_gear = deepcopy(mapped["gear"])
    diagnostic_input = _diagnostic_context_from_mapped_gear(mapped["gear"], build_info)

    report = build_le_tools_import_context_report(
        diagnostic_input,
        source="offline_buildinfo_mapped_copy",
    )

    assert mapped["gear"] == original_gear
    assert report["production_safe"] is False
    assert all(item["production_safe"] is False for item in report["items"])
    assert report["total_items"] == 14
    assert report["status_counts"] == {
        "resolved": 10,
        "needs_context": 2,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 1,
    }

    resolved = {
        (item["forge_item_type"], item["base_type_id"]): item["bundle_item_type_id"]
        for item in report["items"]
        if item["resolver_status"] == "resolved"
    }
    assert resolved[("helm", 0)] == "helmet"
    assert resolved[("chest", 1)] == "body_armor"
    assert resolved[("axe", 5)] == "one_handed_axe"
    assert resolved[("axe", 12)] == "two_handed_axe"
    assert resolved[("mace", 7)] == "one_handed_maces"
    assert resolved[("mace", 13)] == "two_handed_mace"
    assert resolved[("sword", 9)] == "one_handed_sword"
    assert resolved[("sword", 16)] == "two_handed_sword"
    assert resolved[("idol_1x1", 25)] == "idol_1x1_eterra"
    assert resolved[("idol_1x1", 26)] == "idol_1x1_lagon"

    needs_context = [
        item for item in report["items"] if item["resolver_status"] == "needs_context"
    ]
    assert {item["forge_item_type"] for item in needs_context} == {"axe", "belt"}
    assert any(item["subtype_id_present"] for item in needs_context)

    needs_review = [
        item for item in report["items"] if item["resolver_status"] == "needs_review"
    ]
    assert needs_review[0]["forge_item_type"] == "spear"

    unresolved = [
        item for item in report["items"] if item["resolver_status"] == "unresolved"
    ]
    assert unresolved[0]["forge_item_type"] == "unknown_type"
