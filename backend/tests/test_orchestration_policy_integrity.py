from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_evaluator import evaluate_orchestration_policy_compatibility
from app.runtime_orchestration.orchestration_policy_explainability import explain_orchestration_policy_evaluation
from app.runtime_orchestration.orchestration_policy_integrity import (
    audit_orchestration_policy_integrity,
    export_orchestration_policy_integrity_result,
    hash_orchestration_policy_integrity_result,
    serialize_orchestration_policy_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_models import (
    POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    POLICY_INTEGRITY_STABLE,
    POLICY_REQUIRES_MANUAL_REVIEW,
    POLICY_SUPPORTED,
    OrchestrationPolicyDependency,
    OrchestrationPolicyEvaluationInput,
    OrchestrationPolicyIntegrityInput,
    hash_policy_registry,
)
from app.runtime_orchestration.orchestration_policy_registry import (
    build_orchestration_policy_registry,
    default_orchestration_policy_registry,
)
from scripts.report_v3_6_orchestration_policy_foundation import build_v3_6_orchestration_policy_foundation_report


def _registry():
    return default_orchestration_policy_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    evaluation = evaluate_orchestration_policy_compatibility(OrchestrationPolicyEvaluationInput(registry=source_registry))
    explainability = explain_orchestration_policy_evaluation(source_registry, evaluation)
    return OrchestrationPolicyIntegrityInput(
        registry=source_registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_policy_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_policy_integrity_result(_audit(source))


def _replace_policy(registry, policy_id, replacement):
    return build_orchestration_policy_registry(
        tuple(replacement if policy.identifier.policy_id == policy_id else policy for policy in registry.policies)
    )


def test_policy_integrity_is_stable_with_visible_prohibited_and_unsupported_blockers():
    result = _export()

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["blocker_visibility_integrity"]["references"]) == 4
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["policy_execution_enabled"] is False


def test_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_policy_integrity_result(first) == serialize_orchestration_policy_integrity_result(second)
    assert hash_orchestration_policy_integrity_result(first) == hash_orchestration_policy_integrity_result(second)
    assert json.dumps(export_orchestration_policy_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_policy_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-registry-hash")
    result = _export(source)

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH
    assert result["registry_integrity"]["references"] == [hash_policy_registry(source.registry)]
    assert "registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    changed = replace(
        target,
        provenance=replace(target.provenance, replay_reference_ids=()),
    )
    result = _export(_integrity_input(_replace_policy(registry, target.identifier.policy_id, changed)))

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.policy.modeling.allowed:replay_provenance_gap" in result["failure_classification_summary"]


def test_dependency_gap_is_integrity_failure():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.integrity.allowed")
    changed = replace(
        target,
        dependencies=target.dependencies
        + (
            OrchestrationPolicyDependency(
                dependency_id="missing-policy-dependency",
                required_policy_id="v3_6.policy.missing.required",
                required_support_states=(POLICY_SUPPORTED,),
                continuity_reference_id="missing-policy-dependency.continuity",
            ),
        ),
    )
    result = _export(_integrity_input(_replace_policy(registry, target.identifier.policy_id, changed)))

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert "v3_6.policy.integrity.allowed:policy_dependency_missing" in result["failure_classification_summary"]


def test_governance_gap_is_integrity_failure():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    metadata = dict(target.governance_metadata)
    metadata["routing_enabled"] = True
    changed = replace(target, governance_metadata=metadata)
    result = _export(_integrity_input(_replace_policy(registry, target.identifier.policy_id, changed)))

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "governance_continuity_gap" in result["failure_classification_summary"]


def test_explainability_gap_is_integrity_failure():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    changed = replace(target, support_state=POLICY_REQUIRES_MANUAL_REVIEW, manual_review_reasons=())
    isolated_registry = build_orchestration_policy_registry((changed,))
    result = _export(_integrity_input(isolated_registry))

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    assert "explainability_status:policy_explainability_blocked_by_visibility_gap" in result["failure_classification_summary"]


def test_evaluation_and_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_evaluation_hash="mismatched-evaluation-hash",
        expected_explainability_hash="mismatched-explainability-hash",
    )
    result = _export(source)

    assert result["policy_integrity_status"] == POLICY_INTEGRITY_BLOCKED_BY_HASH_MISMATCH
    assert "evaluation_hash_mismatch" in result["failure_classification_summary"]
    assert "explainability_hash_mismatch" in result["failure_classification_summary"]


def test_foundation_report_summarizes_deterministic_policy_statuses():
    first = build_v3_6_orchestration_policy_foundation_report()
    second = build_v3_6_orchestration_policy_foundation_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_policy_count"] == 8
    assert first["supported_policy_count"] == 4
    assert first["prohibited_policy_count"] == 3
    assert first["unsupported_policy_count"] == 1
    assert first["blocker_count"] == 8
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["policy_integrity_status"] == POLICY_INTEGRITY_STABLE
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
