from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_trace_builder import (
    build_orchestration_evaluation_trace,
    export_orchestration_evaluation_trace_build_result,
    hash_orchestration_evaluation_trace_build_result,
    serialize_orchestration_evaluation_trace_build_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_models import (
    TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP,
    TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS,
    TRACE_CLASSIFIED_AS_COMPATIBILITY_BLOCKED,
    TRACE_CLASSIFIED_AS_DEPENDENCY_BLOCKED,
    TRACE_CLASSIFIED_AS_GOVERNANCE_BLOCKED,
    TRACE_CONTINUITY_GAP,
    TRACE_CONTINUITY_PRESERVED,
    TRACE_GOVERNANCE_BOUNDARY_GAP,
    TRACE_HASH_MISMATCH,
    TRACE_POLICY_GAP,
    TRACE_PROHIBITED_DOMAIN_VISIBLE,
    TRACE_PROVENANCE_GAP,
    TRACE_STEP_GAP,
    TRACE_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationEvaluationTraceBuildInput,
    hash_trace_registry,
)
from app.runtime_orchestration.orchestration_evaluation_trace_registry import (
    build_orchestration_evaluation_trace_registry,
    default_orchestration_evaluation_trace_registry,
)


def _registry():
    return default_orchestration_evaluation_trace_registry()


def _build(registry=None, **kwargs):
    return build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_evaluation_trace_build_result(result or _build())


def _record(registry, trace_id):
    return next(record for record in registry.records if record.identifier.trace_id == trace_id)


def _replace_record(registry, trace_id, replacement):
    return build_orchestration_evaluation_trace_registry(
        tuple(
            replacement if record.identifier.trace_id == trace_id else record
            for record in registry.records
        )
    )


def test_default_trace_build_preserves_visible_reasoning_chains():
    result = _export()

    assert result["trace_build_status"] == TRACE_BUILD_STABLE_WITH_VISIBLE_FINDINGS
    assert result["registered_trace_count"] == 9
    assert result["governance_trace_count"] == 9
    assert result["compatibility_trace_count"] == 8
    assert result["dependency_trace_count"] == 3
    assert result["blocker_trace_count"] == 8
    assert result["unsupported_trace_count"] == 3
    assert result["prohibited_trace_count"] == 3
    assert result["provenance_trace_count"] == 9
    assert result["explainability_trace_count"] == 9
    assert result["integrity_trace_count"] == 9
    assert result["trace_step_count"] == 70
    assert result["reasoning_step_count"] == 70
    assert result["provenance_continuity_status"] == TRACE_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == TRACE_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == TRACE_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == TRACE_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["trace_execution_enabled"] is False


def test_trace_build_serialization_and_hash_are_replay_stable():
    first = _build()
    second = _build()

    assert serialize_orchestration_evaluation_trace_build_result(first) == serialize_orchestration_evaluation_trace_build_result(second)
    assert hash_orchestration_evaluation_trace_build_result(first) == hash_orchestration_evaluation_trace_build_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_blocked_trace_states_are_fail_visible():
    result = _export()
    governance = next(record for record in result["build_records"] if record["trace_id"] == "v3_6.trace.governance-review")
    compatibility = next(record for record in result["build_records"] if record["trace_id"] == "v3_6.trace.policy-boundary")
    dependency = next(record for record in result["build_records"] if record["trace_id"] == "v3_6.trace.dependency-analysis")

    assert any(finding["classification"] == TRACE_CLASSIFIED_AS_GOVERNANCE_BLOCKED for finding in governance["findings"])
    assert any(finding["classification"] == TRACE_CLASSIFIED_AS_COMPATIBILITY_BLOCKED for finding in compatibility["findings"])
    assert any(finding["classification"] == TRACE_CLASSIFIED_AS_DEPENDENCY_BLOCKED for finding in dependency["findings"])


def test_unsupported_and_prohibited_trace_domains_are_fail_visible():
    result = _export()
    unsupported = next(record for record in result["build_records"] if record["trace_id"] == "v3_6.trace.unsupported-domain")
    prohibited = next(record for record in result["build_records"] if record["trace_id"] == "v3_6.trace.prohibited-domain")

    assert unsupported["unsupported_domain_count"] == 2
    assert any(finding["classification"] == TRACE_UNSUPPORTED_DOMAIN_VISIBLE for finding in unsupported["findings"])
    assert prohibited["prohibited_domain_count"] == 3
    assert any(finding["classification"] == TRACE_PROHIBITED_DOMAIN_VISIBLE for finding in prohibited["findings"])


def test_hash_mismatch_and_provenance_gap_are_structural_findings():
    registry = _registry()
    target = _record(registry, "v3_6.trace.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = _replace_record(registry, target.identifier.trace_id, changed)
    result = _export(
        _build(
            changed_registry,
            expected_registry_hash="mismatched-trace-registry-hash",
            expected_trace_hashes={target.identifier.trace_id: "mismatched-trace-hash"},
        )
    )

    assert result["trace_build_status"] == TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == TRACE_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_trace_registry(changed_registry)
    assert any(finding["classification"] == TRACE_HASH_MISMATCH for finding in result["finding_summary"])
    assert any(finding["classification"] == TRACE_PROVENANCE_GAP for finding in result["finding_summary"])


def test_governance_boundary_gap_blocks_trace_building():
    registry = _registry()
    target = _record(registry, "v3_6.trace.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_build(_replace_record(registry, target.identifier.trace_id, changed)))

    assert result["trace_build_status"] == TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == TRACE_CONTINUITY_GAP
    assert any(finding["classification"] == TRACE_GOVERNANCE_BOUNDARY_GAP for finding in result["finding_summary"])


def test_policy_and_trace_step_gaps_block_trace_building():
    registry = _registry()
    policy = _record(registry, "v3_6.trace.compatibility-check")
    trace_step = _record(registry, "v3_6.trace.informational")

    policy_result = _export(_build(_replace_record(registry, policy.identifier.trace_id, replace(policy, policy_ids=()))))
    trace_step_result = _export(_build(_replace_record(registry, trace_step.identifier.trace_id, replace(trace_step, trace_steps=()))))

    assert policy_result["trace_build_status"] == TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert any(finding["classification"] == TRACE_POLICY_GAP for finding in policy_result["finding_summary"])
    assert trace_step_result["trace_build_status"] == TRACE_BUILD_BLOCKED_BY_CONTINUITY_GAP
    assert any(finding["classification"] == TRACE_STEP_GAP for finding in trace_step_result["finding_summary"])
