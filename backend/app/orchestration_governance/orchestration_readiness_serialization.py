"""Deterministic serialization for v4.3 orchestration readiness certification."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_readiness_models import (
    OrchestrationReadinessCertification,
    ReadinessCertificationIdentity,
    ReadinessCertificationMetadata,
    ReadinessCertificationRecord,
    ReadinessDiagnostic,
    ReadinessExplainability,
    ReadinessStateSummary,
)


READINESS_DISABLED_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "readiness_approved",
    "orchestration_execution_enabled",
    "orchestration_authorization_enabled",
    "orchestration_approval_enabled",
    "readiness_approval_enabled",
    "orchestration_decision_enabled",
    "orchestration_recommendation_enabled",
    "orchestration_routing_enabled",
    "orchestration_traversal_enabled",
    "orchestration_scheduling_enabled",
    "orchestration_sequencing_enabled",
    "orchestration_activation_enabled",
    "orchestration_coordination_execution_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_runtime_behavior_enabled",
    "orchestration_planning_engine_enabled",
    "orchestration_decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_authorization_enabled",
    "dependency_resolution_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
    "activation_enabled",
    "decision_enabled",
    "recommendation_enabled",
    "mutation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_readiness_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_readiness_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_readiness_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_readiness_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_readiness_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_operational_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in READINESS_DISABLED_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_readiness_certification_identity(
    identity: ReadinessCertificationIdentity,
) -> dict[str, Any]:
    return _disable_operational_fields(asdict(identity))


def export_readiness_certification_metadata(
    metadata: ReadinessCertificationMetadata,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("source_layer_ids", "source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_readiness_certification_record(
    certification: ReadinessCertificationRecord,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(certification))
    for field_name in (
        "certified_layer_ids",
        "evidence_reference_ids",
        "readiness_gap_ids",
        "governance_instability_ids",
        "continuity_failure_ids",
        "integrity_failure_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_readiness_state_summary(summary: ReadinessStateSummary) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    for field_name in ("affected_layer_ids", "affected_reference_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_readiness_diagnostic(diagnostic: ReadinessDiagnostic) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(diagnostic))
    for field_name in ("affected_readiness_ids", "affected_state_summary_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_readiness_explainability(summary: ReadinessExplainability) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_orchestration_readiness_certification(
    certification: OrchestrationReadinessCertification,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(certification))
    data["identity"] = export_readiness_certification_identity(certification.identity)
    data["metadata"] = export_readiness_certification_metadata(certification.metadata)
    data["readiness_certifications"] = [
        export_readiness_certification_record(item)
        for item in sorted(
            certification.readiness_certifications,
            key=lambda item: (item.deterministic_order, item.readiness_id),
        )
    ]
    data["state_readiness_summaries"] = [
        export_readiness_state_summary(item)
        for item in sorted(
            certification.state_readiness_summaries,
            key=lambda item: (item.deterministic_order, item.state_summary_id),
        )
    ]
    data["diagnostics"] = [
        export_readiness_diagnostic(item)
        for item in sorted(
            certification.diagnostics,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explainability_summaries"] = [
        export_readiness_explainability(item)
        for item in sorted(
            certification.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    return data


def serialize_readiness_certification_identity(
    identity: ReadinessCertificationIdentity,
) -> str:
    return stable_serialize(export_readiness_certification_identity(identity))


def serialize_orchestration_readiness_certification(
    certification: OrchestrationReadinessCertification,
) -> str:
    return stable_serialize(export_orchestration_readiness_certification(certification))
