from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_compatibility_evaluator import (
    evaluate_orchestration_policy_compatibility_matrix,
    export_orchestration_policy_compatibility_evaluation_result,
    hash_orchestration_policy_compatibility_evaluation_result,
    serialize_orchestration_policy_compatibility_evaluation_result,
)
from app.runtime_orchestration.orchestration_policy_compatibility_models import (
    COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT,
    COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH,
    COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING,
    COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP,
    COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION,
    COMPATIBILITY_COMPATIBLE,
    COMPATIBILITY_CONTINUITY_GAP,
    COMPATIBILITY_CONTINUITY_PRESERVED,
    COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP,
    COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS,
    COMPATIBILITY_PROHIBITED,
    OrchestrationPolicyCompatibilityEvaluationInput,
    hash_compatibility_registry,
)
from app.runtime_orchestration.orchestration_policy_compatibility_registry import (
    build_orchestration_policy_compatibility_registry,
    default_orchestration_policy_compatibility_registry,
)


def _registry():
    return default_orchestration_policy_compatibility_registry()


def _evaluate(registry=None, **kwargs):
    return evaluate_orchestration_policy_compatibility_matrix(
        OrchestrationPolicyCompatibilityEvaluationInput(compatibility_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_policy_compatibility_evaluation_result(result or _evaluate())


def test_default_evaluation_preserves_visible_compatibility_blockers():
    result = _export()

    assert result["compatibility_evaluation_status"] == COMPATIBILITY_EVALUATION_STABLE_WITH_VISIBLE_BLOCKERS
    assert result["registered_relationship_count"] == 13
    assert result["compatible_relationship_count"] == 5
    assert result["incompatible_relationship_count"] == 1
    assert result["prohibited_relationship_count"] == 3
    assert result["unsupported_relationship_count"] == 2
    assert result["dependency_conflict_count"] == 1
    assert result["governance_conflict_count"] == 1
    assert result["blocker_chain_count"] == 8
    assert result["provenance_continuity_status"] == COMPATIBILITY_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == COMPATIBILITY_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == COMPATIBILITY_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == COMPATIBILITY_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["compatibility_execution_enabled"] is False


def test_evaluation_serialization_and_hash_are_replay_stable():
    first = _evaluate()
    second = _evaluate()

    assert serialize_orchestration_policy_compatibility_evaluation_result(first) == serialize_orchestration_policy_compatibility_evaluation_result(second)
    assert hash_orchestration_policy_compatibility_evaluation_result(first) == hash_orchestration_policy_compatibility_evaluation_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_prohibited_and_unsupported_relationships_remain_fail_visible():
    result = _export()
    blocker_states = {(blocker["relationship_id"], blocker["blocker_state"]) for blocker in result["blocker_summary"]}

    assert ("v3_6.compat.execution-routing.prohibited", COMPATIBILITY_BLOCKED_BY_PROHIBITED_PAIRING) in blocker_states
    assert ("v3_6.compat.autonomy-routing.unsupported", COMPATIBILITY_BLOCKED_BY_UNSUPPORTED_COMBINATION) in blocker_states


def test_dependency_and_governance_conflicts_remain_visible():
    result = _export()
    dependency = next(record for record in result["relationship_records"] if record["relationship_id"] == "v3_6.compat.integrity-execution.dependency-blocked")
    governance = next(record for record in result["relationship_records"] if record["relationship_id"] == "v3_6.compat.governance-production-runtime.governance-blocked")

    assert dependency["dependency_conflict_count"] == 1
    assert any(blocker["blocker_state"] == "compatibility_blocked_by_dependency_conflict" for blocker in dependency["blockers"])
    assert governance["governance_conflict_count"] == 1
    assert any(blocker["blocker_state"] == COMPATIBILITY_BLOCKED_BY_GOVERNANCE_CONFLICT for blocker in governance["blockers"])


def test_multi_policy_compatibility_analysis_is_deterministic():
    compatible = _export(
        _evaluate(
            selected_policy_ids=(
                "v3_6.policy.modeling.allowed",
                "v3_6.policy.governance-boundary.allowed",
                "v3_6.policy.explainability.allowed",
            )
        )
    )
    prohibited = _export(
        _evaluate(
            selected_policy_ids=(
                "v3_6.policy.execution.prohibited",
                "v3_6.policy.routing.prohibited",
                "v3_6.policy.production-runtime.prohibited",
            )
        )
    )

    assert compatible["multi_policy_compatibility_state"] == COMPATIBILITY_COMPATIBLE
    assert prohibited["multi_policy_compatibility_state"] == COMPATIBILITY_PROHIBITED


def test_hash_mismatch_and_provenance_gap_are_structural_blockers():
    registry = _registry()
    target = next(relationship for relationship in registry.relationships if relationship.identifier.relationship_id == "v3_6.compat.modeling-governance.compatible")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = build_orchestration_policy_compatibility_registry(
        tuple(changed if relationship.identifier.relationship_id == target.identifier.relationship_id else relationship for relationship in registry.relationships)
    )
    result = _export(
        _evaluate(
            changed_registry,
            expected_registry_hash="mismatched-compatibility-registry-hash",
            expected_relationship_hashes={target.identifier.relationship_id: "mismatched-relationship-hash"},
        )
    )

    assert result["compatibility_evaluation_status"] == COMPATIBILITY_EVALUATION_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == COMPATIBILITY_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_compatibility_registry(changed_registry)
    assert any(blocker["blocker_state"] == COMPATIBILITY_BLOCKED_BY_HASH_MISMATCH for blocker in result["blocker_summary"])
    assert any(blocker["blocker_state"] == COMPATIBILITY_BLOCKED_BY_PROVENANCE_GAP for blocker in result["blocker_summary"])
