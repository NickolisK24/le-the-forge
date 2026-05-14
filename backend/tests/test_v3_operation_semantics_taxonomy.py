from scripts.report_v3_operation_semantics_taxonomy import (
    CURRENT_CLASSIFICATIONS,
    PROMOTION_STATES,
    REQUIRED_OPERATION_FAMILIES,
    SEMANTIC_CONTRACT_FIELDS,
    build_v3_operation_semantics_taxonomy_report,
)


def test_v3_operation_taxonomy_has_required_top_level_keys():
    report = build_v3_operation_semantics_taxonomy_report()

    assert report["schema_version"] == "v3.operation_semantics_taxonomy.1"
    for key in (
        "current_operation_distribution",
        "operation_families",
        "known_operation_families",
        "unknown_operation_count",
        "blocked_operation_categories",
        "semantic_contract_fields",
        "required_evidence_before_promotion",
        "dependencies",
        "required_golden_baseline_coverage",
        "allowed_promotion_states",
        "disallowed_assumptions",
        "future_sequence",
        "recommended_next_phase",
        "safety_confirmations",
    ):
        assert key in report


def test_v3_operation_taxonomy_includes_required_operation_families():
    report = build_v3_operation_semantics_taxonomy_report()

    operation_ids = {item["operation_id"] for item in report["operation_families"]}
    assert set(REQUIRED_OPERATION_FAMILIES).issubset(operation_ids)


def test_v3_operation_taxonomy_semantic_fields_are_complete():
    report = build_v3_operation_semantics_taxonomy_report()

    assert set(SEMANTIC_CONTRACT_FIELDS).issubset(set(report["semantic_contract_fields"]))


def test_v3_operation_taxonomy_promotion_states_are_strict():
    report = build_v3_operation_semantics_taxonomy_report()

    assert set(report["allowed_promotion_states"]) == PROMOTION_STATES
    states = {item["promotion_status"] for item in report["operation_families"]}
    assert states.issubset(PROMOTION_STATES)


def test_v3_operation_taxonomy_classifications_are_strict():
    report = build_v3_operation_semantics_taxonomy_report()

    classifications = {item["classification"] for item in report["operation_families"]}
    classifications.update(item["classification"] for item in report["blocked_operation_categories"])
    assert classifications.issubset(CURRENT_CLASSIFICATIONS)


def test_v3_operation_taxonomy_does_not_promote_any_operation_family():
    report = build_v3_operation_semantics_taxonomy_report()

    states = {item["promotion_status"] for item in report["operation_families"]}
    assert "planner_semantics_experimental" not in states
    assert "planner_semantics_stable" not in states
    assert all(item["planner_semantics_safe"] is False for item in report["operation_families"])


def test_v3_operation_taxonomy_keeps_unknown_operations_blocked():
    report = build_v3_operation_semantics_taxonomy_report()

    assert report["unknown_operation_count"] == 11606
    unknown = next(item for item in report["operation_families"] if item["operation_id"] == "unknown")
    assert unknown["classification"] == "blocked_by_unknown_operation"
    assert report["safety_confirmations"]["unknown_operations_blocked"] is True


def test_v3_operation_taxonomy_preserves_safety_state():
    report = build_v3_operation_semantics_taxonomy_report()
    safety = report["safety_confirmations"]

    assert safety["operation_semantics_implemented"] is False
    assert safety["modifier_calculations_changed"] is False
    assert safety["values_normalized"] is False
    assert safety["stable_calculable_count"] == 0
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_promoted"] is False
    assert safety["planner_calculable_promoted"] is False
    assert safety["production_consumed"] is False
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["unresolved_stat_identities_blocked"] is True
    assert safety["unsupported_scripted_behavior_excluded"] is True


def test_v3_operation_taxonomy_recommended_next_phase_is_present():
    report = build_v3_operation_semantics_taxonomy_report()

    assert report["recommended_next_phase"] == "v3_stat_identity_resolution_policy"
    sequence = report["future_sequence"]
    assert sequence
    assert [step["order"] for step in sequence] == sorted(step["order"] for step in sequence)
