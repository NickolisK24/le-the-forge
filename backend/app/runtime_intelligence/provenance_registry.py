"""Registry validation for runtime provenance contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.provenance_contracts import (
    PROVENANCE_LABELS,
    build_runtime_provenance_manifest,
    order_provenance_contracts,
)
from app.runtime_intelligence.provenance_hashing import (
    hash_provenance_manifest,
    validate_provenance_replay_stability,
)


REQUIRED_PROVENANCE_FIELDS = (
    "provenance_type_id",
    "provenance_label",
    "deterministic_rank",
    "allowed_evidence_type_ids",
    "allowed_classification_ids",
    "source_required",
    "hash_required",
    "replay_safe",
    "drift_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_provenance_contracts(provenance_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("provenance_type_id")) for row in provenance_contracts)
    labels = Counter(str(row.get("provenance_label")) for row in provenance_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in provenance_contracts)
    return {
        "duplicate_provenance_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_provenance_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_provenance_registry(
    provenance_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ordered = order_provenance_contracts(provenance_contracts)
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    duplicate_detection = detect_duplicate_provenance_contracts(ordered)
    missing_required_fields = {
        str(row.get("provenance_label") or row.get("provenance_type_id") or index): [
            field for field in REQUIRED_PROVENANCE_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("provenance_label")) for row in ordered} - set(PROVENANCE_LABELS))
    invalid_evidence_references = {
        row["provenance_label"]: sorted(set(row.get("allowed_evidence_type_ids", [])) - evidence_type_ids)
        for row in ordered
    }
    invalid_evidence_references = {key: values for key, values in invalid_evidence_references.items() if values}
    invalid_classification_references = {
        row["provenance_label"]: sorted(set(row.get("allowed_classification_ids", [])) - classification_ids)
        for row in ordered
    }
    invalid_classification_references = {key: values for key, values in invalid_classification_references.items() if values}
    production_authorized = [row["provenance_label"] for row in ordered if row.get("production_authorized") is True]
    unsupported_visible = any(row.get("provenance_label") == "unsupported_source" for row in ordered)
    authorization_gate_visible = any(row.get("provenance_label") == "authorization_gate_source" for row in ordered)
    source_required = all(row.get("source_required") is True for row in ordered)
    hash_required = all(row.get("hash_required") is True for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_provenance_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_provenance_fields")
    if unknown_labels:
        validation_errors.append("unknown_provenance_labels")
    if invalid_evidence_references:
        validation_errors.append("invalid_evidence_references")
    if invalid_classification_references:
        validation_errors.append("invalid_classification_references")
    if production_authorized:
        validation_errors.append("production_authorized_provenance_detected")
    if not unsupported_visible:
        validation_errors.append("unsupported_provenance_not_visible")
    if not authorization_gate_visible:
        validation_errors.append("authorization_gate_provenance_not_visible")
    if not source_required:
        validation_errors.append("source_not_required_by_all_provenance_contracts")
    if not hash_required:
        validation_errors.append("hash_not_required_by_all_provenance_contracts")
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "invalid_evidence_references": invalid_evidence_references,
        "invalid_evidence_reference_count": sum(len(values) for values in invalid_evidence_references.values()),
        "invalid_classification_references": invalid_classification_references,
        "invalid_classification_reference_count": sum(len(values) for values in invalid_classification_references.values()),
        "production_authorized_provenance_contracts": production_authorized,
        "unsupported_provenance_visible": unsupported_visible,
        "authorization_gate_provenance_visible": authorization_gate_visible,
        "source_required_by_all_contracts": source_required,
        "hash_required_by_all_contracts": hash_required,
    }


def export_provenance_registry(
    provenance_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    classification_rows = classifications or default_runtime_intelligence_classifications()
    evidence_rows = evidence_contracts or default_runtime_evidence_contracts(classification_rows)
    manifest = build_runtime_provenance_manifest(
        provenance_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    validation = validate_provenance_registry(
        manifest["provenance_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
    )
    replay = validate_provenance_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_provenance_manifest(exported)
    return exported
