"""Deterministic serialization for v4.1 refresh manifest foundations.

Serialization preserves unsupported, prohibited, unknown, stale, blocker, and
warning evidence. It does not correct, omit, authorize, execute, or mutate
refresh manifest state.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_manifest_models import (
    RefreshManifest,
    RefreshManifestContinuityMetadata,
    RefreshManifestDependencyVisibility,
    RefreshManifestDiagnosticsVisibility,
    RefreshManifestExtractionLineage,
    RefreshManifestGovernanceVisibility,
    RefreshManifestIdentity,
    RefreshManifestPatchLineage,
    RefreshManifestProhibitedDomainVisibility,
    RefreshManifestReplayMetadata,
    RefreshManifestRollbackMetadata,
    RefreshManifestSchemaVersionVisibility,
    RefreshManifestSourceLineage,
    RefreshManifestState,
    RefreshManifestTrustVisibility,
    RefreshManifestUnsupportedStateVisibility,
    RefreshManifestValidationVisibility,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in (
        "execution_authorized",
        "refresh_execution_enabled",
        "orchestration_enabled",
        "deployment_execution_enabled",
        "automatic_refresh_enabled",
        "automatic_migration_enabled",
        "planner_integration_enabled",
        "production_consumption_enabled",
        "remediation_enabled",
        "mutation_enabled",
        "runtime_mutation_enabled",
        "recommendation_enabled",
        "ranking_enabled",
        "scoring_enabled",
        "selection_enabled",
        "authorization_enabled",
        "approval_enabled",
        "automatic_rollback_enabled",
        "automatic_recovery_enabled",
        "hidden_operational_behavior_enabled",
        "implicit_execution_pathway_enabled",
        "silent_fallback_enabled",
        "execution_enabled",
        "extraction_execution_enabled",
        "patch_execution_enabled",
        "automatic_extraction_enabled",
        "automatic_source_refresh_enabled",
        "automatic_dependency_refresh_enabled",
        "automatic_validation_execution_enabled",
        "live_replay_enabled",
        "runtime_execution_enabled",
        "recovery_execution_enabled",
    ):
        if field_name in data:
            data[field_name] = False
    return data


def export_refresh_manifest_identity(identity: RefreshManifestIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_refresh_manifest_state(state: RefreshManifestState) -> dict[str, Any]:
    return _disable_execution_fields(asdict(state))


def export_source_lineage(record: RefreshManifestSourceLineage) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("source_evidence_references", "prior_manifest_references", "unsupported_source_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_extraction_lineage(record: RefreshManifestExtractionLineage) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("extraction_evidence_references", "unsupported_extraction_states"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_patch_lineage(record: RefreshManifestPatchLineage) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("patch_evidence_references", "prior_patch_references", "rollback_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_schema_version_visibility(record: RefreshManifestSchemaVersionVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("visible_schema_constraints", "unsupported_schema_versions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_dependency_visibility(record: RefreshManifestDependencyVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in (
        "dependency_references",
        "missing_dependency_visibility",
        "stale_dependency_visibility",
        "prohibited_dependency_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_trust_visibility(record: RefreshManifestTrustVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("trusted_source_references", "untrusted_source_visibility", "ambiguous_trust_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_validation_visibility(record: RefreshManifestValidationVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in (
        "validation_references",
        "validation_warning_visibility",
        "validation_blocker_visibility",
        "unsupported_validation_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_prohibited_domain_visibility(record: RefreshManifestProhibitedDomainVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("prohibited_domains", "visible_blocked_reasons"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_state_visibility(record: RefreshManifestUnsupportedStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("unsupported_states", "unknown_states", "blocked_states", "prohibited_states", "stale_states"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_continuity_metadata(metadata: RefreshManifestContinuityMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in (
        "provenance_continuity_references",
        "lineage_continuity_references",
        "replay_references",
        "rollback_references",
        "diagnostics_references",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_replay_metadata(metadata: RefreshManifestReplayMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    data["replay_evidence_references"] = sorted_entries(data["replay_evidence_references"])
    return data


def export_rollback_metadata(metadata: RefreshManifestRollbackMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    data["rollback_evidence_references"] = sorted_entries(data["rollback_evidence_references"])
    return data


def export_diagnostics_visibility(record: RefreshManifestDiagnosticsVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in (
        "diagnostic_references",
        "warning_visibility",
        "blocker_visibility",
        "unsupported_state_visibility",
        "prohibited_domain_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_visibility(record: RefreshManifestGovernanceVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_refresh_manifest(manifest: RefreshManifest) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(manifest))
    data["identity"] = export_refresh_manifest_identity(manifest.identity)
    data["states"] = [
        export_refresh_manifest_state(state)
        for state in sorted(manifest.states, key=lambda item: (item.deterministic_order, item.state_id))
    ]
    data["source_lineage"] = [
        export_source_lineage(record)
        for record in sorted(manifest.source_lineage, key=lambda item: (item.deterministic_order, item.source_lineage_id))
    ]
    data["extraction_lineage"] = [
        export_extraction_lineage(record)
        for record in sorted(
            manifest.extraction_lineage,
            key=lambda item: (item.deterministic_order, item.extraction_lineage_id),
        )
    ]
    data["patch_lineage"] = [
        export_patch_lineage(record)
        for record in sorted(manifest.patch_lineage, key=lambda item: (item.deterministic_order, item.patch_lineage_id))
    ]
    data["schema_version_visibility"] = [
        export_schema_version_visibility(record)
        for record in sorted(
            manifest.schema_version_visibility,
            key=lambda item: (item.deterministic_order, item.schema_visibility_id),
        )
    ]
    data["dependency_visibility"] = [
        export_dependency_visibility(record)
        for record in sorted(
            manifest.dependency_visibility,
            key=lambda item: (item.deterministic_order, item.dependency_visibility_id),
        )
    ]
    data["trust_visibility"] = [
        export_trust_visibility(record)
        for record in sorted(manifest.trust_visibility, key=lambda item: (item.deterministic_order, item.trust_visibility_id))
    ]
    data["validation_visibility"] = [
        export_validation_visibility(record)
        for record in sorted(
            manifest.validation_visibility,
            key=lambda item: (item.deterministic_order, item.validation_visibility_id),
        )
    ]
    data["prohibited_domain_visibility"] = [
        export_prohibited_domain_visibility(record)
        for record in sorted(
            manifest.prohibited_domain_visibility,
            key=lambda item: (item.deterministic_order, item.prohibited_domain_visibility_id),
        )
    ]
    data["unsupported_state_visibility"] = [
        export_unsupported_state_visibility(record)
        for record in sorted(
            manifest.unsupported_state_visibility,
            key=lambda item: (item.deterministic_order, item.unsupported_state_visibility_id),
        )
    ]
    data["continuity_metadata"] = export_continuity_metadata(manifest.continuity_metadata)
    data["replay_metadata"] = export_replay_metadata(manifest.replay_metadata)
    data["rollback_metadata"] = export_rollback_metadata(manifest.rollback_metadata)
    data["diagnostics_visibility"] = [
        export_diagnostics_visibility(record)
        for record in sorted(
            manifest.diagnostics_visibility,
            key=lambda item: (item.deterministic_order, item.diagnostics_visibility_id),
        )
    ]
    data["governance_visibility"] = export_governance_visibility(manifest.governance_visibility)
    return data


def serialize_refresh_manifest_identity(identity: RefreshManifestIdentity) -> str:
    return stable_serialize(export_refresh_manifest_identity(identity))


def serialize_refresh_manifest(manifest: RefreshManifest) -> str:
    return stable_serialize(export_refresh_manifest(manifest))
