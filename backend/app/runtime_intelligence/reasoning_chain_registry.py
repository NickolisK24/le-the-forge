"""Registry validation for runtime reasoning chain contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import (
    REASONING_STAGE_LABELS,
    build_runtime_reasoning_chain_manifest,
    order_reasoning_stage_contracts,
)
from app.runtime_intelligence.reasoning_chain_hashing import (
    hash_reasoning_chain_manifest,
    validate_reasoning_chain_replay_stability,
)


REQUIRED_REASONING_STAGE_FIELDS = (
    "stage_type_id",
    "stage_label",
    "deterministic_rank",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_classification_ids",
    "required_previous_stage_ids",
    "blocker_capable",
    "risk_capable",
    "limitation_capable",
    "replay_safe",
    "drift_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_reasoning_stage_contracts(reasoning_stage_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("stage_type_id")) for row in reasoning_stage_contracts)
    labels = Counter(str(row.get("stage_label")) for row in reasoning_stage_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in reasoning_stage_contracts)
    return {
        "duplicate_stage_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_stage_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_reasoning_chain_registry(
    reasoning_stage_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    ordered = order_reasoning_stage_contracts(reasoning_stage_contracts)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    provenance_type_ids = {row["provenance_type_id"] for row in provenance_rows}
    stage_ranks = {row.get("stage_type_id"): int(row.get("deterministic_rank", 0)) for row in ordered}
    stage_ids = set(stage_ranks)
    duplicate_detection = detect_duplicate_reasoning_stage_contracts(ordered)
    missing_required_fields = {
        str(row.get("stage_label") or row.get("stage_type_id") or index): [
            field for field in REQUIRED_REASONING_STAGE_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("stage_label")) for row in ordered} - set(REASONING_STAGE_LABELS))
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", evidence_type_ids)
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", provenance_type_ids)
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", classification_ids)
    invalid_previous_stage_references = _invalid_refs(ordered, "required_previous_stage_ids", stage_ids)
    previous_stage_rank_violations = {
        row["stage_label"]: [
            previous_id
            for previous_id in row.get("required_previous_stage_ids", [])
            if previous_id in stage_ranks and stage_ranks[previous_id] >= int(row["deterministic_rank"])
        ]
        for row in ordered
    }
    previous_stage_rank_violations = {key: values for key, values in previous_stage_rank_violations.items() if values}
    production_authorized = [row["stage_label"] for row in ordered if row.get("production_authorized") is True]
    blocker_visible = any(row.get("blocker_capable") is True for row in ordered)
    risk_visible = any(row.get("risk_capable") is True for row in ordered)
    limitation_visible = any(row.get("limitation_capable") is True for row in ordered)
    decision_boundary_visible = any(row.get("stage_label") == "decision_boundary_check" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_reasoning_stage_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_reasoning_stage_fields")
    if unknown_labels:
        validation_errors.append("unknown_reasoning_stage_labels")
    if invalid_evidence_references:
        validation_errors.append("invalid_evidence_references")
    if invalid_provenance_references:
        validation_errors.append("invalid_provenance_references")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if invalid_previous_stage_references:
        validation_errors.append("invalid_previous_stage_references")
    if previous_stage_rank_violations:
        validation_errors.append("previous_stage_rank_ordering_invalid")
    if production_authorized:
        validation_errors.append("production_authorized_reasoning_stage_detected")
    if not blocker_visible:
        validation_errors.append("blocker_capable_stage_not_visible")
    if not risk_visible:
        validation_errors.append("risk_capable_stage_not_visible")
    if not limitation_visible:
        validation_errors.append("limitation_capable_stage_not_visible")
    if not decision_boundary_visible:
        validation_errors.append("decision_boundary_stage_not_visible")
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
        "invalid_previous_stage_references": invalid_previous_stage_references,
        "invalid_previous_stage_reference_count": _count_refs(invalid_previous_stage_references),
        "previous_stage_rank_violations": previous_stage_rank_violations,
        "previous_stage_rank_violation_count": _count_refs(previous_stage_rank_violations),
        "production_authorized_reasoning_stages": production_authorized,
        "blocker_capable_stage_visible": blocker_visible,
        "risk_capable_stage_visible": risk_visible,
        "limitation_capable_stage_visible": limitation_visible,
        "decision_boundary_stage_visible": decision_boundary_visible,
    }


def export_reasoning_chain_registry(
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    provenance_rows = provenance_contracts or default_runtime_provenance_contracts(
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    manifest = build_runtime_reasoning_chain_manifest(
        reasoning_stage_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    validation = validate_reasoning_chain_registry(
        manifest["reasoning_stage_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
    )
    replay = validate_reasoning_chain_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_reasoning_chain_manifest(exported)
    return exported


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {
        row["stage_label"]: sorted(set(row.get(key, [])) - allowed)
        for row in rows
    }
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())
