from app.planner_adapters.v2.item_metadata import (
    EXCLUDED_CALCULATION_FIELDS,
    V2ItemBaseDisplayMetadata,
    build_item_base_metadata_view,
)
from scripts.report_v2_item_base_display_metadata import build_v2_item_base_display_metadata_report


def test_v2_item_base_metadata_view_exposes_display_safe_fields_only():
    view = build_item_base_metadata_view(_base_record(), [_implicit_record()])

    assert view["canonical_id"] == "item_base:test"
    assert view["display_name"] == "Test Helmet"
    assert view["slot"] == "helmet"
    assert view["implicit_count"] == 1
    assert view["display_only_eligible"] is True
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in view


def test_v2_item_base_metadata_does_not_expose_implicit_values_as_stats():
    view = build_item_base_metadata_view(_base_record(), [_implicit_record()])
    implicit = view["implicit_metadata"][0]

    assert implicit["canonical_id"] == "implicit:test"
    assert implicit["modifier_reference_count"] == 1
    assert implicit["planner_calculable"] is False
    assert implicit["stable_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in implicit


def test_v2_item_base_metadata_display_only_does_not_imply_stable_calculable():
    view = build_item_base_metadata_view(
        _base_record(stable_calculable=True, support_status="trusted"),
        [_implicit_record()],
    )

    assert view["display_only_eligible"] is True
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False
    assert "stable_calculable_false" in view["blocked_reasons"]


def test_v2_item_base_metadata_summary_preserves_safety_state():
    summary = V2ItemBaseDisplayMetadata().summarize_metadata(sample_limit=2)

    assert summary["summary"]["item_base_count"] == 542
    assert summary["summary"]["implicit_record_count"] == 1182
    assert summary["summary"]["display_only_eligible_count"] == 542
    assert summary["summary"]["planner_calculable_count"] == 0
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["summary"]["production_consumed"] is False
    assert summary["summary"]["value_normalization_status"] == "audit_only"
    assert summary["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["implicit_metadata_treatment"]["modifier_rows_exposed"] is False
    assert summary["implicit_metadata_treatment"]["modifier_values_exposed_as_planner_stats"] is False


def test_v2_item_base_display_metadata_report_has_required_sections():
    report = build_v2_item_base_display_metadata_report()

    assert report["schema_version"] == "v2.item_base_display_metadata.1"
    assert report["summary"]["item_base_count"] == 542
    assert report["summary"]["planner_calculable_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["optional_route_added"] is False
    assert report["summary"]["optional_frontend_updated"] is False
    assert "implicit_metadata_treatment" in report
    assert "fields_excluded_from_calculation" in report


def test_v2_item_base_display_metadata_forbidden_fields_are_documented_and_absent():
    report = build_v2_item_base_display_metadata_report()

    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field in report["fields_excluded_from_calculation"]
    for sample in report["metadata_samples"]:
        for field in EXCLUDED_CALCULATION_FIELDS:
            assert field not in sample
        for implicit in sample["implicit_metadata"]:
            for field in EXCLUDED_CALCULATION_FIELDS:
                assert field not in implicit


def _base_record(**overrides):
    record = {
        "canonical_id": "item_base:test",
        "display_name": "Test Helmet",
        "item_category": "equipment",
        "item_type": "helmet",
        "subtype": "Test Helmet",
        "slot": "helmet",
        "classification": "armor",
        "level_requirement": 1,
        "class_restrictions": [],
        "mastery_restrictions": [],
        "maximum_affixes": 4,
        "stable_calculable": False,
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "source_id": "test",
        "source_file": "test.json",
        "provenance": {
            "source_path": "test.json",
            "source_type": "item_base",
            "source_id": "test",
            "schema_version": "test.1",
            "extraction_method": "test",
            "patch_version": "test",
        },
        "warnings": ["display only"],
        "base_stats": {"armour": 10},
    }
    record.update(overrides)
    return record


def _implicit_record(**overrides):
    record = {
        "canonical_id": "implicit:test",
        "display_name": "Test Implicit",
        "item_base_id": "item_base:test",
        "item_type": "helmet",
        "stable_calculable": False,
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "source_file": "test.json",
        "provenance": {
            "source_path": "test.json",
            "source_type": "item_implicit",
            "source_id": "test:implicit",
            "schema_version": "test.1",
            "extraction_method": "test",
            "patch_version": "test",
        },
        "warnings": ["display only"],
        "modifier_references": [{"modifier_id": "implicit:test"}],
        "modifier_rows": [{"value_min": 1, "value_max": 2}],
        "value_range": {"min": 1, "max": 2},
    }
    record.update(overrides)
    return record
