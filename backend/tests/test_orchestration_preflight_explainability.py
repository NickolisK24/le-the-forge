from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_preflight_evaluator import evaluate_orchestration_preflight
from app.runtime_orchestration.orchestration_preflight_explainability import (
    explain_orchestration_preflight,
    export_orchestration_preflight_explainability_result,
    hash_orchestration_preflight_explainability_result,
    serialize_orchestration_preflight_explainability_result,
)
from app.runtime_orchestration.orchestration_preflight_models import (
    PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    PREFLIGHT_EXPLAINABILITY_STABLE,
    OrchestrationPreflightEvaluationInput,
)
from app.runtime_orchestration.orchestration_preflight_registry import (
    build_orchestration_preflight_registry,
    default_orchestration_preflight_registry,
)


def _registry():
    return default_orchestration_preflight_registry()


def _explain(registry=None, evaluation=None):
    source_registry = registry or _registry()
    source_evaluation = evaluation or evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=source_registry)
    )
    return explain_orchestration_preflight(source_registry, source_evaluation)


def _export(result=None):
    return export_orchestration_preflight_explainability_result(result or _explain())


def _record(registry, preflight_id):
    return next(record for record in registry.records if record.identifier.preflight_id == preflight_id)


def _replace_record(registry, preflight_id, replacement):
    return build_orchestration_preflight_registry(
        tuple(
            replacement if record.identifier.preflight_id == preflight_id else record
            for record in registry.records
        )
    )


def test_preflight_explainability_generates_stable_visibility():
    result = _export()

    assert result["preflight_explainability_status"] == PREFLIGHT_EXPLAINABILITY_STABLE
    assert result["supported_explanation_count"] == 3
    assert result["unsupported_explanation_count"] == 1
    assert result["prohibited_explanation_count"] == 2
    assert result["governance_blocked_explanation_count"] == 1
    assert result["compatibility_blocked_explanation_count"] == 1
    assert result["dependency_blocked_explanation_count"] == 1
    assert result["policy_visibility_count"] == 31
    assert result["governance_boundary_visibility_count"] == 35
    assert result["compatibility_domain_visibility_count"] == 10
    assert result["dependency_domain_visibility_count"] == 5
    assert result["blocker_domain_visibility_count"] == 11
    assert result["unsupported_domain_visibility_count"] == 4
    assert result["prohibited_domain_visibility_count"] == 5
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["preflight_execution_enabled"] is False


def test_preflight_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_preflight_explainability_result(first) == serialize_orchestration_preflight_explainability_result(second)
    assert hash_orchestration_preflight_explainability_result(first) == hash_orchestration_preflight_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatibility_check_explains_theoretical_supportability():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["preflight_id"] == "v3_6.preflight.compatibility-check")

    assert record["theoretical_supportability_visibility"] == ["theoretically_supportable:True"]
    assert "v3_6.policy.modeling.allowed" in record["policy_visibility"]
    assert "compatibility_matrix" in record["compatibility_domain_visibility"]
    assert "compatibility-check intent is theoretically supportable as preflight analysis" in record["preflight_rationale_visibility"]
    assert "v3_6.preflight.compatibility-check.replay" in record["provenance_visibility"]


def test_blocked_unsupported_and_prohibited_preflights_explain_fail_visible_domains():
    result = _export()
    governance = next(item for item in result["explanation_records"] if item["preflight_id"] == "v3_6.preflight.governance-review")
    unsupported = next(item for item in result["explanation_records"] if item["preflight_id"] == "v3_6.preflight.unsupported-domain")
    prohibited = next(item for item in result["explanation_records"] if item["preflight_id"] == "v3_6.preflight.prohibited-domain")

    assert governance["preflight_state"] == "preflight_governance_blocked"
    assert "governance_conflict_visibility" in governance["blocker_domain_visibility"]
    assert unsupported["preflight_state"] == "preflight_unsupported"
    assert "autonomous_orchestration" in unsupported["unsupported_domain_visibility"]
    assert "unsupported_domain_blocker" in unsupported["blocker_domain_visibility"]
    assert prohibited["preflight_state"] == "preflight_prohibited"
    assert "orchestration_execution" in prohibited["prohibited_domain_visibility"]
    assert "prohibited_execution_blocker" in prohibited["blocker_domain_visibility"]


def test_explainability_gap_is_fail_visible_for_unexplained_preflight():
    registry = _registry()
    target = _record(registry, "v3_6.preflight.informational")
    changed = replace(target, preflight_rationale=())
    changed_registry = _replace_record(registry, target.identifier.preflight_id, changed)
    evaluation = evaluate_orchestration_preflight(
        OrchestrationPreflightEvaluationInput(preflight_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, evaluation))
    record = next(item for item in result["explanation_records"] if item["preflight_id"] == target.identifier.preflight_id)

    assert result["preflight_explainability_status"] == PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert record["explanation_status"] == PREFLIGHT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
