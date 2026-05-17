"""Deterministic serialization for v4.2 coordination manifest foundations.

Serialization preserves unsupported, blocked, stale, unknown, and prohibited
coordination evidence. It does not correct, authorize, execute, remediate, or
mutate manifest state.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_manifest_models import (
    CoordinationContinuityReference,
    CoordinationDependencyReference,
    CoordinationDiagnostic,
    CoordinationGovernanceVisibility,
    CoordinationLineageReference,
    CoordinationManifest,
    CoordinationManifestIdentity,
    CoordinationManifestMetadata,
    CoordinationProhibitedStateVisibility,
    CoordinationUnsupportedStateVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "dependency_resolution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "recovery_execution_enabled",
    "lineage_repair_enabled",
    "inferred_lineage_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_dependency_resolution_enabled",
    "hidden_unsupported_state_resolution_enabled",
    "hidden_operational_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "hidden_fallback_enabled",
    "automatic_refresh_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_coordination_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_coordination_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_coordination_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_coordination_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_coordination_evidence(payload),
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


def normalize_coordination_evidence(payload: Any) -> Any:
    normalized = canonicalize_coordination_evidence(payload)
    if isinstance(normalized, dict):
        normalized = _disable_execution_fields(dict(normalized))
        return {
            key: normalize_coordination_evidence(value)
            for key, value in sorted(normalized.items(), key=lambda item: item[0])
        }
    if isinstance(normalized, list):
        return [normalize_coordination_evidence(value) for value in normalized]
    return normalized


def export_coordination_manifest_identity(identity: CoordinationManifestIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_coordination_manifest_metadata(metadata: CoordinationManifestMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in ("source_report_references", "evidence_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_dependency_reference(reference: CoordinationDependencyReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in (
        "blocked_reason_visibility",
        "stale_reason_visibility",
        "prohibited_reason_visibility",
        "unsupported_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_lineage_reference(reference: CoordinationLineageReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["lineage_evidence_references"] = sorted_entries(data["lineage_evidence_references"])
    return data


def export_coordination_continuity_reference(reference: CoordinationContinuityReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["continuity_evidence_references"] = sorted_entries(data["continuity_evidence_references"])
    return data


def export_coordination_diagnostic(diagnostic: CoordinationDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_prohibited_state_visibility(
    visibility: CoordinationProhibitedStateVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("prohibited_states", "prohibited_capabilities", "blocked_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_state_visibility(
    visibility: CoordinationUnsupportedStateVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("unsupported_states", "unknown_states", "blocked_states", "stale_states"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_governance_visibility(
    visibility: CoordinationGovernanceVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_manifest(manifest: CoordinationManifest) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(manifest))
    data["identity"] = export_coordination_manifest_identity(manifest.identity)
    data["metadata"] = export_coordination_manifest_metadata(manifest.metadata)
    data["dependency_references"] = [
        export_coordination_dependency_reference(reference)
        for reference in sorted(
            manifest.dependency_references,
            key=lambda item: (item.deterministic_order, item.dependency_id),
        )
    ]
    data["lineage_references"] = [
        export_coordination_lineage_reference(reference)
        for reference in sorted(manifest.lineage_references, key=lambda item: (item.deterministic_order, item.lineage_id))
    ]
    data["continuity_references"] = [
        export_coordination_continuity_reference(reference)
        for reference in sorted(
            manifest.continuity_references,
            key=lambda item: (item.deterministic_order, item.continuity_id),
        )
    ]
    data["diagnostics"] = [
        export_coordination_diagnostic(diagnostic)
        for diagnostic in sorted(manifest.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["prohibited_state_visibility"] = export_prohibited_state_visibility(manifest.prohibited_state_visibility)
    data["unsupported_state_visibility"] = export_unsupported_state_visibility(manifest.unsupported_state_visibility)
    data["governance_visibility"] = export_coordination_governance_visibility(manifest.governance_visibility)
    return data


def serialize_coordination_manifest_identity(identity: CoordinationManifestIdentity) -> str:
    return stable_serialize(export_coordination_manifest_identity(identity))


def serialize_coordination_manifest(manifest: CoordinationManifest) -> str:
    return stable_serialize(export_coordination_manifest(manifest))
