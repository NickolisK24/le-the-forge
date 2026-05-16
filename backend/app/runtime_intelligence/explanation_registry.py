"""Registry validation for runtime explanation contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_contracts import (
    EXPLANATION_LABELS,
    build_runtime_explanation_manifest,
    order_explanation_contracts,
)
from app.runtime_intelligence.explanation_hashing import (
    hash_explanation_manifest,
    validate_explanation_replay_stability,
)
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


REQUIRED_EXPLANATION_FIELDS = (
    "explanation_type_id",
    "explanation_label",
    "deterministic_rank",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_classification_ids",
    "allowed_reasoning_stage_ids",
    "required_explanation_sections",
    "blocker_visible",
    "risk_visible",
    "limitation_visible",
    "confidence_visible",
    "replay_safe",
    "drift_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_explanation_contracts(explanation_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("explanation_type_id")) for row in explanation_contracts)
    labels = Counter(str(row.get("explanation_label")) for row in explanation_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in explanation_contracts)
    return {
        "duplicate_explanation_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_explanation_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_explanation_registry(
    explanation_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
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
    ordered = order_explanation_contracts(explanation_contracts)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    provenance_type_ids = {row["provenance_type_id"] for row in provenance_rows}
    reasoning_stage_ids = {row["stage_type_id"] for row in reasoning_rows}
    duplicate_detection = detect_duplicate_explanation_contracts(ordered)
    missing_required_fields = {
        str(row.get("explanation_label") or row.get("explanation_type_id") or index): [
            field for field in REQUIRED_EXPLANATION_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("explanation_label")) for row in ordered} - set(EXPLANATION_LABELS))
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", evidence_type_ids)
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", provenance_type_ids)
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", classification_ids)
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", reasoning_stage_ids)
    required_section_violations = {
        row["explanation_label"]: row.get("required_explanation_sections", [])
        for row in ordered
        if not _sections_valid(row.get("required_explanation_sections", []))
    }
    production_authorized = [row["explanation_label"] for row in ordered if row.get("production_authorized") is True]
    blocker_visible = any(row.get("blocker_visible") is True for row in ordered)
    risk_visible = any(row.get("risk_visible") is True for row in ordered)
    limitation_visible = any(row.get("limitation_visible") is True for row in ordered)
    confidence_visible = any(row.get("confidence_visible") is True for row in ordered)
    unsupported_visible = any(row.get("explanation_label") == "unsupported_summary" for row in ordered)
    decision_boundary_visible = any(row.get("explanation_label") == "decision_boundary_summary" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_explanation_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_explanation_fields")
    if unknown_labels:
        validation_errors.append("unknown_explanation_labels")
    if invalid_evidence_references:
        validation_errors.append("invalid_evidence_references")
    if invalid_provenance_references:
        validation_errors.append("invalid_provenance_references")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if invalid_reasoning_stage_references:
        validation_errors.append("invalid_reasoning_stage_references")
    if required_section_violations:
        validation_errors.append("required_explanation_sections_invalid")
    if production_authorized:
        validation_errors.append("production_authorized_explanation_detected")
    if not blocker_visible:
        validation_errors.append("blocker_visible_explanation_not_visible")
    if not risk_visible:
        validation_errors.append("risk_visible_explanation_not_visible")
    if not limitation_visible:
        validation_errors.append("limitation_visible_explanation_not_visible")
    if not confidence_visible:
        validation_errors.append("confidence_visible_explanation_not_visible")
    if not unsupported_visible:
        validation_errors.append("unsupported_explanation_not_visible")
    if not decision_boundary_visible:
        validation_errors.append("decision_boundary_explanation_not_visible")
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_evidence_references": invalid_evidence_references,
        "invalid_evidence_reference_count": _count_refs(invalid_evidence_references),
        "invalid_provenance_references": invalid_provenance_references,
        "invalid_provenance_reference_count": _count_refs(invalid_provenance_references),
        "invalid_classification_references": invalid_classification_references,
        "invalid_classification_reference_count": _count_refs(invalid_classification_references),
        "invalid_reasoning_stage_references": invalid_reasoning_stage_references,
        "invalid_reasoning_stage_reference_count": _count_refs(invalid_reasoning_stage_references),
        "required_section_violations": required_section_violations,
        "required_section_violation_count": len(required_section_violations),
        "production_authorized_explanations": production_authorized,
        "blocker_visible_explanation_visible": blocker_visible,
        "risk_visible_explanation_visible": risk_visible,
        "limitation_visible_explanation_visible": limitation_visible,
        "confidence_visible_explanation_visible": confidence_visible,
        "unsupported_explanation_visible": unsupported_visible,
        "decision_boundary_explanation_visible": decision_boundary_visible,
    }


def export_explanation_registry(
    explanation_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
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
    manifest = build_runtime_explanation_manifest(
        explanation_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    validation = validate_explanation_registry(
        manifest["explanation_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
    )
    replay = validate_explanation_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_explanation_manifest(exported)
    return exported


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {
        row["explanation_label"]: sorted(set(row.get(key, [])) - allowed)
        for row in rows
    }
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())


def _sections_valid(sections: Any) -> bool:
    if not isinstance(sections, list) or not sections:
        return False
    if any(not isinstance(section, str) or not section.strip() for section in sections):
        return False
    return sections == sorted(set(sections))
