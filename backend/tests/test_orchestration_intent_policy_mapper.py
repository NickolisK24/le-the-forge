from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_intent_policy_mapper import (
    export_orchestration_intent_policy_mapping_result,
    hash_orchestration_intent_policy_mapping_result,
    map_orchestration_intent_policies,
    serialize_orchestration_intent_policy_mapping_result,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_models import (
    MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP,
    MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS,
    MAPPING_CONTINUITY_GAP,
    MAPPING_CONTINUITY_PRESERVED,
    MAPPING_GOVERNANCE_BOUNDARY_GAP,
    MAPPING_HASH_MISMATCH,
    MAPPING_POLICY_APPLICABILITY_VISIBLE,
    MAPPING_PROHIBITED_DOMAIN_VISIBLE,
    MAPPING_PROVENANCE_GAP,
    MAPPING_UNSUPPORTED_DOMAIN_VISIBLE,
    OrchestrationIntentPolicyMappingInput,
    hash_mapping_registry,
)
from app.runtime_orchestration.orchestration_intent_policy_mapping_registry import (
    build_orchestration_intent_policy_mapping_registry,
    default_orchestration_intent_policy_mapping_registry,
)


def _registry():
    return default_orchestration_intent_policy_mapping_registry()


def _map(registry=None, **kwargs):
    return map_orchestration_intent_policies(
        OrchestrationIntentPolicyMappingInput(mapping_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_intent_policy_mapping_result(result or _map())


def _record(registry, mapping_id):
    return next(record for record in registry.records if record.identifier.mapping_id == mapping_id)


def _replace_record(registry, mapping_id, replacement):
    return build_orchestration_intent_policy_mapping_registry(
        tuple(
            replacement if record.identifier.mapping_id == mapping_id else record
            for record in registry.records
        )
    )


def test_default_mapping_analysis_preserves_visible_domains():
    result = _export()

    assert result["mapping_analysis_status"] == MAPPING_ANALYSIS_STABLE_WITH_VISIBLE_FINDINGS
    assert result["registered_mapping_count"] == 9
    assert result["supported_mapping_count"] == 7
    assert result["unsupported_mapping_count"] == 1
    assert result["prohibited_mapping_count"] == 1
    assert result["policy_count"] == 8
    assert result["governance_boundary_count"] == 11
    assert result["compatibility_domain_count"] == 10
    assert result["dependency_domain_count"] == 5
    assert result["blocker_domain_count"] == 11
    assert result["provenance_continuity_status"] == MAPPING_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == MAPPING_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == MAPPING_CONTINUITY_PRESERVED
    assert result["governance_continuity_status"] == MAPPING_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["recommendation_behavior_enabled"] is False
    assert result["optimization_behavior_enabled"] is False
    assert result["graph_execution_enabled"] is False
    assert result["mapping_execution_enabled"] is False


def test_mapping_analysis_serialization_and_hash_are_replay_stable():
    first = _map()
    second = _map()

    assert serialize_orchestration_intent_policy_mapping_result(first) == serialize_orchestration_intent_policy_mapping_result(second)
    assert hash_orchestration_intent_policy_mapping_result(first) == hash_orchestration_intent_policy_mapping_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_policy_applicability_is_visible_before_compatibility_evaluation():
    result = _export()
    record = next(item for item in result["analysis_records"] if item["mapping_id"] == "v3_6.mapping.compatibility-check")

    assert record["policy_count"] == 4
    assert any(finding["classification"] == MAPPING_POLICY_APPLICABILITY_VISIBLE for finding in record["findings"])
    assert "v3_6.policy.integrity.allowed" in next(
        finding["evidence_ids"] for finding in record["findings"] if finding["classification"] == MAPPING_POLICY_APPLICABILITY_VISIBLE
    )


def test_unsupported_and_prohibited_mapping_domains_are_fail_visible():
    result = _export()
    unsupported = next(record for record in result["analysis_records"] if record["mapping_id"] == "v3_6.mapping.unsupported-domain")
    prohibited = next(record for record in result["analysis_records"] if record["mapping_id"] == "v3_6.mapping.prohibited-domain")

    assert unsupported["unsupported_domain_count"] == 2
    assert any(finding["classification"] == MAPPING_UNSUPPORTED_DOMAIN_VISIBLE for finding in unsupported["findings"])
    assert prohibited["prohibited_domain_count"] == 3
    assert any(finding["classification"] == MAPPING_PROHIBITED_DOMAIN_VISIBLE for finding in prohibited["findings"])


def test_hash_mismatch_and_provenance_gap_are_structural_findings():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.compatibility-check")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    changed_registry = _replace_record(registry, target.identifier.mapping_id, changed)
    result = _export(
        _map(
            changed_registry,
            expected_registry_hash="mismatched-mapping-registry-hash",
            expected_mapping_hashes={target.identifier.mapping_id: "mismatched-mapping-hash"},
        )
    )

    assert result["mapping_analysis_status"] == MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == MAPPING_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_mapping_registry(changed_registry)
    assert any(finding["classification"] == MAPPING_HASH_MISMATCH for finding in result["finding_summary"])
    assert any(finding["classification"] == MAPPING_PROVENANCE_GAP for finding in result["finding_summary"])


def test_governance_boundary_gap_blocks_mapping_analysis():
    registry = _registry()
    target = _record(registry, "v3_6.mapping.orchestration-simulation")
    changed = replace(target, graph_execution_enabled=True)
    result = _export(_map(_replace_record(registry, target.identifier.mapping_id, changed)))

    assert result["mapping_analysis_status"] == MAPPING_ANALYSIS_BLOCKED_BY_CONTINUITY_GAP
    assert result["governance_continuity_status"] == MAPPING_CONTINUITY_GAP
    assert any(finding["classification"] == MAPPING_GOVERNANCE_BOUNDARY_GAP for finding in result["finding_summary"])
