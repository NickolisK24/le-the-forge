from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_resolution_auditor import audit_orchestration_policy_resolution
from app.runtime_orchestration.orchestration_policy_resolution_explainability import explain_orchestration_policy_resolution
from app.runtime_orchestration.orchestration_policy_resolution_integrity import (
    audit_orchestration_policy_resolution_integrity,
    export_orchestration_policy_resolution_integrity_result,
    hash_orchestration_policy_resolution_integrity_result,
    serialize_orchestration_policy_resolution_integrity_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_models import (
    RESOLUTION_INTEGRITY_BLOCKED_BY_BLOCKER_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP,
    RESOLUTION_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP,
    RESOLUTION_INTEGRITY_STABLE,
    OrchestrationPolicyResolutionAuditInput,
    OrchestrationPolicyResolutionIntegrityInput,
    hash_resolution_registry,
)
from app.runtime_orchestration.orchestration_policy_resolution_registry import (
    build_orchestration_policy_resolution_registry,
    default_orchestration_policy_resolution_registry,
)
from scripts.report_v3_6_orchestration_policy_resolution_audit import build_v3_6_orchestration_policy_resolution_audit_report


def _registry():
    return default_orchestration_policy_resolution_registry()


def _integrity_input(registry=None, **kwargs):
    source_registry = registry or _registry()
    audit = audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=source_registry)
    )
    explainability = explain_orchestration_policy_resolution(source_registry, audit)
    return OrchestrationPolicyResolutionIntegrityInput(
        resolution_registry=source_registry,
        audit_result=audit,
        explainability_result=explainability,
        **kwargs,
    )


def _audit(source=None):
    return audit_orchestration_policy_resolution_integrity(source or _integrity_input())


def _export(source=None):
    return export_orchestration_policy_resolution_integrity_result(_audit(source))


def _record(registry, resolution_id):
    return next(record for record in registry.records if record.identifier.resolution_id == resolution_id)


def _replace_record(registry, resolution_id, replacement):
    return build_orchestration_policy_resolution_registry(
        tuple(
            replacement if record.identifier.resolution_id == resolution_id else record
            for record in registry.records
        )
    )


def test_resolution_integrity_is_stable_with_visible_blocker_chains():
    result = _export()

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_STABLE
    assert result["failure_classification_summary"] == []
    assert len(result["blocker_integrity"]["references"]) == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["automatic_resolution_enabled"] is False


def test_resolution_integrity_serialization_and_hash_are_replay_stable():
    first = _audit()
    second = _audit()

    assert serialize_orchestration_policy_resolution_integrity_result(first) == serialize_orchestration_policy_resolution_integrity_result(second)
    assert hash_orchestration_policy_resolution_integrity_result(first) == hash_orchestration_policy_resolution_integrity_result(second)
    assert json.dumps(export_orchestration_policy_resolution_integrity_result(first), sort_keys=True) == json.dumps(
        export_orchestration_policy_resolution_integrity_result(second),
        sort_keys=True,
    )


def test_registry_hash_mismatch_is_integrity_failure():
    source = _integrity_input(expected_registry_hash="mismatched-resolution-registry-hash")
    result = _export(source)

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert result["registry_integrity"]["references"] == [hash_resolution_registry(source.resolution_registry)]
    assert "resolution_registry_hash_mismatch" in result["failure_classification_summary"]


def test_provenance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, provenance=replace(target.provenance, replay_reference_ids=()))
    result = _export(_integrity_input(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_PROVENANCE_GAP
    assert "v3_6.resolution.execution-routing.prohibited:replay_provenance_gap" in result["failure_classification_summary"]


def test_missing_evidence_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.explainability-routing.incompatible")
    changed = replace(target, evidence_gaps=())
    result = _export(_integrity_input(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_EVIDENCE_GAP
    assert "v3_6.resolution.explainability-routing.incompatible:missing_evidence_gap_visibility" in result["failure_classification_summary"]


def test_missing_blocker_chain_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, blocker_chain_ids=())
    result = _export(_integrity_input(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_BLOCKER_GAP
    assert "v3_6.resolution.execution-routing.prohibited:missing_blocker_chain_visibility" in result["failure_classification_summary"]


def test_governance_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.autonomy-routing.unsupported")
    changed = replace(target, routing_behavior_enabled=True)
    result = _export(_integrity_input(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_GOVERNANCE_GAP
    assert "v3_6.resolution.autonomy-routing.unsupported:integrity_continuity_gap" in result["failure_classification_summary"]
    assert "v3_6.resolution.autonomy-routing.unsupported:governance_boundary_gap" in result["failure_classification_summary"]


def test_compatibility_continuity_gap_is_integrity_failure():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, compatibility_state="compatibility_incompatible")
    result = _export(_integrity_input(_replace_record(registry, target.identifier.resolution_id, changed)))

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_COMPATIBILITY_GAP
    assert "v3_6.resolution.execution-routing.prohibited:compatibility_state_mismatch" in result["failure_classification_summary"]


def test_audit_and_explainability_hash_mismatches_fail_integrity():
    source = _integrity_input(
        expected_audit_hash="mismatched-resolution-audit-hash",
        expected_explainability_hash="mismatched-resolution-explainability-hash",
    )
    result = _export(source)

    assert result["resolution_integrity_status"] == RESOLUTION_INTEGRITY_BLOCKED_BY_HASH_GAP
    assert "resolution_audit_hash_mismatch" in result["failure_classification_summary"]
    assert "resolution_explainability_hash_mismatch" in result["failure_classification_summary"]


def test_resolution_report_summarizes_deterministic_audit_totals():
    first = build_v3_6_orchestration_policy_resolution_audit_report()
    second = build_v3_6_orchestration_policy_resolution_audit_report()

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["registered_resolution_record_count"] == 8
    assert first["intentional_block_count"] == 3
    assert first["future_candidate_count"] == 1
    assert first["unsupported_by_design_count"] == 2
    assert first["governance_conflict_count"] == 1
    assert first["dependency_conflict_count"] == 1
    assert first["continuity_conflict_count"] == 0
    assert first["evidence_incomplete_count"] == 1
    assert first["provenance_gap_count"] == 0
    assert first["potential_misclassification_count"] == 0
    assert first["blocker_chain_total"] == 8
    assert first["resolution_integrity_status"] == RESOLUTION_INTEGRITY_STABLE
    assert first["deterministic_validation_status"] == "deterministic_validation_stable"
    assert first["replay_safety_confirmation"] is True
    assert first["rollback_safety_confirmation"] is True
