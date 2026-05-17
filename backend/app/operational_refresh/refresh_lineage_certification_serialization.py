"""Deterministic serialization for v4.1 refresh lineage certification."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_lineage_certification_models import (
    RefreshAncestryLink,
    RefreshAncestryNode,
    RefreshEvolutionVisibility,
    RefreshLineageBlockedStateVisibility,
    RefreshLineageCertification,
    RefreshLineageContinuityMetadata,
    RefreshLineageDiagnostics,
    RefreshLineageDriftVisibility,
    RefreshLineageGovernance,
    RefreshLineageIdentity,
    RefreshLineageUnsupportedStateVisibility,
    RefreshProvenanceInheritance,
    RefreshReplayLineageVisibility,
    RefreshRollbackLineageVisibility,
    RefreshSchemaTransitionContinuity,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in (
        "execution_authorized",
        "refresh_execution_enabled",
        "orchestration_enabled",
        "migration_execution_enabled",
        "automatic_lineage_repair_enabled",
        "automatic_continuity_correction_enabled",
        "automatic_schema_migration_enabled",
        "automatic_rollback_enabled",
        "automatic_recovery_enabled",
        "planner_integration_enabled",
        "production_consumption_enabled",
        "remediation_enabled",
        "recommendation_enabled",
        "ranking_enabled",
        "scoring_enabled",
        "selection_enabled",
        "optimization_enabled",
        "authorization_enabled",
        "approval_enabled",
        "runtime_mutation_enabled",
        "hidden_orchestration_behavior_enabled",
        "implicit_execution_pathway_enabled",
        "silent_continuity_correction_enabled",
        "silent_correction_enabled",
        "automatic_repair_enabled",
        "live_replay_enabled",
        "recovery_execution_enabled",
        "execution_enabled",
        "inferred_provenance_allowed",
        "hidden_provenance_resolution_enabled",
        "hidden_evolution_resolution_enabled",
        "hidden_schema_resolution_enabled",
        "hidden_unsupported_resolution_enabled",
        "hidden_drift_resolution_enabled",
    ):
        if field_name in data:
            data[field_name] = False
    return data


def export_lineage_identity(identity: RefreshLineageIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_ancestry_node(node: RefreshAncestryNode) -> dict[str, Any]:
    return _disable_execution_fields(asdict(node))


def export_ancestry_link(link: RefreshAncestryLink) -> dict[str, Any]:
    return _disable_execution_fields(asdict(link))


def export_provenance_inheritance(inheritance: RefreshProvenanceInheritance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(inheritance))
    for field_name in ("inherited_from_references", "source_evidence_references", "provenance_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_evolution_visibility(visibility: RefreshEvolutionVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "parent_child_lineage_visibility",
        "schema_transition_visibility",
        "ancestry_discontinuity_visibility",
        "stale_lineage_visibility",
        "drift_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_continuity_metadata(metadata: RefreshLineageContinuityMetadata) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(metadata))
    for field_name in (
        "ancestry_continuity_references",
        "lineage_continuity_references",
        "provenance_continuity_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "schema_transition_references",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_replay_lineage_visibility(visibility: RefreshReplayLineageVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("replay_lineage_references", "replay_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_rollback_lineage_visibility(visibility: RefreshRollbackLineageVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("rollback_lineage_references", "rollback_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_schema_transition_continuity(continuity: RefreshSchemaTransitionContinuity) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(continuity))
    for field_name in ("schema_transition_visibility", "schema_discontinuity_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_blocked_state_visibility(visibility: RefreshLineageBlockedStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "blocked_lineage_links",
        "circular_ancestry_links",
        "ancestry_discontinuity_visibility",
        "lineage_discontinuity_visibility",
        "provenance_discontinuity_visibility",
        "replay_discontinuity_visibility",
        "rollback_discontinuity_visibility",
        "schema_discontinuity_visibility",
        "prohibited_execution_leakage",
        "prohibited_orchestration_leakage",
        "prohibited_remediation_leakage",
        "prohibited_migration_leakage",
        "prohibited_planner_integration_leakage",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_state_visibility(visibility: RefreshLineageUnsupportedStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "unsupported_lineage_nodes",
        "unsupported_lineage_links",
        "unsupported_lineage_providers",
        "stale_lineage_links",
        "prohibited_lineage_links",
        "prohibited_lineage_domains",
        "failure_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_drift_visibility(visibility: RefreshLineageDriftVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("stale_lineage_references", "changed_schema_references", "lineage_drift_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_diagnostics(diagnostics: RefreshLineageDiagnostics) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostics))
    for field_name in (
        "diagnostic_references",
        "warning_visibility",
        "blocker_visibility",
        "circular_ancestry_visibility",
        "unsupported_lineage_visibility",
        "prohibited_lineage_visibility",
        "drift_visibility",
        "integrity_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance(governance: RefreshLineageGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_refresh_lineage_certification(certification: RefreshLineageCertification) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(certification))
    data["identity"] = export_lineage_identity(certification.identity)
    data["ancestry_nodes"] = [
        export_ancestry_node(node)
        for node in sorted(certification.ancestry_nodes, key=lambda item: (item.deterministic_order, item.node_id))
    ]
    data["ancestry_links"] = [
        export_ancestry_link(link)
        for link in sorted(certification.ancestry_links, key=lambda item: (item.deterministic_order, item.link_id))
    ]
    data["provenance_inheritance"] = [
        export_provenance_inheritance(inheritance)
        for inheritance in sorted(
            certification.provenance_inheritance,
            key=lambda item: (item.deterministic_order, item.inheritance_id),
        )
    ]
    data["evolution_visibility"] = export_evolution_visibility(certification.evolution_visibility)
    data["continuity_metadata"] = export_continuity_metadata(certification.continuity_metadata)
    data["replay_lineage_visibility"] = export_replay_lineage_visibility(certification.replay_lineage_visibility)
    data["rollback_lineage_visibility"] = export_rollback_lineage_visibility(certification.rollback_lineage_visibility)
    data["schema_transition_continuity"] = export_schema_transition_continuity(certification.schema_transition_continuity)
    data["blocked_state_visibility"] = export_blocked_state_visibility(certification.blocked_state_visibility)
    data["unsupported_state_visibility"] = export_unsupported_state_visibility(certification.unsupported_state_visibility)
    data["drift_visibility"] = export_drift_visibility(certification.drift_visibility)
    data["diagnostics"] = export_diagnostics(certification.diagnostics)
    data["governance"] = export_governance(certification.governance)
    return data


def serialize_lineage_identity(identity: RefreshLineageIdentity) -> str:
    return stable_serialize(export_lineage_identity(identity))


def serialize_refresh_lineage_certification(certification: RefreshLineageCertification) -> str:
    return stable_serialize(export_refresh_lineage_certification(certification))
