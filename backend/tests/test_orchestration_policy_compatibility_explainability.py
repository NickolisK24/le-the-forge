from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_compatibility_evaluator import evaluate_orchestration_policy_compatibility_matrix
from app.runtime_orchestration.orchestration_policy_compatibility_explainability import (
    explain_orchestration_policy_compatibility,
    export_orchestration_policy_compatibility_explainability_result,
    hash_orchestration_policy_compatibility_explainability_result,
    serialize_orchestration_policy_compatibility_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_models import (
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    COMPATIBILITY_EXPLAINABILITY_STABLE,
    OrchestrationPolicyCompatibilityEvaluationInput,
)
from app.runtime_orchestration.orchestration_policy_compatibility_registry import (
    build_orchestration_policy_compatibility_registry,
    default_orchestration_policy_compatibility_registry,
)


def _registry():
    return default_orchestration_policy_compatibility_registry()


def _explain(registry=None, evaluation=None):
    source_registry = registry or _registry()
    source_evaluation = evaluation or evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=source_registry)
    )
    return explain_orchestration_policy_compatibility(source_registry, source_evaluation)


def _export(result=None):
    return export_orchestration_policy_compatibility_explainability_result(result or _explain())


def test_explainability_generates_stable_compatibility_visibility():
    result = _export()

    assert result["compatibility_explainability_status"] == COMPATIBILITY_EXPLAINABILITY_STABLE
    assert result["compatible_explanation_count"] == 5
    assert result["incompatible_explanation_count"] == 1
    assert result["prohibited_explanation_count"] == 3
    assert result["unsupported_explanation_count"] == 2
    assert result["dependency_conflict_visibility_count"] == 1
    assert result["governance_conflict_visibility_count"] == 1
    assert result["blocker_chain_visibility_count"] >= 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["compatibility_execution_enabled"] is False


def test_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_policy_compatibility_explainability_result(first) == serialize_orchestration_policy_compatibility_explainability_result(second)
    assert hash_orchestration_policy_compatibility_explainability_result(first) == hash_orchestration_policy_compatibility_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatible_relationship_explains_why_policies_may_coexist():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["relationship_id"] == "v3_6.compat.modeling-governance.compatible")

    assert record["compatibility_state"] == COMPATIBILITY_COMPATIBLE
    assert "policy modeling and governance boundary may coexist as planning-only policy intelligence" in record["why_compatible"]
    assert record["why_prohibited"] == []
    assert "v3_6.compat.modeling-governance.compatible.replay" in record["provenance_visibility"]


def test_prohibited_and_unsupported_relationships_explain_blocker_chains():
    result = _export()
    prohibited = next(item for item in result["explanation_records"] if item["relationship_id"] == "v3_6.compat.execution-routing.prohibited")
    unsupported = next(item for item in result["explanation_records"] if item["relationship_id"] == "v3_6.compat.autonomy-routing.unsupported")

    assert "execution-capable policy and routing-capable policy may not coexist as allowed behavior" in prohibited["why_prohibited"]
    assert any("compatibility_blocked_by_prohibited_pairing" in entry for entry in prohibited["blocker_chain_visibility"])
    assert "autonomous orchestration with routing capability is unsupported and remains blocked" in unsupported["why_unsupported"]
    assert any("compatibility_blocked_by_unsupported_combination" in entry for entry in unsupported["blocker_chain_visibility"])


def test_dependency_and_governance_conflict_chains_are_explainable():
    result = _export()
    dependency = next(item for item in result["explanation_records"] if item["relationship_id"] == "v3_6.compat.integrity-execution.dependency-blocked")
    governance = next(item for item in result["explanation_records"] if item["relationship_id"] == "v3_6.compat.governance-production-runtime.governance-blocked")

    assert any("integrity-requires-non-executing-policy-surface" in entry for entry in dependency["dependency_conflict_chain"])
    assert governance["governance_conflict_chain"] == ["production_runtime_access_conflicts_with_non_production_governance"]
    assert "v3_6.compat.integrity-execution.dependency-blocked.integrity" in dependency["integrity_visibility"]


def test_explainability_gap_is_fail_visible_for_unexplained_relationship():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(target, support_rationale=(), blocker_reasons=(), blocker_chains=())
    changed_registry = build_orchestration_policy_compatibility_registry((changed,))
    evaluation = evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, evaluation))

    assert result["compatibility_explainability_status"] == COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert result["explanation_records"][0]["explanation_status"] == COMPATIBILITY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
