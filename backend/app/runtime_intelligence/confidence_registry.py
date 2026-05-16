"""Registry validation for runtime confidence contracts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import (
    CONFIDENCE_LABELS,
    NON_UPGRADEABLE_CONFIDENCE_LABELS,
    build_runtime_confidence_manifest,
    order_confidence_contracts,
)
from app.runtime_intelligence.confidence_hashing import (
    hash_confidence_manifest,
    validate_confidence_replay_stability,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts


REQUIRED_CONFIDENCE_FIELDS = (
    "confidence_type_id",
    "confidence_label",
    "deterministic_rank",
    "allowed_classification_ids",
    "allowed_evidence_type_ids",
    "allowed_provenance_type_ids",
    "allowed_reasoning_stage_ids",
    "allowed_explanation_type_ids",
    "trust_level",
    "certainty_level",
    "confidence_floor",
    "confidence_ceiling",
    "can_upgrade_without_revalidation",
    "requires_provenance",
    "requires_replay_validation",
    "blocker_visible",
    "risk_visible",
    "limitation_visible",
    "replay_safe",
    "drift_visible",
    "production_authorized",
    "explicit_limitations",
    "explicit_risks",
    "explainability_required",
)


def detect_duplicate_confidence_contracts(confidence_contracts: list[dict[str, Any]]) -> dict[str, Any]:
    ids = Counter(str(row.get("confidence_type_id")) for row in confidence_contracts)
    labels = Counter(str(row.get("confidence_label")) for row in confidence_contracts)
    ranks = Counter(str(row.get("deterministic_rank")) for row in confidence_contracts)
    return {
        "duplicate_confidence_type_ids": sorted(key for key, count in ids.items() if count > 1),
        "duplicate_confidence_labels": sorted(key for key, count in labels.items() if count > 1),
        "duplicate_deterministic_ranks": sorted(key for key, count in ranks.items() if count > 1),
    }


def validate_confidence_registry(
    confidence_contracts: list[dict[str, Any]],
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
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
    ordered = order_confidence_contracts(confidence_contracts)
    classification_ids = {row["classification_id"] for row in classification_rows}
    evidence_type_ids = {row["evidence_type_id"] for row in evidence_rows}
    provenance_type_ids = {row["provenance_type_id"] for row in provenance_rows}
    reasoning_stage_ids = {row["stage_type_id"] for row in reasoning_rows}
    explanation_type_ids = {row["explanation_type_id"] for row in explanation_rows}
    duplicate_detection = detect_duplicate_confidence_contracts(ordered)
    missing_required_fields = {
        str(row.get("confidence_label") or row.get("confidence_type_id") or index): [
            field for field in REQUIRED_CONFIDENCE_FIELDS if field not in row
        ]
        for index, row in enumerate(ordered)
    }
    missing_required_fields = {key: fields for key, fields in missing_required_fields.items() if fields}
    unknown_labels = sorted({str(row.get("confidence_label")) for row in ordered} - set(CONFIDENCE_LABELS))
    invalid_classification_references = _invalid_refs(ordered, "allowed_classification_ids", classification_ids)
    invalid_evidence_references = _invalid_refs(ordered, "allowed_evidence_type_ids", evidence_type_ids)
    invalid_provenance_references = _invalid_refs(ordered, "allowed_provenance_type_ids", provenance_type_ids)
    invalid_reasoning_stage_references = _invalid_refs(ordered, "allowed_reasoning_stage_ids", reasoning_stage_ids)
    invalid_explanation_references = _invalid_refs(ordered, "allowed_explanation_type_ids", explanation_type_ids)
    floor_ceiling_violations = {
        row["confidence_label"]: {
            "confidence_floor": row.get("confidence_floor"),
            "confidence_ceiling": row.get("confidence_ceiling"),
        }
        for row in ordered
        if not _floor_ceiling_valid(row)
    }
    non_upgradeable_violations = sorted(
        row["confidence_label"]
        for row in ordered
        if row.get("confidence_label") in NON_UPGRADEABLE_CONFIDENCE_LABELS
        and row.get("can_upgrade_without_revalidation") is True
    )
    production_authorized = [row["confidence_label"] for row in ordered if row.get("production_authorized") is True]
    blocker_visible = any(row.get("blocker_visible") is True for row in ordered)
    risk_visible = any(row.get("risk_visible") is True for row in ordered)
    limitation_visible = any(row.get("limitation_visible") is True for row in ordered)
    unsupported_visible = any(row.get("confidence_label") == "unsupported" for row in ordered)
    blocked_visible = any(row.get("confidence_label") == "blocked" for row in ordered)
    authorization_prohibited_visible = any(row.get("confidence_label") == "authorization_prohibited" for row in ordered)
    drift_present_visible = any(row.get("confidence_label") == "drift_present" for row in ordered)
    conflict_present_visible = any(row.get("confidence_label") == "conflict_present" for row in ordered)
    provenance_incomplete_visible = any(row.get("confidence_label") == "provenance_incomplete" for row in ordered)
    validation_errors = []
    if any(duplicate_detection.values()):
        validation_errors.append("duplicate_confidence_contracts_detected")
    if missing_required_fields:
        validation_errors.append("missing_required_confidence_fields")
    if unknown_labels:
        validation_errors.append("unknown_confidence_labels")
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
    if floor_ceiling_violations:
        validation_errors.append("confidence_floor_ceiling_invalid")
    if non_upgradeable_violations:
        validation_errors.append("non_upgradeable_confidence_state_marked_upgradeable")
    if production_authorized:
        validation_errors.append("production_authorized_confidence_detected")
    if not blocker_visible:
        validation_errors.append("blocker_visible_confidence_not_visible")
    if not risk_visible:
        validation_errors.append("risk_visible_confidence_not_visible")
    if not limitation_visible:
        validation_errors.append("limitation_visible_confidence_not_visible")
    if not unsupported_visible:
        validation_errors.append("unsupported_confidence_not_visible")
    if not blocked_visible:
        validation_errors.append("blocked_confidence_not_visible")
    if not authorization_prohibited_visible:
        validation_errors.append("authorization_prohibited_confidence_not_visible")
    if not drift_present_visible:
        validation_errors.append("drift_present_confidence_not_visible")
    if not conflict_present_visible:
        validation_errors.append("conflict_present_confidence_not_visible")
    if not provenance_incomplete_visible:
        validation_errors.append("provenance_incomplete_confidence_not_visible")
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
        "floor_ceiling_violations": floor_ceiling_violations,
        "floor_ceiling_violation_count": len(floor_ceiling_violations),
        "non_upgradeable_violations": non_upgradeable_violations,
        "non_upgradeable_violation_count": len(non_upgradeable_violations),
        "production_authorized_confidences": production_authorized,
        "blocker_visible_confidence_visible": blocker_visible,
        "risk_visible_confidence_visible": risk_visible,
        "limitation_visible_confidence_visible": limitation_visible,
        "unsupported_confidence_visible": unsupported_visible,
        "blocked_confidence_visible": blocked_visible,
        "authorization_prohibited_confidence_visible": authorization_prohibited_visible,
        "drift_present_confidence_visible": drift_present_visible,
        "conflict_present_confidence_visible": conflict_present_visible,
        "provenance_incomplete_confidence_visible": provenance_incomplete_visible,
    }


def export_confidence_registry(
    confidence_contracts: list[dict[str, Any]] | None = None,
    *,
    classifications: list[dict[str, Any]] | None = None,
    evidence_contracts: list[dict[str, Any]] | None = None,
    provenance_contracts: list[dict[str, Any]] | None = None,
    reasoning_stage_contracts: list[dict[str, Any]] | None = None,
    explanation_contracts: list[dict[str, Any]] | None = None,
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
    manifest = build_runtime_confidence_manifest(
        confidence_contracts,
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    validation = validate_confidence_registry(
        manifest["confidence_contracts"],
        classifications=classification_rows,
        evidence_contracts=evidence_rows,
        provenance_contracts=provenance_rows,
        reasoning_stage_contracts=reasoning_rows,
        explanation_contracts=explanation_rows,
    )
    replay = validate_confidence_replay_stability(manifest)
    exported = deepcopy(manifest)
    exported["registry_validation"] = validation
    exported["replay_validation"] = replay
    exported["deterministic_hash"] = hash_confidence_manifest(exported)
    return exported


def _invalid_refs(rows: list[dict[str, Any]], key: str, allowed: set[str]) -> dict[str, list[str]]:
    invalid = {
        row["confidence_label"]: sorted(set(row.get(key, [])) - allowed)
        for row in rows
    }
    return {label: refs for label, refs in invalid.items() if refs}


def _count_refs(mapping: dict[str, list[str]]) -> int:
    return sum(len(values) for values in mapping.values())


def _floor_ceiling_valid(row: dict[str, Any]) -> bool:
    floor = row.get("confidence_floor")
    ceiling = row.get("confidence_ceiling")
    if not isinstance(floor, int) or not isinstance(ceiling, int):
        return False
    return 0 <= floor <= ceiling <= 100
