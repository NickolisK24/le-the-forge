"""Validation registry for runtime intelligence classifications."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import (
    CLASSIFICATION_LABELS,
    build_runtime_intelligence_classification_manifest,
    order_classifications,
)
from app.runtime_intelligence.classification_hashing import hash_classification_manifest, validate_replay_stability


REQUIRED_FIELDS = (
    "classification_id",
    "classification_label",
    "deterministic_rank",
    "trust_state",
    "replay_safe",
    "production_authorized",
    "drift_visible",
    "provenance_required",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_classifications(classifications: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("classification_id")) for row in classifications)
    labels = Counter(str(row.get("classification_label")) for row in classifications)
    ranks = Counter(str(row.get("deterministic_rank")) for row in classifications)
    return {
        "duplicate_classification_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_classification_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_classification_registry(classifications: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = order_classifications(classifications)
    duplicate_detection = detect_duplicate_classifications(ordered)
    missing_required_fields = {
        str(row.get("classification_label") or row.get("classification_id") or index): [
            field for field in REQUIRED_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("classification_label")) for row in ordered} - set(CLASSIFICATION_LABELS))
    production_authorized = [row["classification_label"] for row in ordered if row.get("production_authorized") is True]
    unsupported_visible = any(row.get("classification_label") == "unsupported" for row in ordered)
    authorization_prohibited_visible = any(row.get("classification_label") == "authorization_prohibited" for row in ordered)
    provenance_incomplete_visible = any(row.get("classification_label") == "provenance_incomplete" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_classifications_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_classification_fields")
    if unknown_labels:
        validation_errors.append("unknown_classification_labels")
    if production_authorized:
        validation_errors.append("production_authorized_classification_detected")
    if not unsupported_visible:
        validation_errors.append("unsupported_classification_not_visible")
    if not authorization_prohibited_visible:
        validation_errors.append("authorization_prohibited_classification_not_visible")
    if not provenance_incomplete_visible:
        validation_errors.append("provenance_incomplete_classification_not_visible")
    return {
        "valid": not validation_errors,
        "validation_errors": validation_errors,
        "duplicate_detection": duplicate_detection,
        "missing_required_fields": missing_required_fields,
        "unknown_labels": unknown_labels,
        "production_authorized_classifications": production_authorized,
        "unsupported_classification_visible": unsupported_visible,
        "authorization_prohibited_classification_visible": authorization_prohibited_visible,
        "provenance_incomplete_classification_visible": provenance_incomplete_visible,
    }


def export_classification_registry(classifications: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    manifest = build_runtime_intelligence_classification_manifest(classifications)
    validation = validate_classification_registry(manifest["classifications"])
    replay = validate_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_classification_manifest(exported)
    return exported
