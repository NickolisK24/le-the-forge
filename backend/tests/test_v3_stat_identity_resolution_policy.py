from scripts.report_v3_stat_identity_resolution_policy import (
    CURRENT_IDENTITY_STATES,
    IDENTITY_STATES,
    REQUIRED_POLICY_FIELDS,
    build_v3_stat_identity_resolution_policy_report,
)


def test_v3_stat_identity_policy_report_has_required_top_level_keys():
    report = build_v3_stat_identity_resolution_policy_report()

    assert report["schema_version"] == "v3.stat_identity_resolution_policy.1"
    for key in (
        "current_stat_identity_landscape",
        "identity_classification_summaries",
        "policy_fields",
        "identity_states",
        "current_allowed_identity_states",
        "evidence_requirements",
        "disallowed_assumptions",
        "operation_semantic_dependencies",
        "value_normalization_dependencies",
        "golden_baseline_dependencies",
        "production_remap_blockers",
        "future_sequence",
        "recommended_next_phase",
        "safety_confirmations",
    ):
        assert key in report


def test_v3_stat_identity_policy_fields_are_complete():
    report = build_v3_stat_identity_resolution_policy_report()

    assert set(REQUIRED_POLICY_FIELDS).issubset(set(report["policy_fields"]))


def test_v3_stat_identity_states_are_strict():
    report = build_v3_stat_identity_resolution_policy_report()

    assert set(report["identity_states"]) == IDENTITY_STATES
    states = {item["identity_state"] for item in report["identity_classification_summaries"]}
    states.update(item["identity_state"] for item in report["current_stat_identity_landscape"]["sample_identity_classifications"])
    assert states.issubset(IDENTITY_STATES)
    assert set(report["current_allowed_identity_states"]) == CURRENT_IDENTITY_STATES


def test_v3_stat_identity_policy_does_not_promote_any_identity():
    report = build_v3_stat_identity_resolution_policy_report()

    states = {
        item["promotion_status"]
        for item in report["current_stat_identity_landscape"]["sample_identity_classifications"]
    }
    assert "planner_identity_experimental" not in states
    assert "planner_identity_stable" not in states
    assert all(
        item["planner_identity_safe"] is False
        for item in report["current_stat_identity_landscape"]["sample_identity_classifications"]
    )


def test_v3_stat_identity_policy_preserves_zero_planner_counts():
    report = build_v3_stat_identity_resolution_policy_report()
    safety = report["safety_confirmations"]

    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0
    assert safety["planner_calculable_promoted"] is False
    assert safety["stable_calculable_promoted"] is False


def test_v3_stat_identity_policy_keeps_unresolved_identities_blocked():
    report = build_v3_stat_identity_resolution_policy_report()
    landscape = report["current_stat_identity_landscape"]

    assert landscape["unresolved_stat_identity_count"] == 4714
    assert landscape["modifier_rows_affected_by_unresolved_stat_identity"] == 4714
    assert landscape["classification_counts"]["blocked_by_unknown_stat"] == 1
    assert report["safety_confirmations"]["unresolved_stat_identities_blocked"] is True


def test_v3_stat_identity_policy_preserves_non_consumption_and_audit_only_status():
    report = build_v3_stat_identity_resolution_policy_report()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_planner_changed"] is False
    assert safety["values_normalized"] is False
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v3_stat_identity_policy_has_safety_confirmations():
    report = build_v3_stat_identity_resolution_policy_report()
    safety = report["safety_confirmations"]

    for key in (
        "stat_identities_promoted",
        "stat_calculations_changed",
        "values_normalized",
        "operation_semantics_implemented",
        "planner_calculable_promoted",
        "stable_calculable_promoted",
        "production_consumed",
        "production_planner_changed",
        "unresolved_stat_identities_blocked",
        "value_normalization_status",
        "skill_identity_bridge_status",
    ):
        assert key in safety


def test_v3_stat_identity_policy_recommended_next_phase_is_present():
    report = build_v3_stat_identity_resolution_policy_report()

    assert report["recommended_next_phase"] == "v3_skill_identity_bridge_policy"
    sequence = report["future_sequence"]
    assert sequence
    assert [step["order"] for step in sequence] == sorted(step["order"] for step in sequence)
