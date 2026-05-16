"""Registry validation for runtime evidence synthesis contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import (
    PRESERVATION_RULES,
    SYNTHESIS_LABELS,
    build_runtime_evidence_synthesis_manifest,
    order_evidence_synthesis_contracts,
)
from app.runtime_intelligence.evidence_synthesis_hashing import (
    hash_evidence_synthesis_manifest,
    validate_evidence_synthesis_replay_stability,
)
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


REQUIRED_SYNTHESIS_FIELDS = (
    "synthesis_type_id",
    "synthesis_label",
    "deterministic_rank",
    "allowed_input_evidence_type_ids",
    "allowed_output_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_classification_ids",
    "allowed_confidence_type_ids",
    "allowed_reasoning_stage_ids",
    "allowed_explanation_type_ids",
    "minimum_input_count",
    "maximum_input_count",
    "preserves_conflicts",
    "preserves_drift",
    "preserves_unsupported",
    "preserves_blockers",
    "preserves_limitations",
    "preserves_provenance",
    "requires_replay_validation",
    "requires_hash_validation",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_evidence_synthesis_contracts(synthesis_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("synthesis_type_id")) for row in synthesis_contracts)
    labels = Counter(str(row.get("synthesis_label")) for row in synthesis_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in synthesis_contracts)
    return {
        "duplicate_synthesis_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_synthesis_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_evidence_synthesis_registry(
    synthesis_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
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
    ordered = order_evidence_synthesis_contracts(synthesis_contracts)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    provenance_type_ids = {row["provenance_type_id"] for row in provenance_rows}
    reasoning_stage_ids = {row["stage_type_id"] for row in reasoning_rows}
    explanation_type_ids = {row["explanation_type_id"] for row in explanation_rows}
    confidence_type_ids = {row["confidence_type_id"] for row in confidence_rows}
    duplicate_detection = detect_duplicate_evidence_synthesis_contracts(ordered)
    missing_required_fields = {
        str(row.get("synthesis_label") or row.get("synthesis_type_id") or index): [
            field for field in REQUIRED_SYNTHESIS_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("synthesis_label")) for row in ordered} - set(SYNTHESIS_LABELS))
    invalid_input_evidence_references = _invalid_refs(ordered, "allowed_input_evidence_type_ids", evidence_type_ids)
    invalid_output_evidence_references = _invalid_refs(ordered, "allowed_output_evidence_type_ids", evidence_type_ids)
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", provenance_type_ids)
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", classification_ids)
    invalid_confidence_references = _invalid_refs(ordered, "allowed_confidence_type_ids", confidence_type_ids)
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", reasoning_stage_ids)
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", explanation_type_ids)
    input_count_violations = {
        row["synthesis_label"]: {
            "minimum_input_count": row.get("minimum_input_count"),
            "maximum_input_count": row.get("maximum_input_count"),
        }
        for row in ordered
        if not _input_counts_valid(row)
    }
    preservation_rule_violations = {
        row["synthesis_label"]: PRESERVATION_RULES[row["synthesis_label"]]
        for row in ordered
        if row.get("synthesis_label") in PRESERVATION_RULES
        and row.get(PRESERVATION_RULES[row["synthesis_label"]]) is not True
    }
    replay_rule_violations = sorted(
        row["synthesis_label"]
        for row in ordered
        if row.get("synthesis_label") == "replay_verified_merge"
        and row.get("requires_replay_validation") is not True
    )
    production_authorized = [row["synthesis_label"] for row in ordered if row.get("production_authorized") is True]
    conflict_preserving_visible = any(row.get("preserves_conflicts") is True for row in ordered)
    drift_preserving_visible = any(row.get("preserves_drift") is True for row in ordered)
    unsupported_preserving_visible = any(row.get("preserves_unsupported") is True for row in ordered)
    blocker_preserving_visible = any(row.get("preserves_blockers") is True for row in ordered)
    limitation_preserving_visible = any(row.get("preserves_limitations") is True for row in ordered)
    provenance_preserving_visible = any(row.get("preserves_provenance") is True for row in ordered)
    decision_boundary_preserving_visible = any(row.get("synthesis_label") == "decision_boundary_preserving_merge" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_synthesis_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_synthesis_fields")
    if unknown_labels:
        validation_errors.append("unknown_synthesis_labels")
    if invalid_input_evidence_references:
        validation_errors.append("invalid_input_evidence_references")
    if invalid_output_evidence_references:
        validation_errors.append("invalid_output_evidence_references")
    if invalid_provenance_references:
        validation_errors.append("invalid_provenance_references")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if invalid_confidence_references:
        validation_errors.append("invalid_confidence_references")
    if invalid_reasoning_stage_references:
        validation_errors.append("invalid_reasoning_stage_references")
    if invalid_explanation_references:
        validation_errors.append("invalid_explanation_references")
    if input_count_violations:
        validation_errors.append("input_output_count_invalid")
    if preservation_rule_violations or replay_rule_violations:
        validation_errors.append("preservation_rule_invalid")
    if production_authorized:
        validation_errors.append("production_authorized_synthesis_detected")
    if not conflict_preserving_visible:
        validation_errors.append("conflict_preserving_synthesis_not_visible")
    if not drift_preserving_visible:
        validation_errors.append("drift_preserving_synthesis_not_visible")
    if not unsupported_preserving_visible:
        validation_errors.append("unsupported_preserving_synthesis_not_visible")
    if not blocker_preserving_visible:
        validation_errors.append("blocker_preserving_synthesis_not_visible")
    if not limitation_preserving_visible:
        validation_errors.append("limitation_preserving_synthesis_not_visible")
    if not provenance_preserving_visible:
        validation_errors.append("provenance_preserving_synthesis_not_visible")
    if not decision_boundary_preserving_visible:
        validation_errors.append("decision_boundary_preserving_synthesis_not_visible")
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_input_evidence_references": invalid_input_evidence_references,
        "invalid_input_evidence_reference_count": _count_refs(invalid_input_evidence_references),
        "invalid_output_evidence_references": invalid_output_evidence_references,
        "invalid_output_evidence_reference_count": _count_refs(invalid_output_evidence_references),
        "invalid_provenance_references": invalid_provenance_references,
        "invalid_provenance_reference_count": _count_refs(invalid_provenance_references),
        "invalid_classification_references": invalid_classification_references,
        "invalid_classification_reference_count": _count_refs(invalid_classification_references),
        "invalid_confidence_references": invalid_confidence_references,
        "invalid_confidence_reference_count": _count_refs(invalid_confidence_references),
        "invalid_reasoning_stage_references": invalid_reasoning_stage_references,
        "invalid_reasoning_stage_reference_count": _count_refs(invalid_reasoning_stage_references),
        "invalid_explanation_references": invalid_explanation_references,
        "invalid_explanation_reference_count": _count_refs(invalid_explanation_references),
        "input_count_violations": input_count_violations,
        "input_count_violation_count": len(input_count_violations),
        "preservation_rule_violations": preservation_rule_violations,
        "preservation_rule_violation_count": len(preservation_rule_violations) + len(replay_rule_violations),
        "replay_rule_violations": replay_rule_violations,
        "production_authorized_syntheses": production_authorized,
        "conflict_preserving_synthesis_visible": conflict_preserving_visible,
        "drift_preserving_synthesis_visible": drift_preserving_visible,
        "unsupported_preserving_synthesis_visible": unsupported_preserving_visible,
        "blocker_preserving_synthesis_visible": blocker_preserving_visible,
        "limitation_preserving_synthesis_visible": limitation_preserving_visible,
        "provenance_preserving_synthesis_visible": provenance_preserving_visible,
        "decision_boundary_preserving_synthesis_visible": decision_boundary_preserving_visible,
    }


def export_evidence_synthesis_registry(
    synthesis_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
    confidence_contracts: list[dict[str, Any]] | None = None,
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
    manifest = build_runtime_evidence_synthesis_manifest(
        synthesis_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    validation = validate_evidence_synthesis_registry(
        manifest["synthesis_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
        confidence_contracts=confidence_rows,
    )
    replay = validate_evidence_synthesis_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_evidence_synthesis_manifest(exported)
    return exported


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {
        row["synthesis_label"]: sorted(set(row.get(key, [])) - allowed)
        for row in rows
    }
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())


def _input_counts_valid(row: dict[str, Any]) -> bool:
    minimum = row.get("minimum_input_count")
    maximum = row.get("maximum_input_count")
    if not isinstance(minimum, int) or not isinstance(maximum, int):
        return False
    return minimum >= 1 and maximum >= minimum
