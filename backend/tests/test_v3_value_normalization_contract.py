from scripts.report_v3_value_normalization_contract import (
    CURRENT_CLASSIFICATIONS,
    PROMOTION_STATES,
    REQUIRED_CONTRACT_FIELDS,
    build_v3_value_normalization_contract_report,
)


def test_v3_value_normalization_contract_has_required_top_level_keys():
    report = build_v3_value_normalization_contract_report()

    assert report["schema_version"] == "v3.value_normalization_contract.1"
    for key in (
        "current_value_scale_state",
        "value_family_candidates",
        "blocked_family_counts",
        "required_contract_fields",
        "required_evidence_before_promotion",
        "required_golden_baseline_coverage",
        "allowed_promotion_states",
        "current_family_classifications",
        "disallowed_assumptions",
        "production_remap_blockers",
        "future_sequence",
        "recommended_next_phase",
        "safety_confirmations",
    ):
        assert key in report


def test_v3_value_normalization_contract_fields_are_complete():
    report = build_v3_value_normalization_contract_report()

    assert set(REQUIRED_CONTRACT_FIELDS).issubset(set(report["required_contract_fields"]))


def test_v3_value_normalization_promotion_states_are_strict():
    report = build_v3_value_normalization_contract_report()

    assert set(report["allowed_promotion_states"]) == PROMOTION_STATES
    states = {item["promotion_state"] for item in report["current_family_classifications"]}
    assert states.issubset(PROMOTION_STATES)


def test_v3_value_normalization_current_classifications_are_strict():
    report = build_v3_value_normalization_contract_report()

    classifications = {item["classification"] for item in report["current_family_classifications"]}
    assert classifications.issubset(CURRENT_CLASSIFICATIONS)


def test_v3_value_normalization_does_not_promote_any_family():
    report = build_v3_value_normalization_contract_report()

    states = {item["promotion_state"] for item in report["current_family_classifications"]}
    assert "planner_normalized_experimental" not in states
    assert "planner_normalized_stable" not in states
    assert report["blocked_family_counts"]["safe_family_count"] == 0


def test_v3_value_normalization_remains_audit_only():
    report = build_v3_value_normalization_contract_report()

    state = report["current_value_scale_state"]
    safety = report["safety_confirmations"]
    assert state["value_normalization_status"] == "audit_only"
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["values_normalized"] is False


def test_v3_value_normalization_keeps_unknown_and_source_units_blocked():
    report = build_v3_value_normalization_contract_report()
    state = report["current_value_scale_state"]
    safety = report["safety_confirmations"]

    assert state["unknown_value_scale_count"] == 13150
    assert state["source_units_value_scale_count"] == 6248
    assert safety["unknown_values_blocked"] is True
    assert safety["source_units_values_blocked"] is True


def test_v3_value_normalization_preserves_zero_stable_and_non_consumption():
    report = build_v3_value_normalization_contract_report()
    safety = report["safety_confirmations"]

    assert safety["stable_calculable_count"] == 0
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_promoted"] is False
    assert safety["planner_calculable_promoted"] is False
    assert safety["production_consumed"] is False
    assert safety["production_planner_changed"] is False


def test_v3_value_normalization_recommended_next_phase_is_present():
    report = build_v3_value_normalization_contract_report()

    assert report["recommended_next_phase"] == "v3_operation_semantics_taxonomy"
    sequence = report["future_sequence"]
    assert sequence
    assert [step["order"] for step in sequence] == sorted(step["order"] for step in sequence)
