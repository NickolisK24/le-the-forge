"""Registry validation for runtime replay orchestration contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.decision_boundary_contracts import default_runtime_decision_boundary_contracts
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from app.runtime_intelligence.replay_orchestration_contracts import (
    REPLAY_LABELS,
    build_runtime_replay_orchestration_manifest,
    order_replay_orchestration_contracts,
)
from app.runtime_intelligence.replay_orchestration_hashing import (
    hash_replay_orchestration_manifest,
    validate_replay_orchestration_replay_stability,
)


REQUIRED_REPLAY_FIELDS = (
    "replay_type_id",
    "replay_label",
    "deterministic_rank",
    "allowed_classification_ids",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_reasoning_stage_ids",
    "allowed_explanation_type_ids",
    "allowed_confidence_type_ids",
    "allowed_synthesis_type_ids",
    "allowed_boundary_type_ids",
    "required_previous_replay_type_ids",
    "requires_input_hash",
    "requires_output_hash",
    "requires_sequence_hash",
    "mismatch_visible",
    "drift_visible",
    "conflict_visible",
    "blocker_visible",
    "boundary_visible",
    "reproducibility_required",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_replay_orchestration_contracts(replay_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("replay_type_id")) for row in replay_contracts)
    labels = Counter(str(row.get("replay_label")) for row in replay_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in replay_contracts)
    return {
        "duplicate_replay_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_replay_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_replay_orchestration_registry(
    replay_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
    synthesis_contracts: list[dict[str, Any]] | None = None,
    boundary_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    deps = _deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts)
    ordered = order_replay_orchestration_contracts(replay_contracts)
    replay_ranks = {row.get("replay_type_id"): int(row.get("deterministic_rank", 0)) for row in ordered}
    replay_ids = set(replay_ranks)
    duplicate_detection = detect_duplicate_replay_orchestration_contracts(ordered)
    missing_required_fields = {
        str(row.get("replay_label") or row.get("replay_type_id") or index): [
            field for field in REQUIRED_REPLAY_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("replay_label")) for row in ordered} - set(REPLAY_LABELS))
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", {row["classification_id"] for row in deps["classifications"]})
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", {row["evidence_type_id"] for row in deps["evidence"]})
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", {row["provenance_type_id"] for row in deps["provenance"]})
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", {row["stage_type_id"] for row in deps["reasoning"]})
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", {row["explanation_type_id"] for row in deps["explanations"]})
    invalid_confidence_references = _invalid_refs(ordered, "allowed_confidence_type_ids", {row["confidence_type_id"] for row in deps["confidence"]})
    invalid_synthesis_references = _invalid_refs(ordered, "allowed_synthesis_type_ids", {row["synthesis_type_id"] for row in deps["synthesis"]})
    invalid_boundary_references = _invalid_refs(ordered, "allowed_boundary_type_ids", {row["boundary_type_id"] for row in deps["boundaries"]})
    invalid_previous_replay_references = _invalid_refs(ordered, "required_previous_replay_type_ids", replay_ids)
    previous_rank_violations = {
        row["replay_label"]: [
            previous_id for previous_id in row.get("required_previous_replay_type_ids", [])
            if previous_id in replay_ranks and replay_ranks[previous_id] >= int(row["deterministic_rank"])
        ]
        for row in ordered
    }
    previous_rank_violations = {key: values for key, values in previous_rank_violations.items() if values}
    hash_requirement_violations = _hash_requirement_violations(ordered)
    visibility_rule_violations = _visibility_rule_violations(ordered)
    production_authorized = [row["replay_label"] for row in ordered if row.get("production_authorized") is True]
    validation_errors = []
    checks = [
        (any(duplicate_detection.values()), "duplicate_replay_orchestration_contracts_detected"),
        (missing_required_fields, "missing_required_replay_fields"),
        (unknown_labels, "unknown_replay_labels"),
        (invalid_classification_references, "invalid_classification_references"),
        (invalid_evidence_references, "invalid_evidence_references"),
        (invalid_provenance_references, "invalid_provenance_references"),
        (invalid_reasoning_stage_references, "invalid_reasoning_stage_references"),
        (invalid_explanation_references, "invalid_explanation_references"),
        (invalid_confidence_references, "invalid_confidence_references"),
        (invalid_synthesis_references, "invalid_synthesis_references"),
        (invalid_boundary_references, "invalid_boundary_references"),
        (invalid_previous_replay_references, "invalid_previous_replay_references"),
        (previous_rank_violations, "previous_replay_rank_ordering_invalid"),
        (hash_requirement_violations, "hash_requirement_invalid"),
        (visibility_rule_violations, "visibility_rule_invalid"),
        (production_authorized, "production_authorized_replay_orchestration_detected"),
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
        "invalid_previous_replay_references": invalid_previous_replay_references,
        "invalid_previous_replay_reference_count": _count_refs(invalid_previous_replay_references),
        "previous_replay_rank_violations": previous_rank_violations,
        "previous_replay_rank_violation_count": _count_refs(previous_rank_violations),
        "hash_requirement_violations": hash_requirement_violations,
        "hash_requirement_violation_count": len(hash_requirement_violations),
        "visibility_rule_violations": visibility_rule_violations,
        "visibility_rule_violation_count": len(visibility_rule_violations),
        "production_authorized_replay_orchestrations": production_authorized,
    }


def export_replay_orchestration_registry(replay_contracts: list[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    deps = _deps(
        kwargs.get("classifications"),
        kwargs.get("evidence_contracts"),
        kwargs.get("provenance_contracts"),
        kwargs.get("reasoning_stage_contracts"),
        kwargs.get("explanation_contracts"),
        kwargs.get("confidence_contracts"),
        kwargs.get("synthesis_contracts"),
        kwargs.get("boundary_contracts"),
    )
    manifest = build_runtime_replay_orchestration_manifest(
        replay_contracts,
        classifications=deps["classifications"],
        evidence_contracts=deps["evidence"],
        provenance_contracts=deps["provenance"],
        reasoning_stage_contracts=deps["reasoning"],
        explanation_contracts=deps["explanations"],
        confidence_contracts=deps["confidence"],
        synthesis_contracts=deps["synthesis"],
        boundary_contracts=deps["boundaries"],
    )
    validation = validate_replay_orchestration_registry(manifest["replay_contracts"], **{
        "classifications": deps["classifications"],
        "evidence_contracts": deps["evidence"],
        "provenance_contracts": deps["provenance"],
        "reasoning_stage_contracts": deps["reasoning"],
        "explanation_contracts": deps["explanations"],
        "confidence_contracts": deps["confidence"],
        "synthesis_contracts": deps["synthesis"],
        "boundary_contracts": deps["boundaries"],
    })
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = validate_replay_orchestration_replay_stability(manifest)
    exported["deterministic_hash"] = hash_replay_orchestration_manifest(exported)
    return exported


def _deps(classifications, evidence_contracts, provenance_contracts, reasoning_stage_contracts, explanation_contracts, confidence_contracts, synthesis_contracts, boundary_contracts):
    c = classifications or default_runtime_intelligence_classifications()
    e = evidence_contracts or default_runtime_evidence_contracts(c)
    p = provenance_contracts or default_runtime_provenance_contracts(classifications=c, evidence_contracts=e)
    r = reasoning_stage_contracts or default_runtime_reasoning_chain_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p)
    x = explanation_contracts or default_runtime_explanation_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r)
    k = confidence_contracts or default_runtime_confidence_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x)
    s = synthesis_contracts or default_runtime_evidence_synthesis_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x, confidence_contracts=k)
    b = boundary_contracts or default_runtime_decision_boundary_contracts(classifications=c, evidence_contracts=e, provenance_contracts=p, reasoning_stage_contracts=r, explanation_contracts=x, confidence_contracts=k, synthesis_contracts=s)
    return {"classifications": c, "evidence": e, "provenance": p, "reasoning": r, "explanations": x, "confidence": k, "synthesis": s, "boundaries": b}


def _hash_requirement_violations(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    required = {
        "replay_session_identity": ["requires_input_hash", "reproducibility_required"],
        "replay_input_manifest": ["requires_input_hash"],
        "replay_audit_summary": ["requires_output_hash", "requires_sequence_hash"],
        "replay_reproducibility_boundary": ["reproducibility_required", "boundary_visible"],
    }
    return {row["replay_label"]: [field for field in required.get(row["replay_label"], []) if row.get(field) is not True] for row in rows if any(row.get(field) is not True for field in required.get(row["replay_label"], []))}


def _visibility_rule_violations(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    required = {
        "replay_mismatch_detection": ["mismatch_visible"],
        "replay_synthesis_sequence": ["drift_visible", "conflict_visible"],
        "replay_confidence_sequence": ["blocker_visible"],
        "replay_boundary_sequence": ["boundary_visible", "blocker_visible"],
        "replay_reproducibility_boundary": ["boundary_visible", "mismatch_visible"],
    }
    return {row["replay_label"]: [field for field in required.get(row["replay_label"], []) if row.get(field) is not True] for row in rows if any(row.get(field) is not True for field in required.get(row["replay_label"], []))}


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {row["replay_label"]: sorted(set(row.get(key, [])) - allowed) for row in rows}
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())


from app.runtime_intelligence.replay_orchestration_contracts import build_runtime_replay_orchestration_manifest
