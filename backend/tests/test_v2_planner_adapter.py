import json
from pathlib import Path

from app.normalization.v2.modifier_registry import V2ModifierRegistry
from app.planner_adapters.v2 import V2PlannerSafeAdapter, evaluate_modifier_record
from scripts.report_v2_planner_adapter import build_v2_planner_adapter_report


def test_v2_planner_adapter_blocks_source_units_and_partial_support():
    result = evaluate_modifier_record(_modifier_record())

    assert result.eligible is False
    assert "unstable_support_status" in result.blocked_reasons
    assert "source_units_value_scale" in result.blocked_reasons
    assert "not_stable_calculable" in result.blocked_reasons


def test_v2_planner_adapter_blocks_unresolved_identity_and_unknown_stat():
    record = _modifier_record(
        stat_id="stat:unknown",
        operation="unknown",
        value_scale_status="unknown",
        source_identity_status="unresolved",
    )

    result = evaluate_modifier_record(record)

    assert result.eligible is False
    assert "unresolved_stat_identity" in result.blocked_reasons
    assert "unknown_operation" in result.blocked_reasons
    assert "unknown_value_scale" in result.blocked_reasons
    assert "unresolved_skill_identity" in result.blocked_reasons


def test_v2_planner_adapter_blocks_unsupported_scripted_and_text_only_behavior():
    scripted = evaluate_modifier_record(
        _modifier_record(
            value_scale_status="planner_normalized",
            special_behavior_classification="scripted_runtime_behavior",
        )
    )
    text_only = evaluate_modifier_record(
        _modifier_record(
            value_scale_status="planner_normalized",
            special_behavior_classification="text_only_effect",
        )
    )
    unsupported = evaluate_modifier_record(
        _modifier_record(
            value_scale_status="planner_normalized",
            special_behavior_classification="unsupported_special_behavior",
        )
    )

    assert "scripted_behavior" in scripted.blocked_reasons
    assert "text_only_behavior" in text_only.blocked_reasons
    assert "unsupported_behavior" in unsupported.blocked_reasons


def test_v2_planner_adapter_allows_only_explicit_stable_planner_normalized_records():
    result = evaluate_modifier_record(
        _modifier_record(
            support_status="trusted",
            value_scale_status="planner_normalized",
            stable_calculable=True,
        )
    )

    assert result.eligible is True
    assert result.blocked_reasons == ()


def test_v2_planner_adapter_summarizes_zero_eligible_current_registry():
    summary = V2PlannerSafeAdapter().summarize_eligibility(sample_limit=2)

    assert summary["summary"]["inspected_modifier_count"] == 19398
    assert summary["summary"]["eligible_planner_calculable_count"] == 0
    assert summary["summary"]["blocked_modifier_count"] == 19398
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["policy"]["production_consumed"] is False
    assert summary["policy"]["value_normalization_status"] == "audit_only"
    assert summary["policy"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["blocked_reason_counts"]["not_stable_calculable"] == 19398


def test_v2_planner_adapter_is_read_only(tmp_path):
    registry_path = tmp_path / "v2_modifier_registry.json"
    payload = _registry_payload([_modifier_record()])
    registry_path.write_text(json.dumps(payload), encoding="utf-8")
    before = registry_path.read_text(encoding="utf-8")

    registry = V2ModifierRegistry(registry_path).load()
    summary = V2PlannerSafeAdapter(modifier_registry=registry).summarize_eligibility()

    assert summary["summary"]["inspected_modifier_count"] == 1
    assert registry_path.read_text(encoding="utf-8") == before


def test_v2_planner_adapter_report_preserves_safety_status():
    report = build_v2_planner_adapter_report()

    assert report["summary"]["eligible_planner_calculable_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["summary"]["production_consumed"] is False
    assert report["summary"]["value_normalization_status"] == "audit_only"
    assert report["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert report["metadata"]["planner_consumed"] is False


def _modifier_record(**overrides):
    record = {
        "canonical_modifier_id": "modifier:test",
        "source_type": "affix",
        "source_id": "affix:test",
        "source_display_name": "Test",
        "stat_id": "stat:health",
        "raw_stat_id": "Health",
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
        "provenance": {"source_path": "test.json"},
    }
    record.update(overrides)
    return record


def _registry_payload(records):
    return {
        "schema_version": "v2.modifier_registry.1",
        "summary": {"modifier_count": len(records), "stable_calculable_count": 0},
        "records": {"modifiers": records},
    }
