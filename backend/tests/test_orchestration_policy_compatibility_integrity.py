from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_compatibility_evaluator import evaluate_orchestration_policy_compatibility_matrix
from app.runtime_orchestration.orchestration_policy_compatibility_explainability import explain_orchestration_policy_compatibility
from app.runtime_orchestration.orchestration_policy_compatibility_integrity import (
    audit_orchestration_policy_compatibility_integrity,
    export_orchestration_policy_compatibility_integrity_result,
    hash_orchestration_policy_compatibility_integrity_result,
    serialize_orchestration_policy_compatibility_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_models import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_DEPENDENCY_BLOCKED,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP,
    COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_INTEGRITY_STABLE,
    OrchestrationPolicyCompatibilityEvaluationInput,
    OrchestrationPolicyCompatibilityIntegrityInput,
    hash_compatibility_registry,
)
from app.runtime_orchestration.orchestration_policy_compatibility_registry import (
    build_orchestration_policy_compatibility_registry,
    default_orchestration_policy_compatibility_registry,
)
from scripts.report_v3_6_orchestration_policy_compatibility import build_v3_6_orchestration_policy_compatibility_report


def _registry():
    return default_orchestration_policy_compatibility_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    evaluation = evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=source_registry)
    )
    explainability = explain_orchestration_policy_compatibility(source_registry, evaluation)
    return OrchestrationPolicyCompatibilityIntegrityInput(
        compatibility_registry=source_registry,
        evaluation_result=evaluation,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_policy_compatibility_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_policy_compatibility_integrity_result(_audit(source))


def _replace_relationship(registry, relationship_id, replacement):
    return build_orchestration_policy_compatibility_registry(
        tuple(
            replacement if relationship.identifier.relationship_id == relationship_id else relationship
            for relationship in registry.relationships
        )
    )


def test_compatibility_integrity_is_stable_with_visible_blocker_chains():
    result = _export()

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["blocker_chain_integrity"]["references"]) == 10
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["compatibility_execution_enabled"] is False


def test_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_policy_compatibility_integrity_result(first) == serialize_orchestration_policy_compatibility_integrity_result(second)
    assert hash_orchestration_policy_compatibility_integrity_result(first) == hash_orchestration_policy_compatibility_integrity_result(second)
    assert json.dumps(export_orchestration_policy_compatibility_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_policy_compatibility_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-compatibility-registry-hash")
    result = _export(source)

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_compatibility_registry(source.compatibility_registry)]
    assert "compatibility_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_relationship(registry, target.identifier.relationship_id, changed)))

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.compat.modeling-governance.compatible:replay_provenance_gap" in result["failure_classification_summary"]


def test_dependency_conflict_visibility_gap_is_integrity_failure():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.integrity-execution.dependency-blocked")
    changed = replace(target, dependency_conflicts=())
    result = _export(_integrity_input(_replace_relationship(registry, target.identifier.relationship_id, changed)))

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert "v3_6.compat.integrity-execution.dependency-blocked:missing_dependency_conflict_visibility" in result["failure_classification_summary"]


def test_governance_conflict_visibility_gap_is_integrity_failure():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.governance-production-runtime.governance-blocked")
    changed = replace(target, governance_conflicts=())
    result = _export(_integrity_input(_replace_relationship(registry, target.identifier.relationship_id, changed)))

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.compat.governance-production-runtime.governance-blocked:missing_governance_conflict_visibility" in result["failure_classification_summary"]


def test_explainability_gap_is_integrity_failure():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(
        target,
        compatibility_state=COMPATIBILITY_COMPATIBLE,
        support_rationale=(),
        blocker_reasons=(),
        blocker_chains=(),
    )
    isolated_registry = build_orchestration_policy_compatibility_registry((changed,))
    result = _export(_integrity_input(isolated_registry))

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    assert "compatibility_explainability_status:compatibility_explainability_blocked_by_visibility_gap" in result["failure_classification_summary"]


def test_evaluation_and_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_evaluation_hash="mismatched-compatibility-evaluation-hash",
        expected_explainability_hash="mismatched-compatibility-explainability-hash",
    )
    result = _export(source)

    assert result["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "compatibility_evaluation_hash_mismatch" in result["failure_classification_summary"]
    assert "compatibility_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_compatibility_report_summarizes_deterministic_matrix_totals():
    first = build_v3_6_orchestration_policy_compatibility_report()
    second = build_v3_6_orchestration_policy_compatibility_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_compatibility_relationships"] == 13
    assert first["compatible_relationship_count"] == 5
    assert first["incompatible_relationship_count"] == 1
    assert first["prohibited_relationship_count"] == 3
    assert first["unsupported_relationship_count"] == 2
    assert first["dependency_conflict_count"] == 1
    assert first["governance_conflict_count"] == 1
    assert first["blocker_chain_count"] == 8
    assert first["compatibility_integrity_status"] == COMPATIBILITY_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
