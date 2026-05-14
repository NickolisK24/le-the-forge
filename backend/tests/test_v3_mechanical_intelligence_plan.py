from scripts.report_v3_mechanical_intelligence_plan import (
    ALLOWED_CLASSIFICATIONS,
    build_v3_mechanical_intelligence_plan,
)


def test_v3_mechanical_intelligence_plan_has_required_top_level_keys():
    report = build_v3_mechanical_intelligence_plan()

    assert report["schema_version"] == "v3.mechanical_intelligence_plan.1"
    for key in (
        "readiness_decision",
        "current_readiness_status",
        "mechanical_blocker_summary",
        "mechanical_domains",
        "required_policy_decisions",
        "required_golden_baselines",
        "required_dry_run_comparison_layers",
        "required_adapter_gates",
        "systems_that_must_remain_blocked",
        "recommended_v3_phase_sequence",
        "production_remap_gate_requirements",
        "safety_confirmations",
    ):
        assert key in report


def test_v3_mechanical_intelligence_plan_readiness_decision_is_planning_only():
    report = build_v3_mechanical_intelligence_plan()
    decision = report["readiness_decision"]

    assert decision["v3_planning_ready"] is True
    assert decision["v3_mechanical_implementation_ready"] is False
    assert decision["production_planner_remap_ready"] is False
    assert decision["recommended_next_phase"] == "v3_value_normalization_contract_design"


def test_v3_mechanical_work_item_classifications_are_strict():
    report = build_v3_mechanical_intelligence_plan()

    classifications = {item["classification"] for item in report["mechanical_domains"]}
    assert classifications.issubset(ALLOWED_CLASSIFICATIONS)


def test_v3_phase_sequence_is_ordered_and_non_empty():
    report = build_v3_mechanical_intelligence_plan()
    sequence = report["recommended_v3_phase_sequence"]

    assert sequence
    assert [step["order"] for step in sequence] == sorted(step["order"] for step in sequence)
    assert sequence[0]["id"] == "v3_value_normalization_contract_design"
    assert sequence[-1]["id"] == "v3_production_remap_after_stable_gates"


def test_v3_plan_has_required_mechanical_domains():
    report = build_v3_mechanical_intelligence_plan()

    domain_ids = {item["id"] for item in report["mechanical_domains"]}
    assert "value_normalization" in domain_ids
    assert "operation_semantics" in domain_ids
    assert "stat_identity_resolution" in domain_ids
    assert "modifier_application_semantics" in domain_ids
    assert "item_affix_stat_output" in domain_ids
    assert "passive_node_stat_output" in domain_ids
    assert "skill_node_stat_output" in domain_ids
    assert "skill_identity_bridge_policy" in domain_ids
    assert "deterministic_stat_resolution_adapter" in domain_ids
    assert "production_planner_remap_gates" in domain_ids


def test_v3_plan_has_production_remap_gates():
    report = build_v3_mechanical_intelligence_plan()
    gates = set(report["production_remap_gate_requirements"])

    assert "value normalization contracts approved" in gates
    assert "operation semantics approved" in gates
    assert "stat identities resolved for target domain" in gates
    assert "skill identity bridge policy approved" in gates
    assert "unsupported/scripted mechanics excluded" in gates
    assert "golden baselines passing" in gates
    assert "old planner versus v3 dry-run comparison passing" in gates
    assert "rollback and debug path exists" in gates


def test_v3_plan_preserves_v2_and_v2_5_safety_statuses():
    report = build_v3_mechanical_intelligence_plan()
    safety = report["safety_confirmations"]

    assert safety["v2_infrastructure_ready"] is True
    assert safety["v2_5_trust_ux_ready"] is True
    assert safety["production_planner_ready"] is False
    assert safety["mechanical_remap_ready"] is False
    assert safety["production_consumed"] is False


def test_v3_plan_preserves_non_calculating_statuses():
    report = build_v3_mechanical_intelligence_plan()
    safety = report["safety_confirmations"]

    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"
    assert safety["value_normalization_promoted"] is False
    assert safety["skill_identity_bridge_added"] is False
    assert safety["runtime_behavior_changed"] is False


def test_v3_plan_keeps_blocked_systems_visible():
    report = build_v3_mechanical_intelligence_plan()

    blocked_ids = {item["id"] for item in report["systems_that_must_remain_blocked"]}
    assert "unknown_value_scales" in blocked_ids
    assert "source_units_without_contracts" in blocked_ids
    assert "unknown_operations" in blocked_ids
    assert "unresolved_stat_identities" in blocked_ids
    assert "unresolved_skill_identities" in blocked_ids
    assert "scripted_text_only_unsupported_mechanics" in blocked_ids
