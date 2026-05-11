from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_import_context_report import (
    build_le_tools_import_context_report,
    extract_import_item_records,
    load_payload,
    render_le_tools_import_context_report,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "le_tools_parsed_gear_context_sample.json"


def test_helm_with_base_type_id_resolves():
    report = build_le_tools_import_context_report(
        [{"slot": "helmet", "item_type": "helm", "baseTypeID": 0}],
        source="fixture",
    )

    assert report["production_safe"] is False
    assert report["status_counts"]["resolved"] == 1
    item = report["items"][0]
    assert item["resolver_status"] == "resolved"
    assert item["bundle_item_type_id"] == "helmet"
    assert item["production_safe"] is False


def test_axe_without_base_type_id_needs_context():
    report = build_le_tools_import_context_report([{"slot": "weapon", "item_type": "axe"}])

    assert report["status_counts"]["needs_context"] == 1
    assert report["items"][0]["resolver_status"] == "needs_context"
    assert any("base_type_id is required" in warning for warning in report["items"][0]["warnings"])


def test_idol_1x1_without_base_type_id_needs_context():
    report = build_le_tools_import_context_report([{"slot": "idol", "itemType": "idol_1x1"}])

    assert report["status_counts"]["needs_context"] == 1
    assert report["items"][0]["resolver_status"] == "needs_context"


def test_spear_returns_needs_review():
    report = build_le_tools_import_context_report(
        [{"slot": "weapon", "item_type": "spear", "baseTypeID": 14}]
    )

    assert report["status_counts"]["needs_review"] == 1
    assert report["items"][0]["resolver_status"] == "needs_review"
    assert report["items"][0]["bundle_item_type_id"] is None


def test_subtype_id_alone_does_not_resolve():
    report = build_le_tools_import_context_report(
        [{"slot": "belt", "item_type": "belt", "subTypeID": 1}]
    )

    assert report["status_counts"]["needs_context"] == 1
    item = report["items"][0]
    assert item["subtype_id_present"] is True
    assert item["bundle_item_type_id"] is None
    assert any("subtype_id" in warning for warning in item["warnings"])


def test_item_name_alone_does_not_resolve():
    report = build_le_tools_import_context_report([{"name": "Iron Casque"}])

    assert report["total_items"] == 1
    assert report["status_counts"]["unresolved"] == 1
    assert report["items"][0]["bundle_item_type_id"] is None
    assert any("name-only matching is not attempted" in warning for warning in report["items"][0]["warnings"])


def test_unknown_item_type_returns_unresolved():
    report = build_le_tools_import_context_report([{"slot": "unknown", "item_type": "unknown_type"}])

    assert report["status_counts"]["unresolved"] == 1
    assert report["items"][0]["resolver_status"] == "unresolved"


def test_status_counts_for_built_in_sample():
    report = build_le_tools_import_context_report()

    assert report["source"] == "sample"
    assert report["total_items"] == 5
    assert report["status_counts"]["resolved"] == 1
    assert report["status_counts"]["needs_context"] == 2
    assert report["status_counts"]["needs_review"] == 1
    assert report["status_counts"]["unresolved"] == 1
    assert all(item["production_safe"] is False for item in report["items"])


def test_fixture_shape_parsing_for_nested_gear_and_equipment():
    assert extract_import_item_records({"gear": {"helmet": {"item_type": "helm", "baseTypeID": 0}}}) == [
        {"item_type": "helm", "baseTypeID": 0}
    ]
    assert extract_import_item_records({"build_data": {"equipment": [{"itemType": "axe"}]}}) == [
        {"itemType": "axe"}
    ]


def test_rendered_report_contains_status_sections():
    rendered = render_le_tools_import_context_report(build_le_tools_import_context_report())

    assert "LE Tools Import Context Dry-Run Report" in rendered
    assert "production_safe: false" in rendered
    assert "Resolver Status Counts" in rendered


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "let.md")


def test_representative_le_tools_fixture_loads_and_counts_are_stable():
    report = build_le_tools_import_context_report(load_payload(FIXTURE_PATH), source="fixture")

    assert report["production_safe"] is False
    assert report["total_items"] == 16
    assert report["status_counts"] == {
        "resolved": 10,
        "needs_context": 3,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 2,
    }
    assert all(item["production_safe"] is False for item in report["items"])


def test_representative_fixture_resolves_base_type_backed_records():
    report = build_le_tools_import_context_report(load_payload(FIXTURE_PATH), source="fixture")
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


def test_representative_fixture_keeps_context_gaps_unresolved_or_warned():
    report = build_le_tools_import_context_report(load_payload(FIXTURE_PATH), source="fixture")

    needs_context = [
        item for item in report["items"] if item["resolver_status"] == "needs_context"
    ]
    needs_review = [
        item for item in report["items"] if item["resolver_status"] == "needs_review"
    ]
    unresolved = [
        item for item in report["items"] if item["resolver_status"] == "unresolved"
    ]

    assert {item["forge_item_type"] for item in needs_context} == {"axe", "idol_1x1", "belt"}
    assert any(item["subtype_id_present"] for item in needs_context)
    assert needs_review[0]["forge_item_type"] == "spear"
    assert {item["forge_item_type"] for item in unresolved} == {"unknown_type", None}
    assert all(item["bundle_item_type_id"] is None for item in needs_context + needs_review + unresolved)
