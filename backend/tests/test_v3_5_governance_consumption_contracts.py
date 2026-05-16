from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration import (
    BLOCKED_COMPATIBILITY_REQUIREMENT,
    BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT,
    BLOCKED_EXECUTION_BEHAVIOR_DETECTED,
    BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT,
    BLOCKED_MISSING_GOVERNANCE_DEPENDENCY,
    BLOCKED_MISSING_ORCHESTRATION_IDENTITY,
    BLOCKED_MISSING_REPLAY_LINEAGE,
    BLOCKED_MISSING_ROLLBACK_LINEAGE,
    BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN,
    BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE,
    GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING,
    default_governance_consumption_contract,
    default_orchestration_boundary_model,
    default_orchestration_visibility_model,
    evaluate_governance_consumption_contract,
    export_orchestration_blockers,
    export_orchestration_boundary,
    export_orchestration_visibility,
    hash_governance_consumption_contract,
    serialize_governance_consumption_result,
)
from scripts.report_v3_5_governance_consumption_contracts import (
    build_v3_5_governance_consumption_contracts_report,
)


def _base_contract():
    return default_governance_consumption_contract()


def _result(contract=None):
    return evaluate_governance_consumption_contract(contract or _base_contract())


def test_deterministic_contract_generation():
    first = _base_contract()
    second = _base_contract()

    assert hash_governance_consumption_contract(first) == hash_governance_consumption_contract(second)
    assert _result(first)["status"] == GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING


def test_replay_safe_output_stability():
    result = _result()

    assert result["guarantees"]["replay_safe_contract_generation"] is True
    assert result["contract"]["replay_lineage_required"] is True
    assert result["contract"]["replay_lineage_id"]


def test_rollback_safe_output_stability():
    result = _result()

    assert result["guarantees"]["rollback_safe_contract_generation"] is True
    assert result["contract"]["rollback_lineage_required"] is True
    assert result["contract"]["rollback_lineage_id"]


def test_unsupported_state_preservation():
    result = _result(replace(_base_contract(), unsupported_orchestration_states=("unsupported_orchestration_scope",)))

    assert result["status"] == BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE
    assert result["blockers"][0]["blocker_id"] == "unsupported_orchestration_state_visible"
    assert "unsupported_orchestration_scope" in result["boundary"]["unsupported_orchestration_states"]


def test_blocker_visibility_preservation():
    blockers = export_orchestration_blockers(_base_contract().blocker_models)

    assert blockers
    assert all(row["fail_visible"] is True for row in blockers)
    assert all(row["audit_safe"] is True for row in blockers)
    assert all(row["explicit"] is True for row in blockers)


def test_prohibited_domain_preservation():
    result = _result(replace(_base_contract(), requested_orchestration_domain="runtime_execution"))

    assert result["status"] == BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN
    assert "runtime_execution" in result["boundary"]["prohibited_orchestration_domains"]


def test_governance_dependency_preservation():
    result = _result()

    assert result["contract"]["governance_dependency_ids"]
    assert result["guarantees"]["governance_chain_explainability"] is True


def test_compatibility_validation():
    result = _result(replace(_base_contract(), compatibility_verified=False))

    assert result["status"] == BLOCKED_COMPATIBILITY_REQUIREMENT
    assert _result()["guarantees"]["compatibility_safe_evolution"] is True


def test_explainable_visibility_preservation():
    visibility = export_orchestration_visibility(default_orchestration_visibility_model())

    assert visibility["orchestration_status_visible"] is True
    assert visibility["unsupported_state_visible"] is True
    assert visibility["governance_dependency_visible"] is True
    assert visibility["authorization_visible"] is True
    assert visibility["replay_lineage_visible"] is True
    assert visibility["rollback_lineage_visible"] is True
    assert visibility["compatibility_visible"] is True
    assert visibility["orchestration_limitation_visible"] is True
    assert visibility["auditability_required"] is True


def test_boundary_model_preserves_allowed_and_prohibited_domains():
    boundary = export_orchestration_boundary(default_orchestration_boundary_model())

    assert "governance_consumption_planning" in boundary["allowed_orchestration_domains"]
    assert "orchestration_execution" in boundary["prohibited_orchestration_domains"]
    assert boundary["deterministic_fail_visible_blockers"] is True


def test_missing_orchestration_identity_blocked():
    assert _result(replace(_base_contract(), orchestration_request_id=""))["status"] == BLOCKED_MISSING_ORCHESTRATION_IDENTITY


def test_missing_authorization_blocked():
    assert _result(replace(_base_contract(), authorization_state="missing"))["status"] == BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT


def test_missing_governance_dependency_blocked():
    assert _result(replace(_base_contract(), governance_dependency_ids=()))["status"] == BLOCKED_MISSING_GOVERNANCE_DEPENDENCY


def test_missing_replay_lineage_blocked():
    assert _result(replace(_base_contract(), replay_lineage_id=""))["status"] == BLOCKED_MISSING_REPLAY_LINEAGE


def test_missing_rollback_lineage_blocked():
    assert _result(replace(_base_contract(), rollback_lineage_id=""))["status"] == BLOCKED_MISSING_ROLLBACK_LINEAGE


def test_environment_isolation_blocked():
    assert _result(replace(_base_contract(), environment_isolated=False))["status"] == BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT


def test_execution_behavior_detected_blocked():
    assert _result(replace(_base_contract(), orchestration_execution_enabled=True))["status"] == BLOCKED_EXECUTION_BEHAVIOR_DETECTED


def test_deterministic_result_serialization():
    first = _result()
    second = _result()

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert serialize_governance_consumption_result(first) == serialize_governance_consumption_result(second)


def test_no_execution_behavior_exists():
    result = _result()

    assert result["execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["prohibitions"]["runtime_execution_enabled"] is False
    assert result["prohibitions"]["orchestration_execution_enabled"] is False


def test_no_production_routing_or_mutation_behavior_exists():
    prohibitions = _result()["prohibitions"]

    assert prohibitions["production_routing_enabled"] is False
    assert prohibitions["persistent_mutation_enabled"] is False
    assert prohibitions["state_writes_enabled"] is False
    assert prohibitions["audit_log_writes_enabled"] is False
    assert prohibitions["external_side_effects_enabled"] is False
    assert prohibitions["production_authoritative_manifests_enabled"] is False
    assert prohibitions["production_runtime_consumption_enabled"] is False
    assert prohibitions["experiment_execution_enabled"] is False


def test_report_covers_statuses_and_is_stable():
    first = build_v3_5_governance_consumption_contracts_report()
    second = build_v3_5_governance_consumption_contracts_report()
    distribution = first["status_distribution"]

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert distribution[GOVERNANCE_CONSUMPTION_READY_FOR_ORCHESTRATION_PLANNING] == 1
    assert distribution[BLOCKED_MISSING_ORCHESTRATION_IDENTITY] == 1
    assert distribution[BLOCKED_MISSING_AUTHORIZATION_REQUIREMENT] == 1
    assert distribution[BLOCKED_MISSING_GOVERNANCE_DEPENDENCY] == 1
    assert distribution[BLOCKED_MISSING_REPLAY_LINEAGE] == 1
    assert distribution[BLOCKED_MISSING_ROLLBACK_LINEAGE] == 1
    assert distribution[BLOCKED_COMPATIBILITY_REQUIREMENT] == 1
    assert distribution[BLOCKED_UNSUPPORTED_ORCHESTRATION_STATE] == 1
    assert distribution[BLOCKED_PROHIBITED_ORCHESTRATION_DOMAIN] == 1
    assert distribution[BLOCKED_ENVIRONMENT_ISOLATION_REQUIREMENT] == 1
    assert distribution[BLOCKED_EXECUTION_BEHAVIOR_DETECTED] == 1
    assert first["runtime_execution_enabled"] is False
    assert first["orchestration_execution_enabled"] is False
    assert first["production_routing_enabled"] is False
    assert first["persistent_mutation_enabled"] is False
