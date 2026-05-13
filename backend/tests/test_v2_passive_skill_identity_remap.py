from app.planner_adapters.v2.passive_skill_identity import (
    EXCLUDED_CALCULATION_FIELDS,
    V2PassiveSkillIdentityMetadata,
    build_passive_node_identity_view,
    build_skill_identity_view,
    build_skill_node_identity_view,
)
from scripts.report_v2_passive_skill_identity_remap import build_v2_passive_skill_identity_remap_report


def test_v2_passive_skill_identity_views_expose_identity_safe_fields_only():
    passive = build_passive_node_identity_view(_passive_node_record())
    skill = build_skill_identity_view(_skill_record(), identity_status="resolved_top_level")

    assert passive["canonical_id"] == "passive_node:test:1"
    assert passive["tree_id"] == "passive_tree:test"
    assert passive["identity_only_eligible"] is True
    assert passive["planner_calculable"] is False
    assert passive["stable_calculable"] is False
    assert skill["canonical_id"] == "skill:test"
    assert skill["identity_match_status"] == "resolved_top_level"
    assert skill["planner_calculable"] is False
    assert skill["stable_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in passive
        assert field not in skill


def test_v2_passive_skill_identity_does_not_expose_effect_values_as_stats():
    passive = build_passive_node_identity_view(_passive_node_record())
    skill_node = build_skill_node_identity_view(_skill_node_record())

    assert passive["planner_calculable"] is False
    assert skill_node["planner_calculable"] is False
    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field not in passive
        assert field not in skill_node


def test_v2_passive_skill_identity_only_does_not_imply_stable_calculable():
    skill = build_skill_identity_view(_skill_record(stable_calculable=True, support_status="trusted"))

    assert skill["identity_only_eligible"] is True
    assert skill["planner_calculable"] is False
    assert skill["stable_calculable"] is False
    assert "stable_calculable_false" in skill["blocked_reasons"]


def test_v2_passive_skill_identity_summary_preserves_safety_state():
    summary = V2PassiveSkillIdentityMetadata().summarize_identity_metadata(sample_limit=2)

    assert summary["summary"]["passive_tree_count"] == 5
    assert summary["summary"]["passive_node_count"] == 535
    assert summary["summary"]["skill_count"] == 184
    assert summary["summary"]["skill_tree_count"] == 136
    assert summary["summary"]["skill_node_count"] == 3919
    assert summary["summary"]["planner_calculable_count"] == 0
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["summary"]["production_consumed"] is False
    assert summary["summary"]["value_normalization_status"] == "audit_only"
    assert summary["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["skill_identity_audit_summary"]["safe_top_level_matches"] == 60
    assert summary["skill_identity_audit_summary"]["unresolved_refs"] == 2
    assert summary["skill_identity_audit_summary"]["ambiguous_refs"] == 1
    assert summary["skill_identity_audit_summary"]["bridge_safe"] is False
    assert summary["passive_skill_tree_metadata_treatment"]["tooltip_text_used_for_mechanics"] is False


def test_v2_passive_skill_identity_report_has_required_sections():
    report = build_v2_passive_skill_identity_remap_report()

    assert report["schema_version"] == "v2.passive_skill_identity_remap.1"
    assert report["summary"]["planner_calculable_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["optional_route_added"] is False
    assert report["summary"]["optional_frontend_updated"] is False
    assert report["skill_identity_audit_summary"]["total_refs"] == 63
    assert report["skill_identity_audit_summary"]["safe_top_level_matches"] == 60
    assert report["skill_identity_audit_summary"]["bridge_safe"] is False
    assert "passive_skill_tree_metadata_treatment" in report
    assert "fields_excluded_from_calculation" in report


def test_v2_passive_skill_identity_forbidden_fields_are_documented_and_absent():
    report = build_v2_passive_skill_identity_remap_report()

    for field in EXCLUDED_CALCULATION_FIELDS:
        assert field in report["fields_excluded_from_calculation"]
    for sample in report["metadata_samples"]:
        for field in EXCLUDED_CALCULATION_FIELDS:
            assert field not in sample


def test_v2_passive_skill_identity_keeps_unresolved_and_ambiguous_refs_visible():
    report = build_v2_passive_skill_identity_remap_report()

    assert report["skill_identity_audit_summary"]["unresolved_refs"] == 2
    assert report["skill_identity_audit_summary"]["ambiguous_refs"] == 1
    assert report["skill_identity_examples"]["unresolved"]
    assert report["skill_identity_examples"]["ambiguous"]
    assert report["safety_confirmations"]["skill_identity_bridge_added"] is False
    assert report["safety_confirmations"]["skill_identity_bridge_safe"] is False


def _provenance(source_id="test"):
    return {
        "source_path": "exports_json/test.json",
        "source_type": "generated_from_game_data",
        "source_id": source_id,
        "extraction_method": "test_fixture",
        "schema_version": "test.1",
        "patch_version": "test",
    }


def _passive_node_record(**overrides):
    record = {
        "canonical_id": "passive_node:test:1",
        "display_name": "Test Passive",
        "tree_id": "passive_tree:test",
        "owner_class_id": "class:test",
        "owner_mastery_id": None,
        "source_id": "test:1",
        "source_tree_id": "test",
        "source_file": "exports_json/passive_trees.json",
        "provenance": _provenance("test:1"),
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "stable_calculable": False,
        "warnings": ["display only"],
        "modifier_rows": [{"value": 1}],
        "text_effects": ["effect text"],
        "tooltip_text": "effect text",
    }
    record.update(overrides)
    return record


def _skill_record(**overrides):
    record = {
        "canonical_id": "skill:test",
        "display_name": "Test Skill",
        "skill_tree_id": "skill_tree:test",
        "owner_class_ids": ["class:test"],
        "owner_mastery_ids": [],
        "source_id": "test",
        "source_skill_id": "test",
        "source_file": "exports_json/skills_with_trees.json",
        "sourceIdentity": {"abilityPathId": "skill_path:1"},
        "provenance": _provenance("test"),
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "stable_calculable": False,
        "warnings": ["display only"],
        "damage_types": ["Fire"],
        "skill_tags": ["Spell"],
        "tooltip_text": "effect text",
        "cost": {"mana_cost": 1},
    }
    record.update(overrides)
    return record


def _skill_node_record(**overrides):
    record = {
        "canonical_id": "skill_node:test:1",
        "display_name": "Test Skill Node",
        "skill_tree_id": "skill_tree:test",
        "skill_id": "skill:test",
        "owner_class_ids": ["class:test"],
        "owner_mastery_ids": [],
        "source_id": "test:1",
        "source_tree_id": "test",
        "source_file": "exports_json/skills_with_trees.json",
        "raw_reference": {"source_skill_id": "test"},
        "provenance": _provenance("test:1"),
        "support_status": "partial",
        "trust_level": "generated_from_game_data",
        "stable_calculable": False,
        "warnings": ["display only"],
        "modifier_rows": [{"value": 1}],
        "text_effects": ["effect text"],
        "tooltip_text": "effect text",
    }
    record.update(overrides)
    return record
