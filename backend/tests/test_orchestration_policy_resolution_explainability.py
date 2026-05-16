from __future__ import annotations

import json
from dataclasses import replace

from app.runtime_orchestration.orchestration_policy_resolution_auditor import audit_orchestration_policy_resolution
from app.runtime_orchestration.orchestration_policy_resolution_explainability import (
    explain_orchestration_policy_resolution,
    export_orchestration_policy_resolution_explainability_result,
    hash_orchestration_policy_resolution_explainability_result,
    serialize_orchestration_policy_resolution_explainability_result,
)
from app.runtime_orchestration.orchestration_policy_resolution_models import (
    RESOLUTION_EXPLAINABILITY_STABLE,
    OrchestrationPolicyResolutionAuditInput,
)
from app.runtime_orchestration.orchestration_policy_resolution_registry import (
    build_orchestration_policy_resolution_registry,
    default_orchestration_policy_resolution_registry,
)


def _registry():
    return default_orchestration_policy_resolution_registry()


def _explain(registry=None, audit=None):
    source_registry = registry or _registry()
    source_audit = audit or audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=source_registry)
    )
    return explain_orchestration_policy_resolution(source_registry, source_audit)


def _export(result=None):
    return export_orchestration_policy_resolution_explainability_result(result or _explain())


def _record(registry, resolution_id):
    return next(record for record in registry.records if record.identifier.resolution_id == resolution_id)


def _replace_record(registry, resolution_id, replacement):
    return build_orchestration_policy_resolution_registry(
        tuple(
            replacement if record.identifier.resolution_id == resolution_id else record
            for record in registry.records
        )
    )


def test_resolution_explainability_generates_stable_visibility():
    result = _export()

    assert result["resolution_explainability_status"] == RESOLUTION_EXPLAINABILITY_STABLE
    assert result["blocked_explanation_count"] == 8
    assert result["future_support_explanation_count"] == 1
    assert result["evidence_gap_visibility_count"] == 1
    assert result["governance_visibility_count"] >= 5
    assert result["dependency_visibility_count"] == 1
    assert result["blocker_chain_visibility_count"] == 8
    assert result["runtime_execution_enabled"] is False
    assert result["orchestration_execution_enabled"] is False
    assert result["routing_behavior_enabled"] is False
    assert result["mutation_behavior_enabled"] is False
    assert result["production_consumption_enabled"] is False
    assert result["automatic_resolution_enabled"] is False


def test_resolution_explainability_serialization_and_hash_are_replay_stable():
    first = _explain()
    second = _explain()

    assert serialize_orchestration_policy_resolution_explainability_result(first) == serialize_orchestration_policy_resolution_explainability_result(second)
    assert hash_orchestration_policy_resolution_explainability_result(first) == hash_orchestration_policy_resolution_explainability_result(second)
    assert json.dumps(_export(first), sort_keys=True) == json.dumps(_export(second), sort_keys=True)


def test_intentional_block_explains_governance_block_reason():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["resolution_id"] == "v3_6.resolution.execution-routing.prohibited")

    assert "intentional_block" in record["resolution_classifications"]
    assert "block_intentional:true" in record["block_intent_visibility"]
    assert any("execution-capable policy and routing-capable policy may not coexist" in entry for entry in record["why_blocked"])
    assert "v3_6.compat.execution-routing.prohibited.blocker-chain" in record["blocker_chain_visibility"]
    assert "v3_6.resolution.execution-routing.prohibited.replay" in record["provenance_visibility"]


def test_future_candidate_explains_missing_evidence_requirements():
    result = _export()
    record = next(item for item in result["explanation_records"] if item["resolution_id"] == "v3_6.resolution.explainability-routing.incompatible")

    assert "future_candidate" in record["resolution_classifications"]
    assert any("future_support_requires:prove explainability remains non-routing" == entry for entry in record["future_support_visibility"])
    assert any("future_support_governance_boundary_proof" in entry or "future_support_requires" in entry for entry in record["future_support_visibility"])
    assert any("evidence-gap" in entry for entry in record["evidence_gap_visibility"])
    assert "future_candidate_requires_non_execution_governance_evidence" in record["governance_visibility"]


def test_dependency_and_governance_resolution_visibility_are_explainable():
    result = _export()
    dependency = next(item for item in result["explanation_records"] if item["resolution_id"] == "v3_6.resolution.integrity-execution.dependency-blocked")
    governance = next(item for item in result["explanation_records"] if item["resolution_id"] == "v3_6.resolution.governance-production-runtime.governance-blocked")

    assert "integrity-requires-non-executing-policy-surface" in dependency["dependency_visibility"]
    assert any("integrity policy can audit execution prohibition" in entry for entry in dependency["why_blocked"])
    assert "production_runtime_access_conflicts_with_non_production_governance" in governance["governance_visibility"]
    assert any("governance boundary prohibits production runtime policy coexistence" in entry for entry in governance["why_blocked"])


def test_explainability_gap_visibility_remains_explicit():
    registry = _registry()
    target = _record(registry, "v3_6.resolution.execution-routing.prohibited")
    changed = replace(target, resolution_explainability_ids=())
    changed_registry = _replace_record(registry, target.identifier.resolution_id, changed)
    audit = audit_orchestration_policy_resolution(
        OrchestrationPolicyResolutionAuditInput(resolution_registry=changed_registry)
    )
    result = _export(_explain(changed_registry, audit))
    record = next(item for item in result["explanation_records"] if item["resolution_id"] == target.identifier.resolution_id)

    assert result["resolution_explainability_status"] == RESOLUTION_EXPLAINABILITY_STABLE
    assert any("explainability_continuity_state:resolution_continuity_gap" in entry for entry in record["continuity_visibility"])
