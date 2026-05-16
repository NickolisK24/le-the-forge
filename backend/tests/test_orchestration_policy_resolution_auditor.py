from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_resolution_auditor import (
    audit_orchestration_policy_resolution,
    export_orchestration_policy_resolution_audit_result,
    hash_orchestration_policy_resolution_audit_result,
    serialize_orchestration_policy_resolution_audit_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_models import (
    RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP,
    RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS,
    RESOLUTION_CONTINUITY_GAP,
    RESOLUTION_CONTINUITY_PRESERVED,
    RESOLUTION_EVIDENCE_INCOMPLETE,
    RESOLUTION_POTENTIAL_MISCLASSIFICATION,
    RESOLUTION_PROVENANCE_GAP,
    OrchestrationPolicyResolutionAuditInput,
    hash_resolution_registry,
)
from app.runtime_orchestration.orchestration_policy_resolution_registry import (
    build_orchestration_policy_resolution_registry,
    default_orchestration_policy_resolution_registry,
)


def _registry():
    return default_orchestration_policy_resolution_registry()


def _audit(registry=None, **kwargs):
    return audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=registry or _registry(), **kwargs)
    )


def _export(result=None):
    return export_orchestration_policy_resolution_audit_result(result or _audit())


def _record(registry, resolution_id):
    return next(record for record in registry.records if record.identifier.resolution_id == resolution_id)


def _replace_record(registry, resolution_id, replacement):
    return build_orchestration_policy_resolution_registry(
        tuple(
            replacement if record.identifier.resolution_id == resolution_id else record
            for record in registry.records
        )
    )


def test_default_resolution_audit_preserves_visible_blocked_classifications():
    result = _export()

    assert result["resolution_audit_status"] == RESOLUTION_AUDIT_STABLE_WITH_VISIBLE_FINDINGS
    assert result["intentional_block_count"] == 3
    assert result["future_candidate_count"] == 1
    assert result["unsupported_by_design_count"] == 2
    assert result["governance_conflict_count"] == 1
    assert result["dependency_conflict_count"] == 1
    assert result["continuity_conflict_count"] == 0
    assert result["evidence_incomplete_count"] == 1
    assert result["provenance_gap_count"] == 0
    assert result["potential_misclassification_count"] == 0
    assert result["blocker_chain_total"] == 8
    assert result["provenance_continuity_status"] == RESOLUTION_CONTINUITY_PRESERVED
    assert result["explainability_continuity_status"] == RESOLUTION_CONTINUITY_PRESERVED
    assert result["integrity_continuity_status"] == RESOLUTION_CONTINUITY_PRESERVED
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["automatic_resolution_enabled"] is False


def test_resolution_audit_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_policy_resolution_audit_result(first) == serialize_orchestration_policy_resolution_audit_result(second)
    assert hash_orchestration_policy_resolution_audit_result(first) == hash_orchestration_policy_resolution_audit_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_future_candidate_exposes_evidence_gap_without_status_upgrade():
    result = _export()
    record = next(item for item in result["audit_records"] if item["resolution_id"] == "v3_6.resolution.explainability-routing.incompatible")

    assert RESOLUTION_EVIDENCE_INCOMPLETE in record["resolution_classifications"]
    assert record["future_support_possible"] is True
    assert record["evidence_gap_count"] == 1
    assert record["compatibility_state"] == "compatibility_incompatible"


def test_provenance_gap_is_fail_visible():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_audit(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_audit_status"] == RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    assert result["provenance_continuity_status"] == RESOLUTION_CONTINUITY_GAP
    assert result["provenance_gap_count"] == 1
    assert any(finding["classification"] == RESOLUTION_PROVENANCE_GAP for finding in result["finding_summary"])


def test_registry_and_record_hash_mismatches_are_continuity_failures():
    registry = _registry()
    result = _export(
        _audit(
            registry,
            expected_registry_hash="mismatched-resolution-registry-hash",
            expected_resolution_hashes={"v3_6.resolution.explainability-routing.incompatible": "mismatched-resolution-hash"},
        )
    )

    assert result["resolution_audit_status"] == RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    assert result["deterministic_registry_hash"] == hash_resolution_registry(registry)
    assert result["continuity_conflict_count"] == 1
    assert any("resolution registry hash does not match" in finding["reason"] for finding in result["finding_summary"])
    assert any("resolution record hash does not match" in finding["reason"] for finding in result["finding_summary"])


def test_potential_misclassification_is_fail_visible_without_upgrading_status():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, future_support_possible=True)
    result = _export(_audit(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["potential_misclassification_count"] == 1
    record = next(item for item in result["audit_records"] if item["resolution_id"] == target.identifier.resolution_id)
    assert RESOLUTION_POTENTIAL_MISCLASSIFICATION in record["resolution_classifications"]
    assert record["compatibility_state"] == "compatibility_prohibited"


def test_continuity_gap_and_governance_gap_remain_explicit():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.autonomy-routing.unsupported")
    changed = replace(
        target,
        continuity_gaps=("unsupported_combination_requires_new_design_evidence",),
        routing_behavior_enabled=True,
    )
    result = _export(_audit(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_audit_status"] == RESOLUTION_AUDIT_BLOCKED_BY_CONTINUITY_GAP
    assert result["continuity_conflict_count"] == 1
    record = next(item for item in result["audit_records"] if item["resolution_id"] == target.identifier.resolution_id)
    assert record["continuity_gap_count"] == 1
    assert record["integrity_continuity_state"] == RESOLUTION_CONTINUITY_GAP
