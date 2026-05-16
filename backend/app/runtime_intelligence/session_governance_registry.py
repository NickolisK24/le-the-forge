"""Registry validation for runtime session governance contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.session_governance_contracts import (
    SESSION_LABELS,
    _all_deps,
    build_runtime_session_governance_manifest,
    default_runtime_session_governance_contracts,
    order_session_governance_contracts,
)
from app.runtime_intelligence.session_governance_hashing import (
    hash_session_governance_manifest,
    validate_session_governance_replay_stability,
)


REQUIRED_SESSION_FIELDS = (
    "session_contract_id",
    "session_label",
    "deterministic_rank",
    "allowed_classification_ids",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_reasoning_stage_ids",
    "allowed_explanation_type_ids",
    "allowed_confidence_type_ids",
    "allowed_synthesis_type_ids",
    "allowed_boundary_type_ids",
    "allowed_replay_type_ids",
    "allowed_drift_type_ids",
    "required_previous_session_contract_ids",
    "requires_session_id",
    "requires_input_manifest_hash",
    "requires_lineage_hash",
    "requires_replay_scope",
    "requires_drift_scope",
    "requires_rollback_path",
    "requires_invalidation_rule",
    "isolates_session_state",
    "blocks_cross_session_mutation",
    "blocks_invalidated_session_reuse",
    "blocks_production_authorization",
    "rollback_visible",
    "invalidation_visible",
    "drift_visible",
    "replay_mismatch_visible",
    "boundary_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_session_governance_contracts(session_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("session_contract_id")) for row in session_contracts)
    labels = Counter(str(row.get("session_label")) for row in session_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in session_contracts)
    return {
        "duplicate_session_contract_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_session_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_session_governance_registry(session_contracts: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    deps = _all_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
        kwargs.get("drift_contracts"),
    )
    ordered = order_session_governance_contracts(session_contracts)
    session_ranks = {row.get("session_contract_id"): int(row.get("deterministic_rank", 0)) for row in ordered}
    session_ids = set(session_ranks)
    duplicate_detection = detect_duplicate_session_governance_contracts(ordered)
    missing_required_fields = {
        str(row.get("session_label") or row.get("session_contract_id") or index): [
            field for field in REQUIRED_SESSION_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("session_label")) for row in ordered} - set(SESSION_LABELS))
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", {row["classification_id"] for row in deps["classifications"]})
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", {row["evidence_type_id"] for row in deps["evidence"]})
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", {row["provenance_type_id"] for row in deps["provenance"]})
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", {row["stage_type_id"] for row in deps["reasoning"]})
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", {row["explanation_type_id"] for row in deps["explanations"]})
    invalid_confidence_references = _invalid_refs(ordered, "allowed_confidence_type_ids", {row["confidence_type_id"] for row in deps["confidence"]})
    invalid_synthesis_references = _invalid_refs(ordered, "allowed_synthesis_type_ids", {row["synthesis_type_id"] for row in deps["synthesis"]})
    invalid_boundary_references = _invalid_refs(ordered, "allowed_boundary_type_ids", {row["boundary_type_id"] for row in deps["boundaries"]})
    invalid_replay_references = _invalid_refs(ordered, "allowed_replay_type_ids", {row["replay_type_id"] for row in deps["replay"]})
    invalid_drift_references = _invalid_refs(ordered, "allowed_drift_type_ids", {row["drift_type_id"] for row in deps["drift"]})
    invalid_previous_session_references = _invalid_refs(ordered, "required_previous_session_contract_ids", session_ids)
    previous_rank_violations = {
        row["session_label"]: [
            previous_id
            for previous_id in row.get("required_previous_session_contract_ids", [])
            if previous_id in session_ranks and session_ranks[previous_id] >= int(row["deterministic_rank"])
        ]
        for row in ordered
    }
    previous_rank_violations = {key: values for key, values in previous_rank_violations.items() if values}
    behavior_rule_violations = _behavior_rule_violations(ordered)
    production_authorized = [row["session_label"] for row in ordered if row.get("production_authorized") is True]
    checks = [
        (any(duplicate_detection.values()), "duplicate_session_governance_contracts_detected"),
        (missing_required_fields, "missing_required_session_fields"),
        (unknown_labels, "unknown_session_labels"),
        (invalid_classification_references, "invalid_classification_references"),
        (invalid_evidence_references, "invalid_evidence_references"),
        (invalid_provenance_references, "invalid_provenance_references"),
        (invalid_reasoning_stage_references, "invalid_reasoning_stage_references"),
        (invalid_explanation_references, "invalid_explanation_references"),
        (invalid_confidence_references, "invalid_confidence_references"),
        (invalid_synthesis_references, "invalid_synthesis_references"),
        (invalid_boundary_references, "invalid_boundary_references"),
        (invalid_replay_references, "invalid_replay_references"),
        (invalid_drift_references, "invalid_drift_references"),
        (invalid_previous_session_references, "invalid_previous_session_references"),
        (previous_rank_violations, "previous_session_rank_ordering_invalid"),
        (behavior_rule_violations, "session_behavior_rule_invalid"),
        (production_authorized, "production_authorized_session_governance_detected"),
    ]
    validation_errors = [error for condition, error in checks if condition]
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_classification_references": invalid_classification_references,
        "invalid_classification_reference_count": _count_refs(invalid_classification_references),
        "invalid_evidence_references": invalid_evidence_references,
        "invalid_evidence_reference_count": _count_refs(invalid_evidence_references),
        "invalid_provenance_references": invalid_provenance_references,
        "invalid_provenance_reference_count": _count_refs(invalid_provenance_references),
        "invalid_reasoning_stage_references": invalid_reasoning_stage_references,
        "invalid_reasoning_stage_reference_count": _count_refs(invalid_reasoning_stage_references),
        "invalid_explanation_references": invalid_explanation_references,
        "invalid_explanation_reference_count": _count_refs(invalid_explanation_references),
        "invalid_confidence_references": invalid_confidence_references,
        "invalid_confidence_reference_count": _count_refs(invalid_confidence_references),
        "invalid_synthesis_references": invalid_synthesis_references,
        "invalid_synthesis_reference_count": _count_refs(invalid_synthesis_references),
        "invalid_boundary_references": invalid_boundary_references,
        "invalid_boundary_reference_count": _count_refs(invalid_boundary_references),
        "invalid_replay_references": invalid_replay_references,
        "invalid_replay_reference_count": _count_refs(invalid_replay_references),
        "invalid_drift_references": invalid_drift_references,
        "invalid_drift_reference_count": _count_refs(invalid_drift_references),
        "invalid_previous_session_references": invalid_previous_session_references,
        "invalid_previous_session_reference_count": _count_refs(invalid_previous_session_references),
        "previous_session_rank_violations": previous_rank_violations,
        "previous_session_rank_violation_count": _count_refs(previous_rank_violations),
        "behavior_rule_violations": behavior_rule_violations,
        "behavior_rule_violation_count": len(behavior_rule_violations),
        "production_authorized_session_governance": production_authorized,
    }


def export_session_governance_registry(session_contracts: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    deps = _all_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
        kwargs.get("drift_contracts"),
    )
    contracts = session_contracts or default_runtime_session_governance_contracts(
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
        replay_contracts=deps["replay"],
        drift_contracts=deps["drift"],
    )
    manifest = build_runtime_session_governance_manifest(
        contracts,
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
        replay_contracts=deps["replay"],
        drift_contracts=deps["drift"],
    )
    validation = validate_session_governance_registry(
        manifest["session_contracts"],
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
        replay_contracts=deps["replay"],
        drift_contracts=deps["drift"],
    )
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = validate_session_governance_replay_stability(manifest)
    exported["deterministic_hash"] = hash_session_governance_manifest(exported)
    return exported


def _behavior_rule_violations(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    required = {
        "session_identity": ["requires_session_id", "requires_input_manifest_hash"],
        "session_input_manifest": ["requires_input_manifest_hash"],
        "session_isolation_boundary": ["isolates_session_state", "blocks_cross_session_mutation"],
        "session_lineage_record": ["requires_lineage_hash"],
        "session_replay_scope": ["requires_replay_scope"],
        "session_drift_scope": ["requires_drift_scope"],
        "session_invalidation_rule": ["requires_invalidation_rule", "blocks_invalidated_session_reuse", "invalidation_visible"],
        "session_rollback_rule": ["requires_rollback_path", "rollback_visible"],
        "session_authorization_boundary": ["blocks_production_authorization"],
        "session_audit_summary": ["replay_mismatch_visible", "drift_visible", "boundary_visible", "rollback_visible", "invalidation_visible"],
    }
    return {
        row["session_label"]: [field for field in required.get(row["session_label"], []) if row.get(field) is not True]
        for row in rows
        if any(row.get(field) is not True for field in required.get(row["session_label"], []))
    }


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {row["session_label"]: sorted(set(row.get(key, [])) - allowed) for row in rows}
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())
