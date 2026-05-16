from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_intent_classifier import classify_orchestration_intents
from app.runtime_orchestration.orchestration_intent_explainability import (
    explain_orchestration_intents,
    export_orchestration_intent_explainability_result,
    hash_orchestration_intent_explainability_result,
    serialize_orchestration_intent_explainability_result,
)
from app.runtime_orchestration.orchestration_intent_models import (
    INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP,
    INTENT_EXPLAINABILITY_STABLE,
    OrchestrationIntentClassificationInput,
)
from app.runtime_orchestration.orchestration_intent_registry import (
    build_orchestration_intent_registry,
    default_orchestration_intent_registry,
)


def _registry():
    return default_orchestration_intent_registry()


def _explain(registry=None, classification=None):
    source_registry = registry or _registry()
    source_classification = classification or classify_orchestration_intents(
        OrchestrationIntentClassificationInput(intent_registry=source_registry)
    )
    return explain_orchestration_intents(source_registry, source_classification)


def _export(result=None):
    return export_orchestration_intent_explainability_result(result or _explain())


def _record(registry, intent_id):
    return next(record for record in registry.records if record.identifier.intent_id == intent_id)


def _replace_record(registry, intent_id, replacement):
    return build_orchestration_intent_registry(
        tuple(
            replacement if record.identifier.intent_id == intent_id else record
            for record in registry.records
        )
    )


def test_intent_explainability_generates_stable_visibility():
    result = _export()

    assert result["intent_explainability_status"] == INTENT_EXPLAINABILITY_STABLE
    assert result["supported_explanation_count"] == 7
    assert result["unsupported_explanation_count"] == 1
    assert result["prohibited_explanation_count"] == 1
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


def test_intent_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_intent_explainability_result(first) == serialize_orchestration_intent_explainability_result(second)
    assert hash_orchestration_intent_explainability_result(first) == hash_orchestration_intent_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_compatibility_check_explains_pre_analysis_domains():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["intent_id"] == "v3_6.intent.compatibility-check")

    assert record["intent_goal_visibility"] == ["pre-analyze which policy compatibility domains a future request would touch"]
    assert "compatibility_matrix" in record["compatibility_domain_visibility"]
    assert "compatibility_pre_analysis_only" in record["governance_boundary_visibility"]
    assert "compatibility_blocker_visibility" in record["blocker_domain_visibility"]
    assert "v3_6.intent.compatibility-check.replay" in record["provenance_visibility"]


def test_unsupported_and_prohibited_intents_explain_fail_visible_domains():
    result = _export()
    unsupported = next(item for item in result["explanation_records"] if item["intent_id"] == "v3_6.intent.unsupported-domain")
    prohibited = next(item for item in result["explanation_records"] if item["intent_id"] == "v3_6.intent.prohibited-domain")

    assert unsupported["support_state"] == "intent_unsupported"
    assert "autonomous_orchestration" in unsupported["unsupported_domain_visibility"]
    assert "unsupported_domain_blocker" in unsupported["blocker_domain_visibility"]
    assert prohibited["support_state"] == "intent_prohibited"
    assert "orchestration_execution" in prohibited["prohibited_domain_visibility"]
    assert "prohibited_execution_blocker" in prohibited["blocker_domain_visibility"]


def test_explainability_gap_is_fail_visible_for_unexplained_intent():
    registry = _registry()
    target = _record(registry, "v3_6.intent.informational")
    changed = replace(target, intent_goal="")
    changed_registry = _replace_record(registry, target.identifier.intent_id, changed)
    classification = classify_orchestration_intents(
        OrchestrationIntentClassificationInput(intent_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, classification))
    record = next(item for item in result["explanation_records"] if item["intent_id"] == target.identifier.intent_id)

    assert result["intent_explainability_status"] == INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
    assert record["explanation_status"] == INTENT_EXPLAINABILITY_BLOCKED_BY_VISIBILITY_GAP
