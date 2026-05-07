from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_import_context_report import (
    build_le_tools_import_context_report,
    extract_import_item_records,
    render_le_tools_import_context_report,
)


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
