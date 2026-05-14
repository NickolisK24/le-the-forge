from app.planner_adapters.v2.metadata import (
    FORBIDDEN_CALCULATION_FIELDS,
    V2PlannerMetadataRemap,
    build_metadata_view,
)
from scripts.report_v2_planner_metadata_remap import build_v2_planner_metadata_remap_report


def test_v2_planner_metadata_view_exposes_only_non_calculating_fields():
    view = build_metadata_view(_modifier_record())

    assert view["canonical_id"] == "modifier:test"
    assert view["display_name"] == "Test Modifier"
    assert view["source_path"] == "test.json"
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False
    for field in FORBIDDEN_CALCULATION_FIELDS:
        assert field not in view


def test_v2_planner_metadata_display_only_does_not_imply_stable_calculable():
    view = build_metadata_view(_modifier_record(stable_calculable=True, value_scale_status="planner_normalized"))

    assert view["display_only_eligible"] is True
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False


def test_v2_planner_metadata_keeps_blocked_reasons_visible():
    view = build_metadata_view(_modifier_record(value_scale_status="source_units", support_status="partial"))

    assert "source_units_value_scale" in view["adapter_blocked_reasons"]
    assert "unstable_support_status" in view["adapter_blocked_reasons"]
    assert "not_stable_calculable" in view["adapter_blocked_reasons"]


def test_v2_planner_metadata_summary_preserves_safety_status():
    summary = V2PlannerMetadataRemap().summarize_metadata(sample_limit=2)

    assert summary["summary"]["metadata_records_inspected"] == 19398
    assert summary["summary"]["display_only_eligible_count"] == 19398
    assert summary["summary"]["planner_calculable_count"] == 0
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["summary"]["production_consumed"] is False
    assert summary["summary"]["value_normalization_status"] == "audit_only"
    assert summary["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["metadata_policy"]["display_only_does_not_imply_planner_calculable"] is True
    assert summary["metadata_policy"]["values_exposed_for_planner_math"] is False


def test_v2_planner_metadata_report_has_required_sections():
    report = build_v2_planner_metadata_remap_report()

    assert report["schema_version"] == "v2.planner_metadata_remap.1"
    assert "fields_exposed" in report
    assert "forbidden_calculation_fields" in report
    assert "display_only_candidates" in report
    assert "blocked_mechanical_data" in report
    assert report["summary"]["planner_calculable_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["metadata"]["optional_route_added"] is False


def test_v2_planner_metadata_forbidden_calculation_fields_are_documented():
    report = build_v2_planner_metadata_remap_report()

    for field in FORBIDDEN_CALCULATION_FIELDS:
        assert field in report["forbidden_calculation_fields"]
    for sample in report["metadata_samples"]:
        for field in FORBIDDEN_CALCULATION_FIELDS:
            assert field not in sample


def _modifier_record(**overrides):
    record = {
        "canonical_modifier_id": "modifier:test",
        "source_type": "affix",
        "source_id": "affix:test",
        "source_display_name": "Test Modifier",
        "stat_id": "stat:health",
        "raw_stat_name": "Health",
        "operation": "flat",
        "raw_value_min": 1,
        "raw_value_max": 2,
        "normalized_value_min": None,
        "normalized_value_max": None,
        "value_scale_status": "source_units",
        "source_identity_status": "not_applicable",
        "source_record_status": "modifier_row",
        "special_behavior_classification": None,
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "stable_calculable": False,
        "provenance": {
            "source_path": "test.json",
            "source_type": "test",
            "source_id": "test",
            "schema_version": "test.1",
            "extraction_method": "test",
        },
        "warnings": ["test warning"],
    }
    record.update(overrides)
    return record
