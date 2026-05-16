from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_evaluation_trace_builder import build_orchestration_evaluation_trace
from app.runtime_orchestration.orchestration_evaluation_trace_explainability import (
    explain_orchestration_evaluation_trace,
    export_orchestration_evaluation_trace_explainability_result,
    hash_orchestration_evaluation_trace_explainability_result,
    serialize_orchestration_evaluation_trace_explainability_result,
)
from app.runtime_orchestration.orchestration_evaluation_trace_models import (
    TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    TRACE_EXPLAINABILITY_STABLE,
    OrchestrationEvaluationTraceBuildInput,
)
from app.runtime_orchestration.orchestration_evaluation_trace_registry import (
    build_orchestration_evaluation_trace_registry,
    default_orchestration_evaluation_trace_registry,
)


def _registry():
    return default_orchestration_evaluation_trace_registry()


def _explain(registry=None, build=None):
    source_registry = registry or _registry()
    source_build = build or build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=source_registry)
    )
    return explain_orchestration_evaluation_trace(source_registry, source_build)


def _export(result=None):
    return export_orchestration_evaluation_trace_explainability_result(result or _explain())


def _record(registry, trace_id):
    return next(record for record in registry.records if record.identifier.trace_id == trace_id)


def _replace_record(registry, trace_id, replacement):
    return build_orchestration_evaluation_trace_registry(
        tuple(
            replacement if record.identifier.trace_id == trace_id else record
            for record in registry.records
        )
    )


def test_trace_explainability_generates_stable_visibility():
    result = _export()

    assert result["trace_explainability_status"] == TRACE_EXPLAINABILITY_STABLE
    assert result["governance_explanation_count"] == 9
    assert result["compatibility_explanation_count"] == 8
    assert result["dependency_explanation_count"] == 3
    assert result["blocker_explanation_count"] == 8
    assert result["unsupported_explanation_count"] == 3
    assert result["prohibited_explanation_count"] == 3
    assert result["trace_step_visibility_count"] == 70
    assert result["reasoning_chain_visibility_count"] == 70
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["trace_execution_enabled"] is False


def test_trace_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_evaluation_trace_explainability_result(first) == serialize_orchestration_evaluation_trace_explainability_result(second)
    assert hash_orchestration_evaluation_trace_explainability_result(first) == hash_orchestration_evaluation_trace_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatibility_check_explains_reasoning_chain_progression():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["trace_id"] == "v3_6.trace.compatibility-check")

    assert record["trace_state"] == "trace_supported"
    assert any("supportability_evaluation_trace_step" in step for step in record["trace_step_visibility"])
    assert any("compatibility_evaluation_trace_step" in step for step in record["trace_step_visibility"])
    assert any("deterministically expose blocker-chain domains" in step for step in record["reasoning_chain_visibility"])
    assert "v3_6.policy.modeling.allowed" in record["provenance_visibility"]
    assert "v3_6.trace.compatibility-check.replay" in record["provenance_visibility"]


def test_blocked_unsupported_and_prohibited_traces_explain_fail_visible_domains():
    result = _export()
    governance = next(item for item in result["explanation_records"] if item["trace_id"] == "v3_6.trace.governance-review")
    unsupported = next(item for item in result["explanation_records"] if item["trace_id"] == "v3_6.trace.unsupported-domain")
    prohibited = next(item for item in result["explanation_records"] if item["trace_id"] == "v3_6.trace.prohibited-domain")

    assert governance["trace_state"] == "trace_governance_blocked"
    assert "governance_conflict_visibility" in governance["blocker_domain_visibility"]
    assert unsupported["trace_state"] == "trace_unsupported"
    assert "autonomous_orchestration" in unsupported["unsupported_domain_visibility"]
    assert "unsupported_domain_blocker" in unsupported["blocker_domain_visibility"]
    assert prohibited["trace_state"] == "trace_prohibited"
    assert "orchestration_execution" in prohibited["prohibited_domain_visibility"]
    assert "prohibited_execution_blocker" in prohibited["blocker_domain_visibility"]


def test_explainability_gap_is_fail_visible_for_missing_reasoning_chain():
    registry = _registry()
    target = _record(registry, "v3_6.trace.informational")
    changed = replace(target, reasoning_chain=())
    changed_registry = _replace_record(registry, target.identifier.trace_id, changed)
    build = build_orchestration_evaluation_trace(
        OrchestrationEvaluationTraceBuildInput(trace_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, build))
    record = next(item for item in result["explanation_records"] if item["trace_id"] == target.identifier.trace_id)

    assert result["trace_explainability_status"] == TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert record["explanation_status"] == TRACE_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
