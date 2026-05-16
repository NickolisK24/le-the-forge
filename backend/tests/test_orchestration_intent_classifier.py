from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_intent_classifier import (
    classify_orchestration_intents,
    export_orchestration_intent_classification_result,
    hash_orchestration_intent_classification_result,
    serialize_orchestration_intent_classification_result,
)
from app.runtime_orchestration.orchestration_intent_models import (
    INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP,
    INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS,
    INTENT_CONTINUITY_GAP,
    INTENT_CONTINUITY_PRESERVED,
    INTENT_GOVERNANCE_BOUNDARY_GAP,
    INTENT_HASH_MISMATCH,
    INTENT_PROHIBITED_DOMAIN_VISIBLE,
    INTENT_PROVENANCE_GAP,
    INTENT_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationIntentClassificationInput,
    hash_intent_registry,
)
from app.runtime_orchestration.orchestration_intent_registry import (
    build_orchestration_intent_registry,
    default_orchestration_intent_registry,
)


def _registry():
    return default_orchestration_intent_registry()


def _classify(registry=None, **kwargs):
    return classify_orchestration_intents(
        OrchestrationIntentClassificationInput(intent_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_intent_classification_result(result or _classify())


def _record(registry, intent_id):
    return next(record for record in registry.records if record.identifier.intent_id == intent_id)


def _replace_record(registry, intent_id, replacement):
    return build_orchestration_intent_registry(
        tuple(
            replacement if record.identifier.intent_id == intent_id else record
            for record in registry.records
        )
    )


def test_default_intent_classification_preserves_visible_domains():
    result = _export()

    assert result["intent_classification_status"] == INTENT_CLASSIFICATION_STABLE_WITH_VISIBLE_FINDINGS
    assert result["registered_intent_count"] == 9
    assert result["supported_intent_count"] == 7
    assert result["unsupported_intent_count"] == 1
    assert result["prohibited_intent_count"] == 1
    assert result["governance_boundary_count"] == 11
    assert result["compatibility_domain_count"] == 10
    assert result["dependency_domain_count"] == 5
    assert result["blocker_domain_count"] == 11
    assert result["provenance_continuity_status"] == INTENT_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == INTENT_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == INTENT_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == INTENT_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False


def test_intent_classification_serialization_and_hash_are_replay_stable():
    first = _classify()
    second = _classify()

    assert serialize_orchestration_intent_classification_result(first) == serialize_orchestration_intent_classification_result(second)
    assert hash_orchestration_intent_classification_result(first) == hash_orchestration_intent_classification_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_unsupported_and_prohibited_domains_are_fail_visible():
    result = _export()
    unsupported = next(record for record in result["classification_records"] if record["intent_id"] == "v3_6.intent.unsupported-domain")
    prohibited = next(record for record in result["classification_records"] if record["intent_id"] == "v3_6.intent.prohibited-domain")

    assert unsupported["unsupported_domain_count"] == 2
    assert any(finding["classification"] == INTENT_UNSUPPORTED_DOMAIN_VISIBLE for finding in unsupported["findings"])
    assert prohibited["prohibited_domain_count"] == 3
    assert any(finding["classification"] == INTENT_PROHIBITED_DOMAIN_VISIBLE for finding in prohibited["findings"])


def test_hash_mismatch_and_provenance_gap_are_structural_findings():
    registry = _registry()
    target = _record(registry, "v3_6.intent.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = _replace_record(registry, target.identifier.intent_id, changed)
    result = _export(
        _classify(
            changed_registry,
            expected_registry_hash="mismatched-intent-registry-hash",
            expected_intent_hashes={target.identifier.intent_id: "mismatched-intent-hash"},
        )
    )

    assert result["intent_classification_status"] == INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == INTENT_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_intent_registry(changed_registry)
    assert any(finding["classification"] == INTENT_HASH_MISMATCH for finding in result["finding_summary"])
    assert any(finding["classification"] == INTENT_PROVENANCE_GAP for finding in result["finding_summary"])


def test_governance_boundary_gap_blocks_classification():
    registry = _registry()
    target = _record(registry, "v3_6.intent.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_classify(_replace_record(registry, target.identifier.intent_id, changed)))

    assert result["intent_classification_status"] == INTENT_CLASSIFICATION_BLOCKED_BY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == INTENT_CONTINUITY_GAP
    assert any(finding["classification"] == INTENT_GOVERNANCE_BOUNDARY_GAP for finding in result["finding_summary"])
