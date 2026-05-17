"""Continuity certification for v4.1 diagnostics explainability evidence."""

from __future__ import annotations

from .refresh_diagnostics_explainability_models import (
    RefreshDiagnosticsExplainability,
    default_refresh_diagnostics_explainability,
)


def validate_diagnostics_explainability_continuity(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    diagnostic_reference = payload.identity.diagnostics_id
    explanation_reference = payload.identity.explanation_id
    diagnostic_visible = diagnostic_reference in payload.continuity_metadata.diagnostic_references
    explanation_visible = explanation_reference in payload.continuity_metadata.explanation_references
    return {
        "valid": (
            diagnostic_visible
            and explanation_visible
            and payload.continuity_metadata.diagnostics_continuity_preserved
            and payload.continuity_metadata.explanation_continuity_preserved
            and not payload.continuity_metadata.remediation_enabled
            and not payload.continuity_metadata.automatic_correction_enabled
            and not payload.continuity_metadata.runtime_mutation_enabled
        ),
        "diagnostic_reference": diagnostic_reference,
        "diagnostic_reference_visible": diagnostic_visible,
        "explanation_reference": explanation_reference,
        "explanation_reference_visible": explanation_visible,
        "diagnostics_continuity_preserved": payload.continuity_metadata.diagnostics_continuity_preserved,
        "explanation_continuity_preserved": payload.continuity_metadata.explanation_continuity_preserved,
    }


def validate_diagnostics_provenance_continuity(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    provenance_reference = payload.identity.provenance_reference
    provenance_visible = provenance_reference in payload.continuity_metadata.provenance_references
    return {
        "valid": (
            provenance_visible
            and payload.continuity_metadata.provenance_continuity_preserved
            and bool(payload.continuity_metadata.dependency_references)
            and bool(payload.continuity_metadata.schema_references)
            and bool(payload.continuity_metadata.drift_references)
        ),
        "provenance_reference": provenance_reference,
        "provenance_reference_visible": provenance_visible,
        "dependency_reference_count": len(payload.continuity_metadata.dependency_references),
        "schema_reference_count": len(payload.continuity_metadata.schema_references),
        "drift_reference_count": len(payload.continuity_metadata.drift_references),
        "provenance_continuity_preserved": payload.continuity_metadata.provenance_continuity_preserved,
    }


def validate_diagnostics_lineage_continuity(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    lineage_reference = payload.identity.lineage_reference
    lineage_visible = lineage_reference in payload.continuity_metadata.lineage_references
    return {
        "valid": (
            lineage_visible
            and payload.continuity_metadata.lineage_continuity_preserved
            and bool(payload.continuity_metadata.sequencing_references)
        ),
        "lineage_reference": lineage_reference,
        "lineage_reference_visible": lineage_visible,
        "sequencing_reference_count": len(payload.continuity_metadata.sequencing_references),
        "lineage_continuity_preserved": payload.continuity_metadata.lineage_continuity_preserved,
    }


def validate_diagnostics_replay_continuity(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    replay_visible = bool(payload.continuity_metadata.replay_references)
    return {
        "valid": replay_visible and payload.continuity_metadata.replay_continuity_preserved,
        "replay_reference_count": len(payload.continuity_metadata.replay_references),
        "replay_reference_visible": replay_visible,
        "replay_continuity_preserved": payload.continuity_metadata.replay_continuity_preserved,
    }


def validate_diagnostics_rollback_continuity(payload: RefreshDiagnosticsExplainability) -> dict[str, object]:
    rollback_visible = bool(payload.continuity_metadata.rollback_references)
    return {
        "valid": rollback_visible and payload.continuity_metadata.rollback_continuity_preserved,
        "rollback_reference_count": len(payload.continuity_metadata.rollback_references),
        "rollback_reference_visible": rollback_visible,
        "rollback_continuity_preserved": payload.continuity_metadata.rollback_continuity_preserved,
    }


def certify_diagnostics_explainability_continuity(
    payload: RefreshDiagnosticsExplainability | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_diagnostics_explainability()
    diagnostics = validate_diagnostics_explainability_continuity(source)
    provenance = validate_diagnostics_provenance_continuity(source)
    lineage = validate_diagnostics_lineage_continuity(source)
    replay = validate_diagnostics_replay_continuity(source)
    rollback = validate_diagnostics_rollback_continuity(source)
    return {
        "valid": diagnostics["valid"] and provenance["valid"] and lineage["valid"] and replay["valid"] and rollback["valid"],
        "diagnostics_continuity_valid": diagnostics["valid"],
        "provenance_continuity_valid": provenance["valid"],
        "lineage_continuity_valid": lineage["valid"],
        "replay_continuity_valid": replay["valid"],
        "rollback_continuity_valid": rollback["valid"],
        "diagnostics_continuity": diagnostics,
        "provenance_continuity": provenance,
        "lineage_continuity": lineage,
        "replay_continuity": replay,
        "rollback_continuity": rollback,
    }
