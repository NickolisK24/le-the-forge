from scripts.report_v3_production_remap_gate_audit import (
    AUDIT_CATEGORIES,
    build_v3_production_remap_gate_audit_report,
)


def test_production_remap_gate_audit_recommends_not_ready():
    report = build_v3_production_remap_gate_audit_report()

    assert report["schema_version"] == "v3.production_remap_gate_audit_report.1"
    assert report["final_recommendation"] == "PRODUCTION_REMAP_NOT_READY"
    assert report["production_remap_allowed"] is False
    assert report["production_remap_enabled"] is False
    assert report["metadata"]["audit_only"] is True
    assert report["metadata"]["production_behavior_changed"] is False
    assert report["metadata"]["production_remap_performed"] is False


def test_production_remap_gate_audit_uses_expected_categories():
    report = build_v3_production_remap_gate_audit_report()
    observed = set(report["audit_category_counts"])

    assert observed <= set(AUDIT_CATEGORIES)
    assert "remap_ready" in observed
    assert "partially_ready" in observed
    assert "requires_policy_decision" in observed
    assert "blocked_by_missing_baseline" in observed
    assert "blocked_by_identity_gap" in observed
    assert "blocked_by_unknown_operation" in observed
    assert "blocked_by_unsupported_mechanics" in observed
    assert "blocked_by_value_normalization" in observed
    assert "blocked_by_missing_provenance" in observed


def test_production_remap_gate_audit_validates_determinism_and_rollback_visibility():
    report = build_v3_production_remap_gate_audit_report()

    assert report["deterministic_guarantees"]["passed"] is True
    assert report["deterministic_guarantees"]["sample_hash"] == report["deterministic_guarantees"]["repeated_hash"]
    assert report["rollback_debug_guarantees"]["passed"] is True
    assert "execution_rows" in report["rollback_debug_guarantees"]["debug_visibility"]
    assert "candidate_aggregates" in report["rollback_debug_guarantees"]["debug_visibility"]
    assert "blocked_reasons" in report["rollback_debug_guarantees"]["debug_visibility"]


def test_production_remap_gate_audit_validates_unsupported_mechanic_protection():
    report = build_v3_production_remap_gate_audit_report()
    guarantees = report["unsupported_mechanic_guarantees"]

    assert guarantees["passed"] is True
    assert guarantees["blocked_row_count"] > 0
    assert guarantees["promoted_to_execution"] == []
    assert "blocked_unsupported_mechanic" in guarantees["blocked_categories"]
    assert "blocked_text_only_mechanic" in guarantees["blocked_categories"]
    assert "blocked_scripted_mechanic" in guarantees["blocked_categories"]


def test_production_remap_gate_audit_marks_no_domain_stable_for_production_remap():
    report = build_v3_production_remap_gate_audit_report()

    assert report["stable_calculable_findings"]
    assert report["summary"]["stable_calculable_domain_count"] == 0
    assert all(finding["stable_calculable_for_production_remap"] is False for finding in report["stable_calculable_findings"])
    assert {finding["domain"] for finding in report["stable_calculable_findings"]} == {"item_affix", "passive_skill"}


def test_production_remap_gate_audit_current_blockers_are_explicit():
    report = build_v3_production_remap_gate_audit_report()
    blocker_ids = {blocker["gate_id"] for blocker in report["current_blockers"]}

    assert "value_normalization_readiness" in blocker_ids
    assert "operation_semantics_readiness" in blocker_ids
    assert "stat_identity_readiness" in blocker_ids
    assert "skill_identity_readiness" in blocker_ids
    assert "unsupported_mechanic_exclusion" in blocker_ids
    assert "provenance_readiness" in blocker_ids
    assert "golden_baseline_evidence" in blocker_ids
    assert "comparison_backed_execution" in blocker_ids
    assert "policy_decisions" in blocker_ids
