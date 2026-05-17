"""Deterministic serialization for v4.3 orchestration manifests.

Serialization preserves unsupported, prohibited, blocked, missing,
conflicting, stale, and unknown orchestration evidence. It does not correct,
authorize, execute, remediate, repair, infer, route, schedule, sequence, or
mutate manifest state.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_manifest_models import (
    OrchestrationBoundaryVisibility,
    OrchestrationCapabilityVisibility,
    OrchestrationContinuityMetadata,
    OrchestrationExplainabilitySummary,
    OrchestrationManifest,
    OrchestrationManifestDiagnostic,
    OrchestrationManifestIdentity,
    OrchestrationManifestMetadata,
    OrchestrationProhibitedStateVisibility,
    OrchestrationUnsupportedStateVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "runtime_execution_enabled",
    "routing_execution_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "dependency_resolution_enabled",
    "orchestration_remediation_enabled",
    "orchestration_repair_enabled",
    "orchestration_inference_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "runtime_mutation_enabled",
    "operational_state_mutation_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "orchestration_engine_enabled",
    "state_machine_execution_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_orchestration_manifest_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_orchestration_manifest_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_orchestration_manifest_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_orchestration_manifest_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_orchestration_manifest_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def normalize_orchestration_manifest_evidence(payload: Any) -> Any:
    normalized = canonicalize_orchestration_manifest_evidence(payload)
    if isinstance(normalized, dict):
        normalized = _disable_execution_fields(dict(normalized))
        return {
            key: normalize_orchestration_manifest_evidence(value)
            for key, value in sorted(normalized.items(), key=lambda item: item[0])
        }
    if isinstance(normalized, list):
        return [normalize_orchestration_manifest_evidence(value) for value in normalized]
    return normalized


def export_orchestration_manifest_identity(identity: OrchestrationManifestIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_orchestration_manifest_metadata(metadata: OrchestrationManifestMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("source_report_references", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_capability_visibility(
    visibility: OrchestrationCapabilityVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "blocked_reason_visibility",
        "unsupported_reason_visibility",
        "prohibited_reason_visibility",
        "stale_reason_visibility",
        "missing_metadata_visibility",
        "conflicting_metadata_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_boundary_visibility(
    visibility: OrchestrationBoundaryVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("guarantee_references", "prohibited_capabilities"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_continuity_metadata(
    metadata: OrchestrationContinuityMetadata,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_orchestration_manifest_diagnostic(
    diagnostic: OrchestrationManifestDiagnostic,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_orchestration_explainability_summary(
    summary: OrchestrationExplainabilitySummary,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(summary))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_orchestration_prohibited_state_visibility(
    visibility: OrchestrationProhibitedStateVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("prohibited_states", "prohibited_capabilities", "blocked_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_unsupported_state_visibility(
    visibility: OrchestrationUnsupportedStateVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "unsupported_states",
        "blocked_states",
        "stale_metadata_states",
        "missing_metadata_states",
        "conflicting_metadata_states",
        "unknown_states",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_manifest(manifest: OrchestrationManifest) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(manifest))
    data["identity"] = export_orchestration_manifest_identity(manifest.identity)
    data["metadata"] = export_orchestration_manifest_metadata(manifest.metadata)
    data["capability_visibility"] = [
        export_orchestration_capability_visibility(visibility)
        for visibility in sorted(
            manifest.capability_visibility,
            key=lambda item: (item.deterministic_order, item.capability_id),
        )
    ]
    data["boundary_visibility"] = [
        export_orchestration_boundary_visibility(visibility)
        for visibility in sorted(
            manifest.boundary_visibility,
            key=lambda item: (item.deterministic_order, item.boundary_id),
        )
    ]
    data["continuity_metadata"] = [
        export_orchestration_continuity_metadata(metadata)
        for metadata in sorted(
            manifest.continuity_metadata,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_orchestration_manifest_diagnostic(diagnostic)
        for diagnostic in sorted(manifest.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["explainability_summaries"] = [
        export_orchestration_explainability_summary(summary)
        for summary in sorted(
            manifest.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["prohibited_state_visibility"] = export_orchestration_prohibited_state_visibility(
        manifest.prohibited_state_visibility
    )
    data["unsupported_state_visibility"] = export_orchestration_unsupported_state_visibility(
        manifest.unsupported_state_visibility
    )
    return data


def serialize_orchestration_manifest_identity(identity: OrchestrationManifestIdentity) -> str:
    return stable_serialize(export_orchestration_manifest_identity(identity))


def serialize_orchestration_manifest(manifest: OrchestrationManifest) -> str:
    return stable_serialize(export_orchestration_manifest(manifest))
