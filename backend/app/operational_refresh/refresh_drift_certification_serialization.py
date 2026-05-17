"""Deterministic serialization for v4.1 refresh drift certification."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_drift_certification_models import RefreshDriftCertification, RefreshDriftCertificationIdentity


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


CAPABILITY_FIELDS: tuple[str, ...] = (
    "drift_remediation_enabled",
    "automatic_drift_correction_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "automatic_dependency_resolution_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
    "automatic_rollback_enabled",
    "automatic_recovery_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "runtime_mutation_enabled",
    "hidden_remediation_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "silent_drift_suppression_enabled",
    "hidden_fallback_enabled",
    "hidden_drift_resolution_enabled",
    "hidden_classification_resolution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_provenance_resolution_enabled",
    "hidden_unsupported_resolution_enabled",
    "inferred_provenance_allowed",
    "execution_enabled",
    "live_replay_enabled",
    "correction_execution_enabled",
    "remediation_enabled",
)


def _disable_capability_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELDS:
        if field_name in data:
            data[field_name] = False
    return data


def _export_record(record: object) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(record))
    for field_name, value in tuple(data.items()):
        if isinstance(value, (list, tuple)):
            data[field_name] = sorted_entries(value)
    return data


def export_refresh_drift_certification_identity(identity: RefreshDriftCertificationIdentity) -> dict[str, Any]:
    return _export_record(identity)


def export_refresh_drift_certification(certification: RefreshDriftCertification) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(certification))
    data["identity"] = export_refresh_drift_certification_identity(certification.identity)
    data["drift_observations"] = [
        _export_record(observation)
        for observation in sorted(
            certification.drift_observations,
            key=lambda item: (item.deterministic_order, item.observation_id),
        )
    ]
    data["layer_visibility"] = _export_record(certification.layer_visibility)
    data["classification_visibility"] = _export_record(certification.classification_visibility)
    data["continuity_metadata"] = _export_record(certification.continuity_metadata)
    data["lineage_visibility"] = _export_record(certification.lineage_visibility)
    data["provenance_visibility"] = _export_record(certification.provenance_visibility)
    data["replay_visibility"] = _export_record(certification.replay_visibility)
    data["rollback_visibility"] = _export_record(certification.rollback_visibility)
    data["blocked_state_visibility"] = _export_record(certification.blocked_state_visibility)
    data["unsupported_state_visibility"] = _export_record(certification.unsupported_state_visibility)
    data["diagnostics"] = _export_record(certification.diagnostics)
    data["governance"] = _export_record(certification.governance)
    return data


def serialize_refresh_drift_certification_identity(identity: RefreshDriftCertificationIdentity) -> str:
    return stable_serialize(export_refresh_drift_certification_identity(identity))


def serialize_refresh_drift_certification(certification: RefreshDriftCertification) -> str:
    return stable_serialize(export_refresh_drift_certification(certification))
