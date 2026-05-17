"""Continuity certification helpers for v4.1 refresh continuity evidence."""

from __future__ import annotations

from .refresh_continuity_certification_models import (
    CONTINUITY_LAYERS,
    RefreshContinuityCertification,
    default_refresh_continuity_certification,
)
from .refresh_continuity_certification_visibility import validate_refresh_continuity_certification_visibility


def _metadata_reference_field(layer: str) -> str:
    return {
        "manifest": "manifest_references",
        "dependency": "dependency_references",
        "lineage": "lineage_references",
        "schema": "schema_references",
        "sequencing": "sequencing_references",
        "drift": "drift_references",
        "replay": "replay_references",
        "rollback": "rollback_references",
        "diagnostics": "diagnostics_references",
        "explainability": "explainability_references",
    }[layer]


def _metadata_preserved_field(layer: str) -> str:
    return f"{layer}_continuity_preserved"


def _expected_identity_reference(payload: RefreshContinuityCertification, layer: str) -> str:
    identity = payload.identity
    return {
        "manifest": identity.source_manifest_reference,
        "dependency": identity.source_dependency_graph_reference,
        "lineage": identity.source_lineage_certification_reference,
        "schema": identity.source_schema_governance_reference,
        "sequencing": identity.source_sequencing_reference,
        "drift": identity.source_drift_certification_reference,
        "replay": identity.source_replay_rollback_reference,
        "rollback": identity.source_replay_rollback_reference,
        "diagnostics": identity.source_diagnostics_explainability_reference,
        "explainability": identity.source_diagnostics_explainability_reference,
    }[layer]


def validate_layer_continuity(payload: RefreshContinuityCertification, layer: str) -> dict[str, object]:
    metadata_references = getattr(payload.continuity_metadata, _metadata_reference_field(layer))
    expected_reference = _expected_identity_reference(payload, layer)
    reference_visible = expected_reference in metadata_references
    preserved = bool(getattr(payload.continuity_metadata, _metadata_preserved_field(layer)))
    certified_id = f"v4_1_{layer}_continuity_certified"
    failure_id = f"v4_1_{layer}_continuity_failure_visible"
    certification_visible = certified_id in {
        entry.certification_id for entry in payload.certifications if entry.layer == layer
    }
    failure_visible = failure_id in payload.cross_layer_aggregation.continuity_failure_ids
    return {
        "valid": (
            reference_visible
            and preserved
            and certification_visible
            and failure_visible
            and payload.continuity_metadata.continuity_failure_visibility_preserved
            and not payload.continuity_metadata.remediation_enabled
            and not payload.continuity_metadata.automatic_correction_enabled
            and not payload.continuity_metadata.approval_enabled
            and not payload.continuity_metadata.authorization_enabled
            and not payload.continuity_metadata.execution_enabled
            and not payload.continuity_metadata.runtime_mutation_enabled
        ),
        "layer": layer,
        "expected_reference": expected_reference,
        "reference_visible": reference_visible,
        "metadata_reference_count": len(metadata_references),
        "continuity_preserved": preserved,
        "certification_visible": certification_visible,
        "failure_visible": failure_visible,
    }


def validate_cross_layer_continuity(payload: RefreshContinuityCertification) -> dict[str, object]:
    visibility = validate_refresh_continuity_certification_visibility(payload)
    return {
        "valid": (
            visibility["cross_layer_continuity_aggregation_visible"]
            and visibility["continuity_failure_visibility_preserved"]
            and visibility["unsupported_continuity_state_visible"]
            and visibility["blocked_continuity_state_visible"]
            and visibility["prohibited_continuity_state_visible"]
            and visibility["stale_continuity_evidence_visible"]
            and visibility["cross_layer_continuity_conflict_visible"]
            and payload.continuity_metadata.cross_layer_continuity_visibility_preserved
        ),
        "cross_layer_continuity_aggregation_visible": visibility["cross_layer_continuity_aggregation_visible"],
        "continuity_failure_visibility_preserved": visibility["continuity_failure_visibility_preserved"],
        "unsupported_continuity_state_visible": visibility["unsupported_continuity_state_visible"],
        "blocked_continuity_state_visible": visibility["blocked_continuity_state_visible"],
        "prohibited_continuity_state_visible": visibility["prohibited_continuity_state_visible"],
        "stale_continuity_evidence_visible": visibility["stale_continuity_evidence_visible"],
        "cross_layer_continuity_conflict_visible": visibility["cross_layer_continuity_conflict_visible"],
    }


def certify_refresh_continuity(
    payload: RefreshContinuityCertification | None = None,
) -> dict[str, object]:
    source = payload or default_refresh_continuity_certification()
    layer_results = {layer: validate_layer_continuity(source, layer) for layer in CONTINUITY_LAYERS}
    cross_layer = validate_cross_layer_continuity(source)
    provenance_visible = source.identity.provenance_reference in source.continuity_metadata.provenance_references
    lineage_visible = source.identity.lineage_reference in source.continuity_metadata.lineage_references
    replay_visible = source.identity.replay_reference in source.continuity_metadata.replay_references
    rollback_visible = source.identity.rollback_reference in source.continuity_metadata.rollback_references
    return {
        "valid": (
            all(result["valid"] for result in layer_results.values())
            and cross_layer["valid"]
            and provenance_visible
            and lineage_visible
            and replay_visible
            and rollback_visible
        ),
        **{f"{layer}_continuity_valid": result["valid"] for layer, result in layer_results.items()},
        "cross_layer_continuity_valid": cross_layer["valid"],
        "provenance_continuity_valid": provenance_visible,
        "lineage_continuity_valid": lineage_visible,
        "replay_continuity_valid": replay_visible,
        "rollback_continuity_valid": rollback_visible,
        "layer_continuity": layer_results,
        "cross_layer_continuity": cross_layer,
        "provenance_reference": source.identity.provenance_reference,
        "lineage_reference": source.identity.lineage_reference,
        "replay_reference": source.identity.replay_reference,
        "rollback_reference": source.identity.rollback_reference,
    }
