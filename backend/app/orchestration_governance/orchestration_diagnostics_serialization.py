"""Deterministic serialization for v4.3 orchestration diagnostics aggregation."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .orchestration_diagnostics_models import (
    AggregatedDiagnosticFinding,
    AggregatedExplainabilitySummary,
    CrossLayerStateSummary,
    DiagnosticsAggregationIdentity,
    DiagnosticsAggregationMetadata,
    GovernanceLayerDiagnosticSummary,
    OrchestrationDiagnosticsAggregation,
)


DIAGNOSTICS_DISABLED_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "orchestration_execution_enabled",
    "orchestration_intelligence_execution_enabled",
    "orchestration_recommendation_enabled",
    "orchestration_decision_enabled",
    "orchestration_authorization_enabled",
    "readiness_approval_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_activation_enabled",
    "runtime_coordination_enabled",
    "scheduling_execution_enabled",
    "sequencing_execution_enabled",
    "routing_execution_enabled",
    "traversal_execution_enabled",
    "dependency_resolution_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "planning_engine_enabled",
    "decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "execution_enabled",
    "recommendation_enabled",
    "decision_enabled",
    "authorization_enabled",
    "mutation_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_diagnostics_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_diagnostics_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_diagnostics_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_diagnostics_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_diagnostics_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_operational_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in DIAGNOSTICS_DISABLED_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_diagnostics_aggregation_identity(
    identity: DiagnosticsAggregationIdentity,
) -> dict[str, Any]:
    return _disable_operational_fields(asdict(identity))


def export_diagnostics_aggregation_metadata(
    metadata: DiagnosticsAggregationMetadata,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(metadata))
    for field_name in ("source_layer_ids", "source_phase_references", "source_report_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_governance_layer_diagnostic_summary(
    summary: GovernanceLayerDiagnosticSummary,
) -> dict[str, Any]:
    return _disable_operational_fields(asdict(summary))


def export_aggregated_diagnostic_finding(
    diagnostic: AggregatedDiagnosticFinding,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(diagnostic))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_aggregated_explainability_summary(
    summary: AggregatedExplainabilitySummary,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    data["affected_reference_ids"] = sorted_entries(data["affected_reference_ids"])
    return data


def export_cross_layer_state_summary(summary: CrossLayerStateSummary) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(summary))
    for field_name in (
        "source_layer_ids",
        "affected_reference_ids",
        "diagnostic_reference_ids",
        "explainability_reference_ids",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_orchestration_diagnostics_aggregation(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> dict[str, Any]:
    data = _disable_operational_fields(asdict(aggregation))
    data["identity"] = export_diagnostics_aggregation_identity(aggregation.identity)
    data["metadata"] = export_diagnostics_aggregation_metadata(aggregation.metadata)
    data["governance_layer_summaries"] = [
        export_governance_layer_diagnostic_summary(summary)
        for summary in sorted(
            aggregation.governance_layer_summaries,
            key=lambda item: (item.deterministic_order, item.layer_id),
        )
    ]
    data["diagnostics"] = [
        export_aggregated_diagnostic_finding(diagnostic)
        for diagnostic in sorted(
            aggregation.diagnostics,
            key=lambda item: (item.deterministic_order, item.aggregated_diagnostic_id),
        )
    ]
    data["explainability_summaries"] = [
        export_aggregated_explainability_summary(summary)
        for summary in sorted(
            aggregation.explainability_summaries,
            key=lambda item: (item.deterministic_order, item.aggregated_explanation_id),
        )
    ]
    data["cross_layer_state_summaries"] = [
        export_cross_layer_state_summary(summary)
        for summary in sorted(
            aggregation.cross_layer_state_summaries,
            key=lambda item: (item.deterministic_order, item.state_summary_id),
        )
    ]
    return data


def serialize_diagnostics_aggregation_identity(
    identity: DiagnosticsAggregationIdentity,
) -> str:
    return stable_serialize(export_diagnostics_aggregation_identity(identity))


def serialize_orchestration_diagnostics_aggregation(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> str:
    return stable_serialize(export_orchestration_diagnostics_aggregation(aggregation))
