from app.planner_adapters.v2.affix_metadata import (
    EXCLUDED_CALCULATION_FIELDS,
    V2AffixDisplayProvenanceMetadata,
    build_affix_metadata_view,
)
from scripts.report_v2_affix_display_provenance import build_v2_affix_display_provenance_report


def test_v2_affix_metadata_view_exposes_display_provenance_safe_fields_only():
    view = build_affix_metadata_view(_affix_record())

    assert view["canonical_id"] == "affix:equipment:1"
    assert view["display_name"] == "Test Health"
    assert view["domain"] == "equipment"
    assert view["tier_count"] == 1
    assert view["modifier_reference_count"] == 1
    assert view["display_only_eligible"] is True
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in view


def test_v2_affix_metadata_does_not_expose_tier_or_modifier_values_as_stats():
    view = build_affix_metadata_view(_affix_record())
    modifier = view["modifier_reference_metadata"][0]

    assert modifier["modifier_id"] == "equipment:1"
    assert modifier["property"] == "Health"
    assert modifier["planner_calculable"] is False
    assert modifier["stable_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in modifier


def test_v2_affix_metadata_display_only_does_not_imply_stable_calculable():
    view = build_affix_metadata_view(_affix_record(stable_calculable=True, support_status="trusted"))

    assert view["display_only_eligible"] is True
    assert view["planner_calculable"] is False
    assert view["stable_calculable"] is False
    assert "stable_calculable_false" in view["blocked_reasons"]


def test_v2_affix_metadata_summary_preserves_safety_state():
    summary = V2AffixDisplayProvenanceMetadata().summarize_metadata(sample_limit=2)

    assert summary["summary"]["affix_count"] == 1098
    assert summary["summary"]["display_only_eligible_count"] == 1098
    assert summary["summary"]["planner_calculable_count"] == 0
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["summary"]["production_consumed"] is False
    assert summary["summary"]["value_normalization_status"] == "audit_only"
    assert summary["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["tier_modifier_metadata_treatment"]["tier_ranges_exposed"] is False
    assert summary["tier_modifier_metadata_treatment"]["modifier_values_exposed_as_planner_stats"] is False


def test_v2_affix_display_provenance_report_has_required_sections():
    report = build_v2_affix_display_provenance_report()

    assert report["schema_version"] == "v2.affix_display_provenance.1"
    assert report["summary"]["affix_count"] == 1098
    assert report["summary"]["planner_calculable_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["optional_route_added"] is False
    assert report["summary"]["optional_frontend_updated"] is False
    assert "tier_modifier_metadata_treatment" in report
    assert "fields_excluded_from_calculation" in report


def test_v2_affix_display_provenance_forbidden_fields_are_documented_and_absent():
    report = build_v2_affix_display_provenance_report()

    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field in report["fields_excluded_from_calculation"]
    for sample in report["metadata_samples"]:
        for field in EXCLUDED_CALCULATION_FIELDS:
            assert field not in sample
        for modifier in sample["modifier_reference_metadata"]:
            for field in EXCLUDED_CALCULATION_FIELDS:
                assert field not in modifier


def _affix_record(**overrides):
    record = {
        "canonical_id": "affix:equipment:1",
        "display_name": "Test Health",
        "source_id": "equipment:1",
        "source_type": "equipment",
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "provenance": {
            "source_path": "exports_json/affixes.json",
            "source_type": "equipment",
            "source_id": "equipment:1",
            "extraction_method": "test_fixture",
            "schema_version": "v2.affix_bundle.1",
            "patch_version": "test",
        },
        "affix_domain": "equipment",
        "affix_type": "prefix",
        "prefix_suffix": "prefix",
        "categories": ["PREFIX"],
        "slot_restrictions": ["HELMET"],
        "item_type_restrictions": ["HELMET"],
        "class_restrictions": [],
        "mastery_restrictions": [],
        "tier_count": 1,
        "tier_ranges": [{"tier": 1, "min_value": 5, "max_value": 10}],
        "modifier_reference_count": 1,
        "modifier_references": [
            {
                "modifier_id": "equipment:1",
                "modifier_type": "ADDED",
                "property": "Health",
                "property_path": "ADDED.Health",
                "source_record_id": "equipment:1",
                "tags": ["Health"],
            }
        ],
        "stable_calculable": False,
        "warnings": ["display only"],
        "value_scale_policy": "source_units",
        "polarity_policy": "source_preserved",
    }
    record.update(overrides)
    return record
