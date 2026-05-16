"""Deterministic coordination boundary intelligence models for v3.8.

These models classify coordination boundary evidence only. They do not route,
schedule, dispatch, traverse, mutate, optimize, recommend, authorize, or execute
orchestration behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .coordination_foundation_models import deterministic_hash, stable_serialize


V3_8_COORDINATION_BOUNDARY_INTELLIGENCE_PHASE_ID = "v3_8_coordination_boundary_intelligence"
V3_8_COORDINATION_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION = (
    "v3_8.coordination_boundary_intelligence.1"
)
V3_8_BOUNDARY_AUDIT_STABLE = "v3_8_coordination_boundary_intelligence_stable"
V3_8_BOUNDARY_AUDIT_BLOCKED = "v3_8_coordination_boundary_intelligence_blocked"

BOUNDARY_CLASSIFICATION_SUPPORTED = "supported"
BOUNDARY_CLASSIFICATION_UNSUPPORTED = "unsupported"
BOUNDARY_CLASSIFICATION_PROHIBITED = "prohibited"
BOUNDARY_CLASSIFICATION_UNKNOWN = "unknown"
BOUNDARY_CLASSIFICATION_EXPERIMENTAL = "experimental"
BOUNDARY_CLASSIFICATION_PLANNING_ONLY = "planning_only"
BOUNDARY_CLASSIFICATION_NON_EXECUTABLE = "non_executable"
BOUNDARY_CLASSIFICATIONS: tuple[str, ...] = (
    BOUNDARY_CLASSIFICATION_SUPPORTED,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
)

BOUNDARY_VISIBILITY_VISIBLE = "visible"
BOUNDARY_VISIBILITY_FAIL_VISIBLE = "fail_visible"
BOUNDARY_SEVERITY_INFO = "info"
BOUNDARY_SEVERITY_WARNING = "warning"
BOUNDARY_SEVERITY_BLOCKED = "blocked"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


def _sorted_entries(values: tuple[str, ...] | list[str]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class V38CoordinationBoundaryIdentity:
    boundary_id: str
    boundary_source_id: str
    boundary_source_type: str
    schema_version: str = V3_8_COORDINATION_BOUNDARY_INTELLIGENCE_SCHEMA_VERSION
    phase_id: str = V3_8_COORDINATION_BOUNDARY_INTELLIGENCE_PHASE_ID


@dataclass(frozen=True)
class V38CoordinationBoundaryEvidence:
    evidence_id: str
    source_coordination_reference: str
    provenance_reference: str
    continuity_reference: str
    replay_evidence_reference: str
    rollback_evidence_reference: str
    deterministic_hash_reference: str
    evidence_scope: str = "coordination_boundary_audit_evidence_only"
    replay_safe: bool = True
    rollback_safe: bool = True
    provenance_preserved: bool = True
    non_executable: bool = True


@dataclass(frozen=True)
class V38CoordinationBoundaryRecord:
    identity: V38CoordinationBoundaryIdentity
    classification: str
    severity: str
    visibility_status: str
    explanation: str
    evidence: V38CoordinationBoundaryEvidence
    provenance_reference_ids: tuple[str, ...]
    continuity_reference_ids: tuple[str, ...]
    replay_reference_ids: tuple[str, ...]
    rollback_reference_ids: tuple[str, ...]
    supported_risk_hidden: bool = False
    fail_visible: bool = True
    hidden: bool = False
    non_executable: bool = True
    execution_capability_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "provenance_reference_ids",
            "continuity_reference_ids",
            "replay_reference_ids",
            "rollback_reference_ids",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationBoundaryFinding:
    finding_id: str
    source_coordination_reference: str
    boundary_id: str
    boundary_classification: str
    severity: str
    explanation: str
    provenance_reference: str
    replay_safe_evidence: tuple[str, ...]
    rollback_safe_evidence: tuple[str, ...]
    deterministic_visibility_status: str
    non_execution_confirmation: bool
    fail_visible: bool = True
    hidden: bool = False
    blocks_boundary_intelligence: bool = False
    execution_behavior_detected: bool = False

    def __post_init__(self) -> None:
        for field_name in ("replay_safe_evidence", "rollback_safe_evidence"):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V38CoordinationBoundaryAudit:
    audit_id: str
    audit_status: str
    source_foundation_id: str
    boundary_records: tuple[V38CoordinationBoundaryRecord, ...]
    findings: tuple[V38CoordinationBoundaryFinding, ...]
    classification_counts: Mapping[str, int]
    validation_totals: Mapping[str, int | bool | str]
    deterministic_boundary_hash: str = ""
    non_executable: bool = True
    coordination_execution_enabled: bool = False
    orchestration_execution_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    traversal_execution_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    execution_authorization_enabled: bool = False
    callable_coordination_flow_enabled: bool = False
    persistent_runtime_mutation_enabled: bool = False
    hidden_transition_enabled: bool = False
    silent_fallback_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in ("boundary_records", "findings"):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_8_boundary_identity(identity: V38CoordinationBoundaryIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v3_8_boundary_evidence(evidence: V38CoordinationBoundaryEvidence) -> dict[str, Any]:
    return asdict(evidence)


def export_v3_8_boundary_record(record: V38CoordinationBoundaryRecord) -> dict[str, Any]:
    data = {
        "identity": export_v3_8_boundary_identity(record.identity),
        "classification": record.classification,
        "severity": record.severity,
        "visibility_status": record.visibility_status,
        "explanation": record.explanation,
        "evidence": export_v3_8_boundary_evidence(record.evidence),
        "provenance_reference_ids": _sorted_entries(record.provenance_reference_ids),
        "continuity_reference_ids": _sorted_entries(record.continuity_reference_ids),
        "replay_reference_ids": _sorted_entries(record.replay_reference_ids),
        "rollback_reference_ids": _sorted_entries(record.rollback_reference_ids),
        "supported_risk_hidden": record.supported_risk_hidden,
        "fail_visible": record.fail_visible,
        "hidden": record.hidden,
        "non_executable": record.non_executable,
        "execution_capability_enabled": record.execution_capability_enabled,
    }
    return data


def export_v3_8_boundary_finding(finding: V38CoordinationBoundaryFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["replay_safe_evidence"] = _sorted_entries(data["replay_safe_evidence"])
    data["rollback_safe_evidence"] = _sorted_entries(data["rollback_safe_evidence"])
    return data


def export_v3_8_boundary_audit(audit: V38CoordinationBoundaryAudit) -> dict[str, Any]:
    return {
        "audit_id": audit.audit_id,
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "boundary_records": [
            export_v3_8_boundary_record(record)
            for record in sorted(
                audit.boundary_records,
                key=lambda item: (item.classification, item.identity.boundary_id),
            )
        ],
        "findings": [
            export_v3_8_boundary_finding(finding)
            for finding in sorted(audit.findings, key=lambda item: item.finding_id)
        ],
        "classification_counts": dict(sorted(audit.classification_counts.items())),
        "validation_totals": dict(sorted(audit.validation_totals.items())),
        "deterministic_boundary_hash": audit.deterministic_boundary_hash,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
    }


def serialize_v3_8_boundary_audit(audit: V38CoordinationBoundaryAudit) -> str:
    return stable_serialize(export_v3_8_boundary_audit(audit))


def hash_v3_8_boundary_audit(audit: V38CoordinationBoundaryAudit) -> str:
    data = export_v3_8_boundary_audit(audit)
    data.pop("deterministic_boundary_hash", None)
    return deterministic_hash(data)


def validate_v3_8_boundary_serialization_stability(
    audit: V38CoordinationBoundaryAudit,
) -> dict[str, Any]:
    first = serialize_v3_8_boundary_audit(audit)
    second = serialize_v3_8_boundary_audit(audit)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_v3_8_boundary_intelligence",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_8_boundary_hash_stability(audit: V38CoordinationBoundaryAudit) -> dict[str, Any]:
    first = hash_v3_8_boundary_audit(audit)
    second = hash_v3_8_boundary_audit(audit)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_v3_8_boundary_intelligence",
    }


def boundary_finding_id(classification: str, boundary_id: str) -> str:
    return f"v3_8_boundary_{classification}_{boundary_id}"

