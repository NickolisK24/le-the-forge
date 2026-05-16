from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_evaluator import evaluate_orchestration_policy_compatibility
from app.runtime_orchestration.orchestration_policy_explainability import (
    explain_orchestration_policy_evaluation,
    export_orchestration_policy_explainability_result,
    hash_orchestration_policy_explainability_result,
    serialize_orchestration_policy_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_models import (
    POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    POLICY_EXPLAINABILITY_STABLE,
    POLICY_REQUIRES_MANUAL_REVIEW,
    POLICY_SUPPORTED,
    OrchestrationPolicyEvaluationInput,
)
from app.runtime_orchestration.orchestration_policy_registry import (
    build_orchestration_policy_registry,
    default_orchestration_policy_registry,
)


def _registry():
    return default_orchestration_policy_registry()


def _explain(registry=None, evaluation=None):
    source_registry = registry or _registry()
    source_evaluation = evaluation or evaluate_orchestration_policy_compatibility(
        OrchestrationPolicyEvaluationInput(registry=source_registry)
    )
    return explain_orchestration_policy_evaluation(source_registry, source_evaluation)


def _export(result=None):
    return export_orchestration_policy_explainability_result(result or _explain())


def test_explainability_generates_stable_policy_visibility():
    result = _export()

    assert result["explainability_status"] == POLICY_EXPLAINABILITY_STABLE
    assert result["supported_explanation_count"] == 4
    assert result["prohibited_explanation_count"] == 3
    assert result["unsupported_explanation_count"] == 1
    assert result["blocked_explanation_count"] == 4
    assert result["dependency_chain_visibility_count"] > 0
    assert result["governance_chain_visibility_count"] > 0
    assert result["provenance_visibility_count"] > 0
    assert result["integrity_visibility_count"] == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["policy_execution_enabled"] is False


def test_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_policy_explainability_result(first) == serialize_orchestration_policy_explainability_result(second)
    assert hash_orchestration_policy_explainability_result(first) == hash_orchestration_policy_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_supported_policy_explains_why_it_is_supported():
    result = _export()
    modeling = next(record for record in result["explanation_records"] if record["policy_id"] == "v3_6.policy.modeling.allowed")

    assert modeling["support_state"] == POLICY_SUPPORTED
    assert "policy modeling is declarative" in modeling["why_supported"]
    assert modeling["why_blocked"] == []
    assert any(entry.startswith("planning_only=True") for entry in modeling["governance_chain_visibility"])


def test_prohibited_policy_explains_why_it_is_blocked_and_prohibited():
    result = _export()
    execution = next(record for record in result["explanation_records"] if record["policy_id"] == "v3_6.policy.execution.prohibited")

    assert "orchestration execution is prohibited in v3.6" in execution["why_prohibited"]
    assert any("policy_blocked_by_prohibition" in entry for entry in execution["why_blocked"])
    assert "v3_6.policy.execution.prohibited.replay" in execution["provenance_visibility"]
    assert execution["continuity_gap_visibility"] == []


def test_unsupported_policy_explains_unsupported_state():
    result = _export()
    autonomy = next(record for record in result["explanation_records"] if record["policy_id"] == "v3_6.policy.autonomy.unsupported")

    assert "autonomous orchestration is unsupported" in autonomy["why_unsupported"]
    assert any("policy_blocked_by_unsupported_state" in entry for entry in autonomy["blocker_visibility"])


def test_dependency_and_integrity_visibility_are_exposed():
    result = _export()
    integrity = next(record for record in result["explanation_records"] if record["policy_id"] == "v3_6.policy.integrity.allowed")

    assert "v3_6.policy.explainability.allowed" in integrity["dependency_chain_visibility"]
    assert "v3_6.policy.modeling.allowed" in integrity["dependency_chain_visibility"]
    assert "v3_6_policy_integrity_integrity" in integrity["integrity_visibility"]
    assert any("v3_6_governance_first_policy_intelligence" == entry for entry in integrity["provenance_visibility"])


def test_explainability_gap_is_fail_visible_for_unexplained_policy_state():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    changed = replace(target, support_state=POLICY_REQUIRES_MANUAL_REVIEW, manual_review_reasons=())
    changed_registry = build_orchestration_policy_registry(
        tuple(changed if policy.identifier.policy_id == target.identifier.policy_id else policy for policy in registry.policies)
    )
    evaluation = evaluate_orchestration_policy_compatibility(OrchestrationPolicyEvaluationInput(registry=changed_registry))
    result = _export(_explain(changed_registry, evaluation))
    changed_record = next(record for record in result["explanation_records"] if record["policy_id"] == target.identifier.policy_id)

    assert result["explainability_status"] == POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert changed_record["explanation_status"] == POLICY_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
