"""Certification helpers for v4.2 coordination readiness evidence."""

from __future__ import annotations

from typing import Any

from .coordination_readiness_diagnostics import (
    build_coordination_readiness_diagnostics,
    validate_coordination_readiness_non_execution,
    validate_coordination_readiness_visibility,
    validate_descriptive_readiness_classification,
    validate_layer_readiness_compatibility,
    validate_phase_evidence_compatibility,
)
from .coordination_readiness_hashing import (
    hash_coordination_readiness_certification,
    hash_descriptive_readiness_classification,
)
from .coordination_readiness_models import (
    CoordinationReadinessCertification,
    DescriptiveReadinessClassification,
    default_coordination_readiness_certification,
)
from .coordination_readiness_serialization import export_coordination_readiness_certification


def build_descriptive_readiness_classification(
    certification: CoordinationReadinessCertification | None = None,
) -> DescriptiveReadinessClassification:
    source = certification or default_coordination_readiness_certification()
    return source.descriptive_readiness_classification


def validate_descriptive_only_coordination_readiness_certification(
    certification: CoordinationReadinessCertification | None = None,
) -> dict[str, object]:
    source = certification or default_coordination_readiness_certification()
    visibility = validate_coordination_readiness_visibility(source)
    classification = validate_descriptive_readiness_classification(source)
    phase_evidence = validate_phase_evidence_compatibility(source)
    layer_compatibility = validate_layer_readiness_compatibility(source)
    non_execution = validate_coordination_readiness_non_execution(source)
    return {
        "valid": (
            visibility["valid"]
            and classification["valid"]
            and phase_evidence["valid"]
            and layer_compatibility["valid"]
            and non_execution["valid"]
        ),
        "visibility_valid": visibility["valid"],
        "classification_valid": classification["valid"],
        "phase_evidence_valid": phase_evidence["valid"],
        "layer_compatibility_valid": layer_compatibility["valid"],
        "non_execution_valid": non_execution["valid"],
        "readiness_approval_disabled": non_execution["readiness_approval_disabled"],
        "operational_authorization_disabled": non_execution["operational_authorization_disabled"],
        "remediation_disabled": non_execution["remediation_disabled"],
        "automatic_correction_disabled": non_execution["automatic_correction_disabled"],
        "drift_correction_disabled": non_execution["drift_correction_disabled"],
        "continuity_repair_disabled": non_execution["continuity_repair_disabled"],
        "routing_execution_disabled": non_execution["routing_execution_disabled"],
        "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
        "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
        "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
        "planner_integration_disabled": non_execution["planner_integration_disabled"],
        "production_consumption_disabled": non_execution["production_consumption_disabled"],
        "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
    }


def build_coordination_readiness_certification_evidence(
    certification: CoordinationReadinessCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_coordination_readiness_certification()
    visibility = validate_coordination_readiness_visibility(source)
    classification = validate_descriptive_readiness_classification(source)
    return {
        "certification_hash": hash_coordination_readiness_certification(source),
        "classification_hash": hash_descriptive_readiness_classification(
            source.descriptive_readiness_classification
        ),
        "phase_evidence_count": len(source.phase_evidence_references),
        "readiness_record_count": len(source.readiness_records),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_record_count": len(visibility["fail_visible_record_ids"]),
        "readiness_state_counts": visibility["readiness_state_counts"],
        "classification": source.descriptive_readiness_classification.classification,
        "classification_reasons": source.descriptive_readiness_classification.classification_reasons,
        "readiness_visibility_validation": visibility,
        "readiness_classification_validation": classification,
        "descriptive_only_validation": validate_descriptive_only_coordination_readiness_certification(source),
        "readiness_diagnostics": build_coordination_readiness_diagnostics(source),
        "exported_readiness_certification": export_coordination_readiness_certification(source),
    }
