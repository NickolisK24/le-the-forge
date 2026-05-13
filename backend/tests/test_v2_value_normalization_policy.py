import json
from pathlib import Path

from app.normalization.v2.value_scale_policy import classify_family, family_key, stat_family
from scripts.report_v2_value_normalization_policy import build_value_normalization_policy_report


def test_value_normalization_report_generation_counts_source_units_and_unknown():
    report, candidates = build_value_normalization_policy_report(_modifiers())

    assert report["summary"]["total_modifier_count"] == 4
    assert report["summary"]["source_unit_modifier_count"] == 2
    assert report["summary"]["unknown_scale_modifier_count"] == 2
    assert report["summary"]["safe_family_count"] == 0
    assert report["summary"]["stable_calculable_count_changed"] is False
    assert candidates["summary"]["candidate_family_count"] == 2


def test_source_unit_percent_family_is_candidate_not_safe_without_evidence():
    rows = [_modifier("m1", operation="increased", stat_id="stat:increased_damage", scale="source_units")]

    decision = classify_family(rows)

    assert decision["policy_status"] == "candidate_percent_family_requires_source_validation"
    assert decision["planner_normalization_safe"] is False
    assert decision["blocked_reasons"] == ["missing_explicit_scale_evidence"]


def test_source_unit_numeric_family_is_candidate_not_global_scale():
    rows = [_modifier("m1", operation="flat", stat_id="stat:added_health", scale="source_units")]

    decision = classify_family(rows)

    assert decision["policy_status"] == "candidate_numeric_family_requires_source_validation"
    assert decision["planner_normalization_safe"] is False
    assert decision["proposed_scale_factor"] is None


def test_explicit_high_confidence_evidence_can_mark_family_safe():
    rows = [_modifier("m1", operation="increased", stat_id="stat:increased_damage", scale="source_units")]

    decision = classify_family(
        rows,
        {
            "evidence_type": "golden_planner_baseline",
            "confidence": "high",
            "scale_factor": 100,
        },
    )

    assert decision["policy_status"] == "candidate_safe_with_explicit_evidence"
    assert decision["planner_normalization_safe"] is True
    assert decision["proposed_scale_factor"] == 100


def test_unknown_or_unsafe_family_stays_blocked():
    rows = [
        _modifier(
            "m1",
            operation="unknown",
            stat_id="stat:unknown",
            scale="unknown",
            special_behavior_classification="unsupported_special_behavior",
        )
    ]

    decision = classify_family(rows)

    assert decision["policy_status"] == "blocked_or_unsafe"
    assert decision["planner_normalization_safe"] is False
    assert "unknown_value_scale" in decision["blocked_reasons"]
    assert "unknown_operation" in decision["blocked_reasons"]
    assert "unknown_stat_id" in decision["blocked_reasons"]
    assert "special_behavior_not_calculable" in decision["blocked_reasons"]


def test_source_identity_gap_blocks_even_with_known_operation():
    rows = [_modifier("m1", operation="cost", stat_id="stat:cost_mana", scale="source_units", source_identity_status="partially_unresolved")]

    decision = classify_family(rows)

    assert decision["policy_status"] == "blocked_or_unsafe"
    assert "source_identity_gap" in decision["blocked_reasons"]


def test_family_helpers_are_deterministic():
    row = _modifier("m1", operation="increased", stat_id="stat:increased_damage_spell", scale="source_units")

    assert stat_family(row["stat_id"]) == "increased_damage"
    assert family_key(row) == "affix|increased|increased_damage"


def test_generated_policy_report_json_shape(tmp_path):
    report, candidates = build_value_normalization_policy_report(_modifiers())
    output = tmp_path / "policy.json"
    output.write_text(json.dumps(report), encoding="utf-8")
    loaded = json.loads(output.read_text(encoding="utf-8"))

    assert loaded["metadata"]["read_only"] is True
    assert loaded["metadata"]["production_safe"] is False
    assert loaded["summary"]["production_consumed"] is False
    assert candidates["metadata"]["read_only"] is True


def _modifier(
    modifier_id: str,
    *,
    operation: str,
    stat_id: str,
    scale: str,
    source_type: str = "affix",
    source_identity_status: str = "not_applicable",
    special_behavior_classification: str | None = None,
) -> dict:
    return {
        "canonical_modifier_id": modifier_id,
        "source_type": source_type,
        "source_id": f"{source_type}:1",
        "source_display_name": "Example",
        "stat_id": stat_id,
        "operation": operation,
        "raw_value_min": 0.1,
        "raw_value_max": 0.2,
        "value_scale_status": scale,
        "source_identity_status": source_identity_status,
        "special_behavior_classification": special_behavior_classification,
    }


def _modifiers() -> list[dict]:
    return [
        _modifier("m1", operation="increased", stat_id="stat:increased_damage", scale="source_units"),
        _modifier("m2", operation="flat", stat_id="stat:added_health", scale="source_units"),
        _modifier("m3", operation="unknown", stat_id="stat:unknown", scale="unknown"),
        _modifier("m4", operation="cost", stat_id="stat:cost_mana", scale="unknown", source_type="skill_structured_value", source_identity_status="partially_unresolved"),
    ]
