from scripts.report_v3_golden_baseline_readiness_audit import (
    ALLOWED_BASELINE_READINESS_STATES,
    BASELINE_READINESS_ENTRY_FIELDS,
    build_v3_golden_baseline_readiness_audit_report,
)


def test_v3_golden_baseline_readiness_report_generation_succeeds():
    report = build_v3_golden_baseline_readiness_audit_report()

    assert report["schema_version"] == "v3.golden_baseline_readiness_audit.1"
    assert report["summary"]["total_candidate_count_from_phase_5"] == 2070
    assert report["summary"]["recommended_pilot_candidate_count"] == 10


def test_v3_golden_baseline_readiness_has_required_top_level_keys():
    report = build_v3_golden_baseline_readiness_audit_report()

    for key in (
        "summary",
        "baseline_readiness_entry_fields",
        "allowed_baseline_readiness_states",
        "candidate_readiness_distribution",
        "recommended_pilot_candidates_reviewed",
        "excluded_candidate_readiness_entries",
        "baseline_case_type_requirements",
        "baseline_evidence_requirements",
        "missing_evidence_summary",
        "dependency_blockers",
        "repeat_validation_policy",
        "proposed_future_fixture_schema",
        "excluded_baseline_categories",
        "production_remap_blockers",
        "safety_confirmations",
        "recommended_next_phase",
    ):
        assert key in report


def test_v3_golden_baseline_readiness_entries_include_required_fields():
    report = build_v3_golden_baseline_readiness_audit_report()

    entries = report["recommended_pilot_candidates_reviewed"] + report["excluded_candidate_readiness_entries"]
    assert entries
    for entry in entries:
        assert set(BASELINE_READINESS_ENTRY_FIELDS).issubset(set(entry))


def test_v3_golden_baseline_readiness_states_are_allowed():
    report = build_v3_golden_baseline_readiness_audit_report()

    entries = report["recommended_pilot_candidates_reviewed"] + report["excluded_candidate_readiness_entries"]
    states = {entry["baseline_readiness_state"] for entry in entries}
    states.update(report["candidate_readiness_distribution"])
    assert states.issubset(ALLOWED_BASELINE_READINESS_STATES)


def test_v3_golden_baseline_readiness_never_allows_promotion_or_baseline_creation():
    report = build_v3_golden_baseline_readiness_audit_report()

    entries = report["recommended_pilot_candidates_reviewed"] + report["excluded_candidate_readiness_entries"]
    assert all(entry["promotion_allowed"] is False for entry in entries)
    assert all(entry["baseline_creation_allowed"] is False for entry in entries)


def test_v3_golden_baseline_readiness_preserves_no_planner_or_stable_promotion():
    report = build_v3_golden_baseline_readiness_audit_report()
    safety = report["safety_confirmations"]

    assert safety["planner_calculable_promoted"] is False
    assert safety["stable_calculable_promoted"] is False
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0


def test_v3_golden_baseline_readiness_preserves_non_consumption_and_audit_only_status():
    report = build_v3_golden_baseline_readiness_audit_report()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_planner_changed"] is False
    assert safety["values_normalized"] is False
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v3_golden_baseline_readiness_has_safety_confirmations():
    report = build_v3_golden_baseline_readiness_audit_report()
    safety = report["safety_confirmations"]

    for key in (
        "golden_baselines_created",
        "stat_identities_promoted",
        "canonical_candidates_promoted",
        "stat_calculations_changed",
        "values_normalized",
        "operation_semantics_implemented",
        "planner_calculable_promoted",
        "stable_calculable_promoted",
        "production_consumed",
        "unresolved_stat_identities_blocked",
        "ambiguous_mappings_blocked",
    ):
        assert key in safety


def test_v3_golden_baseline_readiness_exposes_case_types_and_fixture_schema():
    report = build_v3_golden_baseline_readiness_audit_report()

    assert "single_modifier_flat_stat" in report["baseline_case_type_requirements"]
    assert "unsupported_behavior_exclusion" in report["baseline_case_type_requirements"]
    assert "baseline_id" in report["proposed_future_fixture_schema"]["fields"]
    assert "expected_final_stat_delta" in report["proposed_future_fixture_schema"]["fields"]


def test_v3_golden_baseline_readiness_recommended_next_phase_exists():
    report = build_v3_golden_baseline_readiness_audit_report()

    assert report["recommended_next_phase"] == "v3_skill_identity_bridge_policy"
    assert report["recommended_pilot_candidates_reviewed"]
