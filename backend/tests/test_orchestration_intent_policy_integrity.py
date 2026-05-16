from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_intent_policy_explainability import explain_orchestration_intent_policy_mappings
from app.runtime_orchestration.orchestration_intent_policy_integrity import (
    audit_orchestration_intent_policy_mapping_integrity,
    export_orchestration_intent_policy_mapping_integrity_result,
    hash_orchestration_intent_policy_mapping_integrity_result,
    serialize_orchestration_intent_policy_mapping_integrity_result,
)
from app.runtime_orchestration.orchestration_intent_policy_mapper import map_orchestration_intent_policies
from app.runtime_orchestration.orchestration_intent_policy_mapping_models import (
    MAPPING_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_POLICY_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    MAPPING_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP,
    MAPPING_INTEGRITY_STABLE,
    OrchestrationIntentPolicyMappingInput,
    OrchestrationIntentPolicyMappingIntegrityInput,
    hash_mapping_registry,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_registry import (
    build_orchestration_intent_policy_mapping_registry,
    default_orchestration_intent_policy_mapping_registry,
)
from scripts.report_v3_6_orchestration_intent_policy_mapping import build_v3_6_orchestration_intent_policy_mapping_report


def _registry():
    return default_orchestration_intent_policy_mapping_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    mapping = map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=source_registry)
    )
    explainability = explain_orchestration_intent_policy_mappings(source_registry, mapping)
    return OrchestrationIntentPolicyMappingIntegrityInput(
        mapping_registry=source_registry,
        mapping_result=mapping,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_intent_policy_mapping_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_intent_policy_mapping_integrity_result(_audit(source))


def _record(registry, mapping_id):
    return next(record for record in registry.records if record.identifier.mapping_id == mapping_id)


def _replace_record(registry, mapping_id, replacement):
    return build_orchestration_intent_policy_mapping_registry(
        tuple(
            replacement if record.identifier.mapping_id == mapping_id else record
            for record in registry.records
        )
    )


def test_mapping_integrity_is_stable_with_visible_domains():
    result = _export()

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["governance_integrity"]["references"]) == 9
    assert len(result["policy_integrity"]["references"]) == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["mapping_execution_enabled"] is False


def test_mapping_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_intent_policy_mapping_integrity_result(first) == serialize_orchestration_intent_policy_mapping_integrity_result(second)
    assert hash_orchestration_intent_policy_mapping_integrity_result(first) == hash_orchestration_intent_policy_mapping_integrity_result(second)
    assert json.dumps(export_orchestration_intent_policy_mapping_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_intent_policy_mapping_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-mapping-registry-hash")
    result = _export(source)

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_mapping_registry(source.mapping_registry)]
    assert "mapping_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_record(registry, target.identifier.mapping_id, changed)))

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.mapping.compatibility-check:replay_provenance_gap" in result["failure_classification_summary"]


def test_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_mapping_analysis_hash="mismatched-mapping-analysis-hash",
        expected_explainability_hash="mismatched-mapping-explainability-hash",
    )
    result = _export(source)

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "mapping_analysis_hash_mismatch" in result["failure_classification_summary"]
    assert "mapping_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_explainability_visibility_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.informational")
    changed = replace(target, mapping_rationale=())
    result = _export(_integrity_input(_replace_record(registry, target.identifier.mapping_id, changed)))

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_BLOCKED_BY_EXPLAINABILITY_GAP
    assert "mapping_explainability_status:mapping_explainability_blocked_by_visibility_gap" in result["failure_classification_summary"]


def test_governance_boundary_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_integrity_input(_replace_record(registry, target.identifier.mapping_id, changed)))

    assert result["mapping_integrity_status"] == MAPPING_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.mapping.orchestration-simulation:governance_boundary_gap" in result["failure_classification_summary"]


def test_mapping_domain_and_policy_gaps_fail_integrity():
    registry = _registry()
    compatibility = _record(registry, "v3_6.mapping.compatibility-check")
    dependency = _record(registry, "v3_6.mapping.dependency-analysis")
    blocker = _record(registry, "v3_6.mapping.prohibited-domain")
    supported = _record(registry, "v3_6.mapping.informational")
    policy = _record(registry, "v3_6.mapping.policy-boundary")

    assert _export(_integrity_input(_replace_record(registry, compatibility.identifier.mapping_id, replace(compatibility, compatibility_domains=()))))[
        "mapping_integrity_status"
    ] == MAPPING_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    assert _export(_integrity_input(_replace_record(registry, dependency.identifier.mapping_id, replace(dependency, dependency_domains=()))))[
        "mapping_integrity_status"
    ] == MAPPING_INTEGRITY_BLOCKED_BY_DEPENDENCY_GAP
    assert _export(_integrity_input(_replace_record(registry, blocker.identifier.mapping_id, replace(blocker, blocker_domains=()))))[
        "mapping_integrity_status"
    ] == MAPPING_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    assert _export(_integrity_input(_replace_record(registry, supported.identifier.mapping_id, replace(supported, supported_domains=()))))[
        "mapping_integrity_status"
    ] == MAPPING_INTEGRITY_BLOCKED_BY_SUPPORTED_DOMAIN_GAP
    assert _export(_integrity_input(_replace_record(registry, policy.identifier.mapping_id, replace(policy, policy_ids=()))))[
        "mapping_integrity_status"
    ] == MAPPING_INTEGRITY_BLOCKED_BY_POLICY_GAP


def test_mapping_report_summarizes_deterministic_mapping_totals():
    first = build_v3_6_orchestration_intent_policy_mapping_report()
    second = build_v3_6_orchestration_intent_policy_mapping_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_mapping_count"] == 9
    assert first["supported_mapping_count"] == 7
    assert first["unsupported_mapping_count"] == 1
    assert first["prohibited_mapping_count"] == 1
    assert first["governance_boundary_count"] == 11
    assert first["compatibility_domain_count"] == 10
    assert first["dependency_domain_count"] == 5
    assert first["blocker_domain_count"] == 11
    assert first["mapping_integrity_status"] == MAPPING_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
