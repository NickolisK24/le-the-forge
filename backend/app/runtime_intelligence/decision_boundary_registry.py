"""Registry validation for runtime decision boundary contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.decision_boundary_contracts import (
    BOUNDARY_LABELS,
    VALID_BOUNDARY_ACTIONS,
    build_runtime_decision_boundary_manifest,
    order_decision_boundary_contracts,
)
from app.runtime_intelligence.decision_boundary_hashing import (
    hash_decision_boundary_manifest,
    validate_decision_boundary_replay_stability,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


REQUIRED_BOUNDARY_FIELDS = (
    "boundary_type_id",
    "boundary_label",
    "deterministic_rank",
    "allowed_classification_ids",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_reasoning_stage_ids",
    "allowed_explanation_type_ids",
    "allowed_confidence_type_ids",
    "allowed_synthesis_type_ids",
    "boundary_action",
    "blocks_downstream_reasoning",
    "blocks_synthesis_execution",
    "blocks_recommendation_logic",
    "blocks_production_authorization",
    "requires_manual_review",
    "requires_replay_validation",
    "requires_hash_validation",
    "preserves_conflicts",
    "preserves_drift",
    "preserves_unsupported",
    "preserves_blockers",
    "preserves_limitations",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_decision_boundary_contracts(boundary_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("boundary_type_id")) for row in boundary_contracts)
    labels = Counter(str(row.get("boundary_label")) for row in boundary_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in boundary_contracts)
    return {
        "duplicate_boundary_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_boundary_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_decision_boundary_registry(
    boundary_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    ordered = order_decision_boundary_contracts(boundary_contracts)
    duplicate_detection = detect_duplicate_decision_boundary_contracts(ordered)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    provenance_type_ids = {row["provenance_type_id"] for row in provenance_rows}
    reasoning_stage_ids = {row["stage_type_id"] for row in reasoning_rows}
    explanation_type_ids = {row["explanation_type_id"] for row in explanation_rows}
    confidence_type_ids = {row["confidence_type_id"] for row in confidence_rows}
    synthesis_type_ids = {row["synthesis_type_id"] for row in synthesis_rows}
    missing_required_fields = {
        str(row.get("boundary_label") or row.get("boundary_type_id") or index): [
            field for field in REQUIRED_BOUNDARY_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("boundary_label")) for row in ordered} - set(BOUNDARY_LABELS))
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", classification_ids)
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", evidence_type_ids)
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", provenance_type_ids)
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", reasoning_stage_ids)
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", explanation_type_ids)
    invalid_confidence_references = _invalid_refs(ordered, "allowed_confidence_type_ids", confidence_type_ids)
    invalid_synthesis_references = _invalid_refs(ordered, "allowed_synthesis_type_ids", synthesis_type_ids)
    invalid_boundary_actions = sorted(
        row["boundary_label"] for row in ordered if row.get("boundary_action") not in VALID_BOUNDARY_ACTIONS
    )
    behavior_rule_violations = _behavior_rule_violations(ordered)
    production_authorized = [row["boundary_label"] for row in ordered if row.get("production_authorized") is True]
    hard_stop_visible = any(row.get("boundary_action") == "hard_stop" for row in ordered)
    escalation_visible = any(row.get("boundary_action") == "escalation" for row in ordered)
    manual_review_visible = any(row.get("requires_manual_review") is True for row in ordered)
    recommendation_prohibited_visible = any(row.get("boundary_label") == "recommendation_prohibited_boundary" for row in ordered)
    production_prohibited_visible = any(row.get("blocks_production_authorization") is True for row in ordered)
    replay_mismatch_visible = any(row.get("boundary_label") == "replay_mismatch_stop" for row in ordered)
    confidence_ceiling_visible = any(row.get("boundary_label") == "confidence_ceiling_stop" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_decision_boundary_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_boundary_fields")
    if unknown_labels:
        validation_errors.append("unknown_boundary_labels")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if invalid_evidence_references:
        validation_errors.append("invalid_evidence_references")
    if invalid_provenance_references:
        validation_errors.append("invalid_provenance_references")
    if invalid_reasoning_stage_references:
        validation_errors.append("invalid_reasoning_stage_references")
    if invalid_explanation_references:
        validation_errors.append("invalid_explanation_references")
    if invalid_confidence_references:
        validation_errors.append("invalid_confidence_references")
    if invalid_synthesis_references:
        validation_errors.append("invalid_synthesis_references")
    if invalid_boundary_actions:
        validation_errors.append("invalid_boundary_actions")
    if behavior_rule_violations:
        validation_errors.append("boundary_behavior_rule_invalid")
    if production_authorized:
        validation_errors.append("production_authorized_boundary_detected")
    if not hard_stop_visible:
        validation_errors.append("hard_stop_boundary_not_visible")
    if not escalation_visible:
        validation_errors.append("escalation_boundary_not_visible")
    if not manual_review_visible:
        validation_errors.append("manual_review_boundary_not_visible")
    if not recommendation_prohibited_visible:
        validation_errors.append("recommendation_prohibited_boundary_not_visible")
    if not production_prohibited_visible:
        validation_errors.append("production_prohibited_boundary_not_visible")
    if not replay_mismatch_visible:
        validation_errors.append("replay_mismatch_boundary_not_visible")
    if not confidence_ceiling_visible:
        validation_errors.append("confidence_ceiling_boundary_not_visible")
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
        "invalid_boundary_actions": invalid_boundary_actions,
        "invalid_boundary_action_count": len(invalid_boundary_actions),
        "behavior_rule_violations": behavior_rule_violations,
        "behavior_rule_violation_count": len(behavior_rule_violations),
        "production_authorized_boundaries": production_authorized,
        "hard_stop_boundary_visible": hard_stop_visible,
        "escalation_boundary_visible": escalation_visible,
        "manual_review_boundary_visible": manual_review_visible,
        "recommendation_prohibited_boundary_visible": recommendation_prohibited_visible,
        "production_prohibited_boundary_visible": production_prohibited_visible,
        "replay_mismatch_boundary_visible": replay_mismatch_visible,
        "confidence_ceiling_boundary_visible": confidence_ceiling_visible,
    }


def export_decision_boundary_registry(
    boundary_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    reasoning_rows = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    explanation_rows = explanation_contracts or default_runtime_explanation_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    confidence_rows = confidence_contracts or default_runtime_confidence_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    synthesis_rows = synthesis_contracts or default_runtime_evidence_synthesis_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    manifest = build_runtime_decision_boundary_manifest(
        boundary_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
        synthesis_contracts=synthesis_rows,
    )
    validation = validate_decision_boundary_registry(
        manifest["boundary_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
        synthesis_contracts=synthesis_rows,
    )
    replay = validate_decision_boundary_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_decision_boundary_manifest(exported)
    return exported


def _behavior_rule_violations(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    required = {
        "unsupported_hard_stop": [("blocks_downstream_reasoning", True), ("preserves_unsupported", True)],
        "authorization_prohibited_hard_stop": [("blocks_production_authorization", True)],
        "production_routing_hard_stop": [("blocks_production_authorization", True)],
        "default_manifest_consumption_hard_stop": [("blocks_production_authorization", True)],
        "confidence_ceiling_stop": [("blocks_downstream_reasoning", True)],
        "replay_mismatch_stop": [("requires_replay_validation", True), ("blocks_downstream_reasoning", True)],
        "drift_detected_escalation": [("preserves_drift", True), ("boundary_action", "escalation")],
        "conflict_detected_escalation": [("preserves_conflicts", True), ("boundary_action", "escalation")],
        "provenance_incomplete_escalation": [("requires_manual_review", True), ("boundary_action", "escalation")],
        "blocker_detected_stop": [("preserves_blockers", True), ("blocks_downstream_reasoning", True)],
        "recommendation_prohibited_boundary": [("blocks_recommendation_logic", True)],
        "manual_review_required_boundary": [("requires_manual_review", True)],
    }
    violations = {}
    for row in rows:
        label = row.get("boundary_label")
        failed = [
            field
            for field, expected in required.get(label, [])
            if row.get(field) != expected
        ]
        if failed:
            violations[str(label)] = failed
    return violations


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {
        row["boundary_label"]: sorted(set(row.get(key, [])) - allowed)
        for row in rows
    }
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())
