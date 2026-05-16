from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_preflight_evaluator import evaluate_orchestration_preflight
from app.runtime_orchestration.orchestration_preflight_explainability import explain_orchestration_preflight
from app.runtime_orchestration.orchestration_preflight_integrity import (
    audit_orchestration_preflight_integrity,
    export_orchestration_preflight_integrity_result,
    hash_orchestration_preflight_integrity_result,
    serialize_orchestration_preflight_integrity_result,
)
from app.runtime_orchestration.orchestration_preflight_models import (
    PREFLIGHT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    PREFLIGHT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    PREFLIGHT_INTEGRITY_STABLE,
    OrchestrationPreflightEvaluationInput,
    OrchestrationPreflightIntegrityInput,
    hash_preflight_registry,
)
from app.runtime_orchestration.orchestration_preflight_registry import (
    build_orchestration_preflight_registry,
    default_orchestration_preflight_registry,
)
from scripts.report_v3_6_orchestration_preflight_evaluation import build_v3_6_orchestration_preflight_report


def _registry():
    return default_orchestration_preflight_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    evaluation = evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=source_registry)
    )
    explainability = explain_orchestration_preflight(source_registry, evaluation)
    return OrchestrationPreflightIntegrityInput(
        preflight_registry=source_registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_preflight_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_preflight_integrity_result(_audit(source))


def _record(registry, preflight_id):
    return next(record for record in registry.records if record.identifier.preflight_id == preflight_id)


def _replace_record(registry, preflight_id, replacement):
    return build_orchestration_preflight_registry(
        tuple(
            replacement if record.identifier.preflight_id == preflight_id else record
            for record in registry.records
        )
    )


def test_preflight_integrity_is_stable_with_visible_domains():
    result = _export()

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["governance_integrity"]["references"]) == 9
    assert len(result["policy_integrity"]["references"]) == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["preflight_execution_enabled"] is False


def test_preflight_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_preflight_integrity_result(first) == serialize_orchestration_preflight_integrity_result(second)
    assert hash_orchestration_preflight_integrity_result(first) == hash_orchestration_preflight_integrity_result(second)
    assert json.dumps(export_orchestration_preflight_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_preflight_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-preflight-registry-hash")
    result = _export(source)

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_preflight_registry(source.preflight_registry)]
    assert "preflight_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_record(registry, target.identifier.preflight_id, changed)))

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.preflight.compatibility-check:replay_provenance_gap" in result["failure_classification_summary"]


def test_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_evaluation_hash="mismatched-preflight-evaluation-hash",
        expected_explainability_hash="mismatched-preflight-explainability-hash",
    )
    result = _export(source)

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "preflight_evaluation_hash_mismatch" in result["failure_classification_summary"]
    assert "preflight_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_explainability_visibility_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.informational")
    changed = replace(target, preflight_rationale=())
    result = _export(_integrity_input(_replace_record(registry, target.identifier.preflight_id, changed)))

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    assert "preflight_explainability_status:preflight_explainability_blocked_by_visibility_gap" in result["failure_classification_summary"]


def test_governance_boundary_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_integrity_input(_replace_record(registry, target.identifier.preflight_id, changed)))

    assert result["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.preflight.orchestration-simulation:governance_boundary_gap" in result["failure_classification_summary"]


def test_preflight_domain_and_policy_gaps_fail_integrity():
    registry = _registry()
    compatibility = _record(registry, "v3_6.preflight.policy-boundary")
    dependency = _record(registry, "v3_6.preflight.dependency-analysis")
    blocker = _record(registry, "v3_6.preflight.prohibited-domain")
    supported = _record(registry, "v3_6.preflight.informational")
    policy = _record(registry, "v3_6.preflight.compatibility-check")

    assert _export(_integrity_input(_replace_record(registry, compatibility.identifier.preflight_id, replace(compatibility, compatibility_domains=()))))[
        "preflight_integrity_status"
    ] == PREFLIGHT_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    assert _export(_integrity_input(_replace_record(registry, dependency.identifier.preflight_id, replace(dependency, dependency_domains=()))))[
        "preflight_integrity_status"
    ] == PREFLIGHT_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert _export(_integrity_input(_replace_record(registry, blocker.identifier.preflight_id, replace(blocker, blocker_domains=()))))[
        "preflight_integrity_status"
    ] == PREFLIGHT_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    assert _export(_integrity_input(_replace_record(registry, supported.identifier.preflight_id, replace(supported, supported_domains=()))))[
        "preflight_integrity_status"
    ] == PREFLIGHT_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    assert _export(_integrity_input(_replace_record(registry, policy.identifier.preflight_id, replace(policy, policy_ids=()))))[
        "preflight_integrity_status"
    ] == PREFLIGHT_INTEGRITY_BLOCKED_BY_POLICY_GAP


def test_preflight_report_summarizes_deterministic_evaluation_totals():
    first = build_v3_6_orchestration_preflight_report()
    second = build_v3_6_orchestration_preflight_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_preflight_count"] == 9
    assert first["supported_preflight_count"] == 3
    assert first["unsupported_preflight_count"] == 1
    assert first["prohibited_preflight_count"] == 2
    assert first["governance_blocked_count"] == 1
    assert first["compatibility_blocked_count"] == 1
    assert first["dependency_blocked_count"] == 1
    assert first["blocker_domain_count"] == 11
    assert first["preflight_integrity_status"] == PREFLIGHT_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
