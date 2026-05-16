from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_evaluator import (
    evaluate_orchestration_policy_compatibility,
    export_orchestration_policy_evaluation_result,
    hash_orchestration_policy_evaluation_result,
    serialize_orchestration_policy_evaluation_result,
)
from app.runtime_orchestration.orchestration_policy_models import (
    POLICY_BLOCKED_BY_GOVERNANCE_GAP,
    POLICY_BLOCKED_BY_HASH_MISMATCH,
    POLICY_BLOCKED_BY_MISSING_DEPENDENCY,
    POLICY_BLOCKED_BY_PROHIBITION,
    POLICY_BLOCKED_BY_UNSUPPORTED_STATE,
    POLICY_CONTINUITY_GAP,
    POLICY_CONTINUITY_PRESERVED,
    POLICY_DEPENDENCY_MISSING,
    POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP,
    POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    POLICY_PROHIBITED,
    POLICY_SUPPORTED,
    POLICY_UNSUPPORTED,
    OrchestrationPolicyDependency,
    OrchestrationPolicyEvaluationInput,
    hash_policy_definition,
    hash_policy_registry,
)
from app.runtime_orchestration.orchestration_policy_registry import (
    build_orchestration_policy_registry,
    default_orchestration_policy_registry,
)


def _registry():
    return default_orchestration_policy_registry()


def _evaluate(registry=None, **kwargs):
    return evaluate_orchestration_policy_compatibility(
        OrchestrationPolicyEvaluationInput(registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_policy_evaluation_result(result or _evaluate())


def test_default_evaluation_preserves_visible_policy_blockers_without_execution():
    result = _export()

    assert result["policy_evaluation_status"] == POLICY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS
    assert result["registered_policy_count"] == 8
    assert result["supported_policy_count"] == 4
    assert result["prohibited_policy_count"] == 3
    assert result["unsupported_policy_count"] == 1
    assert result["blocker_count"] == 8
    assert result["dependency_continuity_status"] == POLICY_CONTINUITY_PRESERVED
    assert result["provenance_continuity_status"] == POLICY_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == POLICY_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == POLICY_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == POLICY_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["policy_execution_enabled"] is False


def test_evaluation_serialization_and_hash_are_replay_stable():
    first = _evaluate()
    second = _evaluate()

    assert serialize_orchestration_policy_evaluation_result(first) == serialize_orchestration_policy_evaluation_result(second)
    assert hash_orchestration_policy_evaluation_result(first) == hash_orchestration_policy_evaluation_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_prohibited_and_unsupported_policy_states_remain_fail_visible():
    result = _export()
    blocker_states = {(blocker["policy_id"], blocker["blocker_state"]) for blocker in result["blocker_summary"]}

    assert all(policy_id in result["prohibited_policy_ids"] for policy_id in (
        "v3_6.policy.execution.prohibited",
        "v3_6.policy.routing.prohibited",
        "v3_6.policy.production-runtime.prohibited",
    ))
    assert result["unsupported_policy_ids"] == ["v3_6.policy.autonomy.unsupported"]
    assert ("v3_6.policy.execution.prohibited", POLICY_BLOCKED_BY_PROHIBITION) in blocker_states
    assert ("v3_6.policy.autonomy.unsupported", POLICY_BLOCKED_BY_UNSUPPORTED_STATE) in blocker_states


def test_missing_dependency_blocks_supported_policy_with_visible_dependency_gap():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.integrity.allowed")
    missing_dependency = OrchestrationPolicyDependency(
        dependency_id="missing-policy-dependency",
        required_policy_id="v3_6.policy.missing.required",
        required_support_states=(POLICY_SUPPORTED,),
        continuity_reference_id="missing-policy-dependency.continuity",
    )
    changed = replace(target, dependencies=target.dependencies + (missing_dependency,))
    changed_registry = build_orchestration_policy_registry(
        tuple(changed if policy.identifier.policy_id == target.identifier.policy_id else policy for policy in registry.policies)
    )
    result = _export(_evaluate(changed_registry))
    integrity_record = next(record for record in result["policy_records"] if record["policy_id"] == "v3_6.policy.integrity.allowed")

    assert result["policy_evaluation_status"] == POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP
    assert result["dependency_continuity_status"] == POLICY_CONTINUITY_GAP
    assert integrity_record["dependency_state"] == POLICY_DEPENDENCY_MISSING
    assert any(blocker["blocker_state"] == POLICY_BLOCKED_BY_MISSING_DEPENDENCY for blocker in integrity_record["blockers"])


def test_governance_continuity_gap_blocks_policy_intelligence():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    metadata = dict(target.governance_metadata)
    metadata["execution_enabled"] = True
    changed = replace(target, governance_metadata=metadata)
    changed_registry = build_orchestration_policy_registry(
        tuple(changed if policy.identifier.policy_id == target.identifier.policy_id else policy for policy in registry.policies)
    )
    result = _export(_evaluate(changed_registry))

    assert result["policy_evaluation_status"] == POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == POLICY_CONTINUITY_GAP
    assert any(blocker["blocker_state"] == POLICY_BLOCKED_BY_GOVERNANCE_GAP for blocker in result["blocker_summary"])


def test_registry_and_policy_hash_mismatches_are_deterministic_blockers():
    registry = _registry()
    target = next(policy for policy in registry.policies if policy.identifier.policy_id == "v3_6.policy.modeling.allowed")
    result = _export(
        _evaluate(
            registry,
            expected_registry_hash="mismatched-registry-hash",
            expected_policy_hashes={target.identifier.policy_id: "mismatched-policy-hash"},
        )
    )

    assert result["policy_evaluation_status"] == POLICY_EVALUATION_BLOCKED_BY_POLICY_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_policy_registry(registry)
    assert any(blocker["blocker_state"] == POLICY_BLOCKED_BY_HASH_MISMATCH for blocker in result["blocker_summary"])
    assert target.identifier.policy_id in result["supported_policy_ids"]
    assert hash_policy_definition(target) != "mismatched-policy-hash"


def test_support_state_counts_are_derived_from_policy_registry():
    result = _export()

    records = result["policy_records"]
    assert sum(1 for record in records if record["support_state"] == POLICY_SUPPORTED) == result["supported_policy_count"]
    assert sum(1 for record in records if record["support_state"] == POLICY_PROHIBITED) == result["prohibited_policy_count"]
    assert sum(1 for record in records if record["support_state"] == POLICY_UNSUPPORTED) == result["unsupported_policy_count"]
