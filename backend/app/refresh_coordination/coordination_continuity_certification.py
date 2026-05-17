"""Certification helpers for v4.2 coordination continuity evidence."""

from __future__ import annotations

from typing import Any

from .coordination_continuity_diagnostics import (
    build_coordination_continuity_diagnostics,
    validate_coordination_continuity_non_execution,
    validate_coordination_continuity_visibility,
    validate_cross_layer_continuity_summary,
)
from .coordination_continuity_hashing import (
    hash_coordination_continuity_certification,
    hash_cross_layer_continuity_summary,
)
from .coordination_continuity_models import (
    CoordinationContinuityCertification,
    CrossLayerContinuitySummary,
    default_coordination_continuity_certification,
)
from .coordination_continuity_serialization import export_coordination_continuity_certification


def build_cross_layer_continuity_summary(
    certification: CoordinationContinuityCertification | None = None,
) -> CrossLayerContinuitySummary:
    source = certification or default_coordination_continuity_certification()
    return source.cross_layer_continuity_summary


def validate_descriptive_only_coordination_continuity_certification(
    certification: CoordinationContinuityCertification | None = None,
) -> dict[str, object]:
    source = certification or default_coordination_continuity_certification()
    visibility = validate_coordination_continuity_visibility(source)
    summary = validate_cross_layer_continuity_summary(source)
    non_execution = validate_coordination_continuity_non_execution(source)
    return {
        "valid": visibility["valid"] and summary["valid"] and non_execution["valid"],
        "visibility_valid": visibility["valid"],
        "cross_layer_summary_valid": summary["valid"],
        "non_execution_valid": non_execution["valid"],
        "continuity_repair_disabled": non_execution["continuity_repair_disabled"],
        "continuity_inference_disabled": non_execution["continuity_inference_disabled"],
        "remediation_disabled": non_execution["remediation_disabled"],
        "automatic_correction_disabled": non_execution["automatic_correction_disabled"],
        "drift_correction_disabled": non_execution["drift_correction_disabled"],
        "routing_execution_disabled": non_execution["routing_execution_disabled"],
        "orchestration_execution_disabled": non_execution["orchestration_execution_disabled"],
        "refresh_execution_disabled": non_execution["refresh_execution_disabled"],
        "dependency_resolution_disabled": non_execution["dependency_resolution_disabled"],
        "planner_integration_disabled": non_execution["planner_integration_disabled"],
        "production_consumption_disabled": non_execution["production_consumption_disabled"],
        "runtime_mutation_disabled": non_execution["runtime_mutation_disabled"],
    }


def build_coordination_continuity_certification_evidence(
    certification: CoordinationContinuityCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_coordination_continuity_certification()
    exported = export_coordination_continuity_certification(source)
    visibility = validate_coordination_continuity_visibility(source)
    summary = validate_cross_layer_continuity_summary(source)
    non_execution = validate_coordination_continuity_non_execution(source)
    return {
        "certification_hash": hash_coordination_continuity_certification(source),
        "cross_layer_summary_hash": hash_cross_layer_continuity_summary(source.cross_layer_continuity_summary),
        "continuity_record_count": len(source.continuity_records),
        "diagnostic_count": len(source.diagnostics),
        "fail_visible_record_count": len(visibility["fail_visible_record_ids"]),
        "state_counts": visibility["continuity_state_counts"],
        "summary_lines": source.cross_layer_continuity_summary.summary_lines,
        "continuity_visibility_validation": visibility,
        "cross_layer_summary_validation": summary,
        "non_execution_validation": non_execution,
        "descriptive_only_validation": validate_descriptive_only_coordination_continuity_certification(source),
        "exported_continuity_certification": exported,
    }
