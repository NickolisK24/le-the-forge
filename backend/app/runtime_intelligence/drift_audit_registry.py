"""Registry validation for runtime drift audit contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.drift_audit_contracts import (
    DRIFT_LABELS,
    VALID_DRIFT_ACTIONS,
    VALID_DRIFT_CATEGORIES,
    build_runtime_drift_audit_manifest,
    default_runtime_drift_audit_contracts,
    order_drift_audit_contracts,
    _resolve_deps,
)
from app.runtime_intelligence.drift_audit_hashing import (
    hash_drift_audit_manifest,
    validate_drift_audit_replay_stability,
)


REQUIRED_DRIFT_FIELDS = (
    "drift_type_id",
    "drift_label",
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
    "drift_category",
    "drift_action",
    "requires_baseline_hash",
    "requires_current_hash",
    "requires_diff_summary",
    "requires_replay_validation",
    "requires_manual_review",
    "blocks_confidence_upgrade",
    "blocks_production_authorization",
    "preserves_drift",
    "preserves_conflicts",
    "preserves_unsupported",
    "preserves_blockers",
    "boundary_visible",
    "replay_mismatch_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_drift_audit_contracts(drift_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("drift_type_id")) for row in drift_contracts)
    labels = Counter(str(row.get("drift_label")) for row in drift_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in drift_contracts)
    return {
        "duplicate_drift_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_drift_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_drift_audit_registry(drift_contracts: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    deps = _resolve_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
    )
    ordered = order_drift_audit_contracts(drift_contracts)
    duplicate_detection = detect_duplicate_drift_audit_contracts(ordered)
    missing_required_fields = {
        str(row.get("drift_label") or row.get("drift_type_id") or index): [
            field for field in REQUIRED_DRIFT_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("drift_label")) for row in ordered} - set(DRIFT_LABELS))
    invalid_categories = sorted(row["drift_label"] for row in ordered if row.get("drift_category") not in VALID_DRIFT_CATEGORIES)
    invalid_actions = sorted(row["drift_label"] for row in ordered if row.get("drift_action") not in VALID_DRIFT_ACTIONS)
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", {row["classification_id"] for row in deps["classifications"]})
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", {row["evidence_type_id"] for row in deps["evidence"]})
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", {row["provenance_type_id"] for row in deps["provenance"]})
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", {row["stage_type_id"] for row in deps["reasoning"]})
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", {row["explanation_type_id"] for row in deps["explanations"]})
    invalid_confidence_references = _invalid_refs(ordered, "allowed_confidence_type_ids", {row["confidence_type_id"] for row in deps["confidence"]})
    invalid_synthesis_references = _invalid_refs(ordered, "allowed_synthesis_type_ids", {row["synthesis_type_id"] for row in deps["synthesis"]})
    invalid_boundary_references = _invalid_refs(ordered, "allowed_boundary_type_ids", {row["boundary_type_id"] for row in deps["boundaries"]})
    invalid_replay_references = _invalid_refs(ordered, "allowed_replay_type_ids", {row["replay_type_id"] for row in deps["replay"]})
    behavior_rule_violations = _behavior_rule_violations(ordered)
    production_authorized = [row["drift_label"] for row in ordered if row.get("production_authorized") is True]
    validation_errors = []
    checks = [
        (any(duplicate_detection.values()), "duplicate_drift_audit_contracts_detected"),
        (missing_required_fields, "missing_required_drift_fields"),
        (unknown_labels, "unknown_drift_labels"),
        (invalid_categories, "invalid_drift_categories"),
        (invalid_actions, "invalid_drift_actions"),
        (invalid_classification_references, "invalid_classification_references"),
        (invalid_evidence_references, "invalid_evidence_references"),
        (invalid_provenance_references, "invalid_provenance_references"),
        (invalid_reasoning_stage_references, "invalid_reasoning_stage_references"),
        (invalid_explanation_references, "invalid_explanation_references"),
        (invalid_confidence_references, "invalid_confidence_references"),
        (invalid_synthesis_references, "invalid_synthesis_references"),
        (invalid_boundary_references, "invalid_boundary_references"),
        (invalid_replay_references, "invalid_replay_references"),
        (behavior_rule_violations, "drift_behavior_rule_invalid"),
        (production_authorized, "production_authorized_drift_audit_detected"),
    ]
    validation_errors = [error for condition, error in checks if condition]
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_drift_categories": invalid_categories,
        "invalid_drift_category_count": len(invalid_categories),
        "invalid_drift_actions": invalid_actions,
        "invalid_drift_action_count": len(invalid_actions),
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
        "behavior_rule_violations": behavior_rule_violations,
        "behavior_rule_violation_count": len(behavior_rule_violations),
        "production_authorized_drift_audits": production_authorized,
    }


def export_drift_audit_registry(drift_contracts: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    deps = _resolve_deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
        kwargs.get("replay_contracts"),
    )
    contracts = drift_contracts or default_runtime_drift_audit_contracts(
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
        replay_contracts=deps["replay"],
    )
    manifest = build_runtime_drift_audit_manifest(
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
    )
    validation = validate_drift_audit_registry(
        manifest["drift_contracts"],
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
        replay_contracts=deps["replay"],
    )
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = validate_drift_audit_replay_stability(manifest)
    exported["deterministic_hash"] = hash_drift_audit_manifest(exported)
    return exported


def _behavior_rule_violations(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    required = {
        "production_authorization_drift": ["blocks_production_authorization"],
        "confidence_boundary_drift": ["blocks_confidence_upgrade"],
        "unsupported_state_drift": ["preserves_unsupported"],
        "replay_sequence_drift": ["requires_replay_validation", "replay_mismatch_visible"],
        "hash_manifest_drift": ["requires_baseline_hash", "requires_current_hash"],
        "patch_version_drift": ["requires_diff_summary"],
        "provenance_lineage_drift": ["requires_manual_review"],
        "decision_boundary_drift": ["boundary_visible"],
    }
    return {
        row["drift_label"]: [field for field in required.get(row["drift_label"], []) if row.get(field) is not True]
        for row in rows
        if any(row.get(field) is not True for field in required.get(row["drift_label"], []))
    }


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {row["drift_label"]: sorted(set(row.get(key, [])) - allowed) for row in rows}
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())
