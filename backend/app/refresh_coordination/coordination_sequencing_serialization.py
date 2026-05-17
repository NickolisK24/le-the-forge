"""Canonical serialization for v4.2 coordination sequencing intelligence."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_sequencing_models import (
    CoordinationSequenceRecord,
    CoordinationSequencingDiagnostic,
    CoordinationSequencingGovernance,
    CoordinationSequencingIdentity,
    CoordinationSequencingIntelligence,
    DependencyGraphSequenceReference,
    LineageSequenceReference,
    ManifestSequenceReference,
    NonExecutableSequenceOrderingVisibility,
    SequenceStateVisibility,
    SequenceStepIdentity,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "dependency_resolution_enabled",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "hidden_sequence_execution_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_sequencing_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_sequencing_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_sequencing_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_sequencing_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_sequencing_evidence(payload),
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


def export_coordination_sequencing_identity(identity: CoordinationSequencingIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_sequence_step_identity(step: SequenceStepIdentity) -> dict[str, Any]:
    return _disable_execution_fields(asdict(step))


def export_manifest_sequence_reference(reference: ManifestSequenceReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["step_identity_ids"] = sorted_entries(data["step_identity_ids"])
    return data


def export_dependency_graph_sequence_reference(reference: DependencyGraphSequenceReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("node_references", "edge_references", "step_identity_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_lineage_sequence_reference(reference: LineageSequenceReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("lineage_record_references", "step_identity_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_sequence_record(record: CoordinationSequenceRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_sequence_state_visibility(visibility: SequenceStateVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("sequence_record_ids", "step_identity_ids", "reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_non_executable_sequence_ordering_visibility(
    visibility: NonExecutableSequenceOrderingVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "ordered_step_identity_ids",
        "ordered_sequence_record_ids",
        "blocked_ordering_ids",
        "prohibited_ordering_ids",
        "unsupported_ordering_ids",
        "stale_ordering_ids",
        "missing_ordering_ids",
        "conflicting_ordering_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_sequencing_diagnostic(diagnostic: CoordinationSequencingDiagnostic) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_sequence_record_ids", "affected_step_identity_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_sequencing_governance(governance: CoordinationSequencingGovernance) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_sequencing_intelligence(
    sequencing: CoordinationSequencingIntelligence,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(sequencing))
    data["identity"] = export_coordination_sequencing_identity(sequencing.identity)
    data["step_identities"] = [
        export_sequence_step_identity(step)
        for step in sorted(sequencing.step_identities, key=lambda item: (item.deterministic_order, item.step_identity_id))
    ]
    data["manifest_sequence_references"] = [
        export_manifest_sequence_reference(reference)
        for reference in sorted(
            sequencing.manifest_sequence_references,
            key=lambda item: (item.deterministic_order, item.manifest_sequence_reference_id),
        )
    ]
    data["dependency_graph_sequence_references"] = [
        export_dependency_graph_sequence_reference(reference)
        for reference in sorted(
            sequencing.dependency_graph_sequence_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_sequence_reference_id),
        )
    ]
    data["lineage_sequence_references"] = [
        export_lineage_sequence_reference(reference)
        for reference in sorted(
            sequencing.lineage_sequence_references,
            key=lambda item: (item.deterministic_order, item.lineage_sequence_reference_id),
        )
    ]
    data["sequence_records"] = [
        export_coordination_sequence_record(record)
        for record in sorted(
            sequencing.sequence_records,
            key=lambda item: (item.deterministic_order, item.sequence_record_id),
        )
    ]
    data["ordering_visibility"] = export_non_executable_sequence_ordering_visibility(sequencing.ordering_visibility)
    data["blocked_sequence_visibility"] = export_sequence_state_visibility(sequencing.blocked_sequence_visibility)
    data["prohibited_sequence_visibility"] = export_sequence_state_visibility(sequencing.prohibited_sequence_visibility)
    data["unsupported_sequence_visibility"] = export_sequence_state_visibility(sequencing.unsupported_sequence_visibility)
    data["stale_sequence_visibility"] = export_sequence_state_visibility(sequencing.stale_sequence_visibility)
    data["missing_sequence_visibility"] = export_sequence_state_visibility(sequencing.missing_sequence_visibility)
    data["conflicting_sequence_visibility"] = export_sequence_state_visibility(sequencing.conflicting_sequence_visibility)
    data["diagnostics"] = [
        export_coordination_sequencing_diagnostic(diagnostic)
        for diagnostic in sorted(
            sequencing.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["governance_visibility"] = export_coordination_sequencing_governance(sequencing.governance_visibility)
    return data


def serialize_coordination_sequencing_identity(identity: CoordinationSequencingIdentity) -> str:
    return stable_serialize(export_coordination_sequencing_identity(identity))


def serialize_coordination_sequencing_intelligence(sequencing: CoordinationSequencingIntelligence) -> str:
    return stable_serialize(export_coordination_sequencing_intelligence(sequencing))
