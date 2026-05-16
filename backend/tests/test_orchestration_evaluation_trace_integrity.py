from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_trace_builder import build_orchestration_evaluation_trace
from app.runtime_orchestration.orchestration_evaluation_trace_explainability import explain_orchestration_evaluation_trace
from app.runtime_orchestration.orchestration_evaluation_trace_integrity import (
    audit_orchestration_evaluation_trace_integrity,
    export_orchestration_evaluation_trace_integrity_result,
    hash_orchestration_evaluation_trace_integrity_result,
    serialize_orchestration_evaluation_trace_integrity_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_models import (
    TRACE_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP,
    TRACE_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    TRACE_INTEGRITY_STABLE,
    OrchestrationEvaluationTraceBuildInput,
    OrchestrationEvaluationTraceIntegrityInput,
    hash_trace_registry,
)
from app.runtime_orchestration.orchestration_evaluation_trace_registry import (
    build_orchestration_evaluation_trace_registry,
    default_orchestration_evaluation_trace_registry,
)
from scripts.report_v3_6_orchestration_evaluation_trace_modeling import build_v3_6_orchestration_evaluation_trace_report


def _registry():
    return default_orchestration_evaluation_trace_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    build = build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=source_registry)
    )
    explainability = explain_orchestration_evaluation_trace(source_registry, build)
    return OrchestrationEvaluationTraceIntegrityInput(
        trace_registry=source_registry,
        build_result=build,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_evaluation_trace_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_evaluation_trace_integrity_result(_audit(source))


def _record(registry, trace_id):
    return next(record for record in registry.records if record.identifier.trace_id == trace_id)


def _replace_record(registry, trace_id, replacement):
    return build_orchestration_evaluation_trace_registry(
        tuple(
            replacement if record.identifier.trace_id == trace_id else record
            for record in registry.records
        )
    )


def test_trace_integrity_is_stable_with_visible_domains():
    result = _export()

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["governance_integrity"]["references"]) == 9
    assert len(result["policy_integrity"]["references"]) == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["trace_execution_enabled"] is False


def test_trace_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_evaluation_trace_integrity_result(first) == serialize_orchestration_evaluation_trace_integrity_result(second)
    assert hash_orchestration_evaluation_trace_integrity_result(first) == hash_orchestration_evaluation_trace_integrity_result(second)
    assert json.dumps(export_orchestration_evaluation_trace_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_evaluation_trace_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-trace-registry-hash")
    result = _export(source)

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_trace_registry(source.trace_registry)]
    assert "trace_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.trace.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_record(registry, target.identifier.trace_id, changed)))

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.trace.compatibility-check:replay_provenance_gap" in result["failure_classification_summary"]


def test_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_build_hash="mismatched-trace-build-hash",
        expected_explainability_hash="mismatched-trace-explainability-hash",
    )
    result = _export(source)

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "trace_build_hash_mismatch" in result["failure_classification_summary"]
    assert "trace_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_explainability_visibility_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.trace.informational")
    changed = replace(target, reasoning_chain=())
    result = _export(_integrity_input(_replace_record(registry, target.identifier.trace_id, changed)))

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP
    assert "v3_6.trace.informational:missing_reasoning_chain_visibility" in result["failure_classification_summary"]


def test_governance_boundary_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.trace.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_integrity_input(_replace_record(registry, target.identifier.trace_id, changed)))

    assert result["trace_integrity_status"] == TRACE_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.trace.orchestration-simulation:governance_boundary_gap" in result["failure_classification_summary"]


def test_trace_domain_and_policy_gaps_fail_integrity():
    registry = _registry()
    compatibility = _record(registry, "v3_6.trace.policy-boundary")
    dependency = _record(registry, "v3_6.trace.dependency-analysis")
    blocker = _record(registry, "v3_6.trace.prohibited-domain")
    supported = _record(registry, "v3_6.trace.informational")
    policy = _record(registry, "v3_6.trace.compatibility-check")
    trace_step = _record(registry, "v3_6.trace.continuity-analysis")

    assert _export(_integrity_input(_replace_record(registry, compatibility.identifier.trace_id, replace(compatibility, compatibility_domains=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    assert _export(_integrity_input(_replace_record(registry, dependency.identifier.trace_id, replace(dependency, dependency_domains=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert _export(_integrity_input(_replace_record(registry, blocker.identifier.trace_id, replace(blocker, blocker_domains=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    assert _export(_integrity_input(_replace_record(registry, supported.identifier.trace_id, replace(supported, supported_domains=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    assert _export(_integrity_input(_replace_record(registry, policy.identifier.trace_id, replace(policy, policy_ids=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_POLICY_GAP
    assert _export(_integrity_input(_replace_record(registry, trace_step.identifier.trace_id, replace(trace_step, trace_steps=()))))[
        "trace_integrity_status"
    ] == TRACE_INTEGRITY_BLOCKED_BY_STEP_GAP


def test_trace_report_summarizes_deterministic_evaluation_trace_totals():
    first = build_v3_6_orchestration_evaluation_trace_report()
    second = build_v3_6_orchestration_evaluation_trace_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_evaluation_trace_count"] == 9
    assert first["governance_trace_count"] == 9
    assert first["compatibility_trace_count"] == 8
    assert first["dependency_trace_count"] == 3
    assert first["blocker_trace_count"] == 8
    assert first["unsupported_domain_trace_count"] == 3
    assert first["prohibited_domain_trace_count"] == 3
    assert first["trace_step_count"] == 70
    assert first["reasoning_step_count"] == 70
    assert first["trace_integrity_status"] == TRACE_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
