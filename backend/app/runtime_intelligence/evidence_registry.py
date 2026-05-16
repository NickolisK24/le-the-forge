"""Registry validation for runtime evidence contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import (
    EVIDENCE_LABELS,
    build_runtime_evidence_manifest,
    order_evidence_contracts,
)
from app.runtime_intelligence.evidence_hashing import hash_evidence_manifest, validate_evidence_replay_stability


REQUIRED_EVIDENCE_FIELDS = (
    "evidence_type_id",
    "evidence_label",
    "deterministic_rank",
    "allowed_classification_ids",
    "provenance_required",
    "source_required",
    "replay_safe",
    "drift_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_evidence_contracts(evidence_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("evidence_type_id")) for row in evidence_contracts)
    labels = Counter(str(row.get("evidence_label")) for row in evidence_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in evidence_contracts)
    return {
        "duplicate_evidence_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_evidence_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_evidence_registry(
    evidence_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ordered = order_evidence_contracts(evidence_contracts)
    classification_rows = classifications or default_runtime_intelligence_classifications()
    classification_ids = {row["classification_id"] for row in classification_rows}
    duplicate_detection = detect_duplicate_evidence_contracts(ordered)
    missing_required_fields = {
        str(row.get("evidence_label") or row.get("evidence_type_id") or index): [
            field for field in REQUIRED_EVIDENCE_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("evidence_label")) for row in ordered} - set(EVIDENCE_LABELS))
    invalid_classification_references = {
        row["evidence_label"]: sorted(set(row.get("allowed_classification_ids", [])) - classification_ids)
        for row in ordered
    }
    invalid_classification_references = {key: values for key, values in invalid_classification_references.items() if values}
    production_authorized = [row["evidence_label"] for row in ordered if row.get("production_authorized") is True]
    unsupported_visible = _has_allowed_label(ordered, classification_rows, "unsupported")
    authorization_prohibited_visible = _has_allowed_label(ordered, classification_rows, "authorization_prohibited")
    provenance_required = all(row.get("provenance_required") is True for row in ordered)
    source_required = all(row.get("source_required") is True for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_evidence_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_evidence_fields")
    if unknown_labels:
        validation_errors.append("unknown_evidence_labels")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if production_authorized:
        validation_errors.append("production_authorized_evidence_detected")
    if not unsupported_visible:
        validation_errors.append("unsupported_evidence_not_visible")
    if not authorization_prohibited_visible:
        validation_errors.append("authorization_prohibited_evidence_not_visible")
    if not provenance_required:
        validation_errors.append("provenance_not_required_by_all_evidence_contracts")
    if not source_required:
        validation_errors.append("source_not_required_by_all_evidence_contracts")
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_classification_references": invalid_classification_references,
        "invalid_classification_reference_count": sum(len(values) for values in invalid_classification_references.values()),
        "production_authorized_evidence_contracts": production_authorized,
        "unsupported_evidence_visible": unsupported_visible,
        "authorization_prohibited_evidence_visible": authorization_prohibited_visible,
        "provenance_required_by_all_contracts": provenance_required,
        "source_required_by_all_contracts": source_required,
    }


def export_evidence_registry(
    evidence_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    manifest = build_runtime_evidence_manifest(evidence_contracts, classifications=classification_rows)
    validation = validate_evidence_registry(manifest["evidence_contracts"], classifications=classification_rows)
    replay = validate_evidence_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_evidence_manifest(exported)
    return exported


def _has_allowed_label(
    evidence_contracts: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    classification_label: str,
) -> bool:
    ids_by_label = {row["classification_label"]: row["classification_id"] for row in classifications}
    target_id = ids_by_label.get(classification_label)
    return bool(target_id) and any(target_id in row.get("allowed_classification_ids", []) for row in evidence_contracts)
