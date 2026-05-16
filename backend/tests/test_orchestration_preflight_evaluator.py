from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_preflight_evaluator import (
    evaluate_orchestration_preflight,
    export_orchestration_preflight_evaluation_result,
    hash_orchestration_preflight_evaluation_result,
    serialize_orchestration_preflight_evaluation_result,
)
from app.runtime_orchestration.orchestration_preflight_models import (
    PREFLIGHT_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    PREFLIGHT_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    PREFLIGHT_CONTINUITY_GAP,
    PREFLIGHT_CONTINUITY_PRESERVED,
    PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP,
    PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS,
    PREFLIGHT_GOVERNANCE_BOUNDARY_GAP,
    PREFLIGHT_HASH_MISMATCH,
    PREFLIGHT_PROHIBITED_DOMAIN_VISIBLE,
    PREFLIGHT_PROVENANCE_GAP,
    PREFLIGHT_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationPreflightEvaluationInput,
    hash_preflight_registry,
)
from app.runtime_orchestration.orchestration_preflight_registry import (
    build_orchestration_preflight_registry,
    default_orchestration_preflight_registry,
)


def _registry():
    return default_orchestration_preflight_registry()


def _evaluate(registry=None, **kwargs):
    return evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_preflight_evaluation_result(result or _evaluate())


def _record(registry, preflight_id):
    return next(record for record in registry.records if record.identifier.preflight_id == preflight_id)


def _replace_record(registry, preflight_id, replacement):
    return build_orchestration_preflight_registry(
        tuple(
            replacement if record.identifier.preflight_id == preflight_id else record
            for record in registry.records
        )
    )


def test_default_preflight_evaluation_preserves_visible_domains():
    result = _export()

    assert result["preflight_evaluation_status"] == PREFLIGHT_EVALUATION_STABLE_WITH_VISIBLE_FINDINGS
    assert result["registered_preflight_count"] == 9
    assert result["supported_preflight_count"] == 3
    assert result["unsupported_preflight_count"] == 1
    assert result["prohibited_preflight_count"] == 2
    assert result["governance_blocked_count"] == 1
    assert result["compatibility_blocked_count"] == 1
    assert result["dependency_blocked_count"] == 1
    assert result["policy_count"] == 8
    assert result["governance_boundary_count"] == 11
    assert result["compatibility_domain_count"] == 10
    assert result["dependency_domain_count"] == 5
    assert result["blocker_domain_count"] == 11
    assert result["provenance_continuity_status"] == PREFLIGHT_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == PREFLIGHT_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == PREFLIGHT_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == PREFLIGHT_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["preflight_execution_enabled"] is False


def test_preflight_evaluation_serialization_and_hash_are_replay_stable():
    first = _evaluate()
    second = _evaluate()

    assert serialize_orchestration_preflight_evaluation_result(first) == serialize_orchestration_preflight_evaluation_result(second)
    assert hash_orchestration_preflight_evaluation_result(first) == hash_orchestration_preflight_evaluation_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_blocked_preflight_states_are_fail_visible():
    result = _export()
    governance = next(record for record in result["evaluation_records"] if record["preflight_id"] == "v3_6.preflight.governance-review")
    compatibility = next(record for record in result["evaluation_records"] if record["preflight_id"] == "v3_6.preflight.policy-boundary")
    dependency = next(record for record in result["evaluation_records"] if record["preflight_id"] == "v3_6.preflight.dependency-analysis")

    assert any(finding["classification"] == PREFLIGHT_CLASSIFIED_AS_GOVERNANCE_BLOCKED for finding in governance["findings"])
    assert any(finding["classification"] == PREFLIGHT_CLASSIFIED_AS_COMPATIBILITY_BLOCKED for finding in compatibility["findings"])
    assert any(finding["classification"] == PREFLIGHT_CLASSIFIED_AS_DEPENDENCY_BLOCKED for finding in dependency["findings"])


def test_unsupported_and_prohibited_preflight_domains_are_fail_visible():
    result = _export()
    unsupported = next(record for record in result["evaluation_records"] if record["preflight_id"] == "v3_6.preflight.unsupported-domain")
    prohibited = next(record for record in result["evaluation_records"] if record["preflight_id"] == "v3_6.preflight.prohibited-domain")

    assert unsupported["unsupported_domain_count"] == 2
    assert any(finding["classification"] == PREFLIGHT_UNSUPPORTED_DOMAIN_VISIBLE for finding in unsupported["findings"])
    assert prohibited["prohibited_domain_count"] == 3
    assert any(finding["classification"] == PREFLIGHT_PROHIBITED_DOMAIN_VISIBLE for finding in prohibited["findings"])


def test_hash_mismatch_and_provenance_gap_are_structural_findings():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = _replace_record(registry, target.identifier.preflight_id, changed)
    result = _export(
        _evaluate(
            changed_registry,
            expected_registry_hash="mismatched-preflight-registry-hash",
            expected_preflight_hashes={target.identifier.preflight_id: "mismatched-preflight-hash"},
        )
    )

    assert result["preflight_evaluation_status"] == PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == PREFLIGHT_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_preflight_registry(changed_registry)
    assert any(finding["classification"] == PREFLIGHT_HASH_MISMATCH for finding in result["finding_summary"])
    assert any(finding["classification"] == PREFLIGHT_PROVENANCE_GAP for finding in result["finding_summary"])


def test_governance_boundary_gap_blocks_preflight_evaluation():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_evaluate(_replace_record(registry, target.identifier.preflight_id, changed)))

    assert result["preflight_evaluation_status"] == PREFLIGHT_EVALUATION_BLOCKED_BY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == PREFLIGHT_CONTINUITY_GAP
    assert any(finding["classification"] == PREFLIGHT_GOVERNANCE_BOUNDARY_GAP for finding in result["finding_summary"])
