"""Deterministic serialization for v4.1 diagnostics explainability."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from operational_lifecycle.lifecycle_serialization import stable_serialize

from .refresh_diagnostics_explainability_models import (
    RefreshDiagnosticsExplainability,
    RefreshDiagnosticsExplainabilityIdentity,
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


CAPABILITY_FIELDS: tuple[str, ...] = (
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_repair_enabled",
    "refresh_execution_enabled",
    "orchestration_enabled",
    "automatic_sequencing_enabled",
    "dependency_resolution_enabled",
    "schema_migration_execution_enabled",
    "automatic_migration_enabled",
    "rollback_execution_enabled",
    "recovery_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "recommendation_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "optimization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
    "runtime_mutation_enabled",
    "hidden_remediation_behavior_enabled",
    "hidden_orchestration_behavior_enabled",
    "implicit_execution_pathway_enabled",
    "hidden_fallback_enabled",
    "hidden",
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


def export_diagnostics_explainability_identity(
    identity: RefreshDiagnosticsExplainabilityIdentity,
) -> dict[str, Any]:
    return _export_record(identity)


def export_refresh_diagnostics_explainability(payload: RefreshDiagnosticsExplainability) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(payload))
    data["identity"] = export_diagnostics_explainability_identity(payload.identity)
    data["diagnostic_summaries"] = [
        _export_record(summary)
        for summary in sorted(
            payload.diagnostic_summaries,
            key=lambda item: (item.deterministic_order, item.diagnostic_id),
        )
    ]
    data["explanation_summaries"] = [
        _export_record(summary)
        for summary in sorted(
            payload.explanation_summaries,
            key=lambda item: (item.deterministic_order, item.explanation_id),
        )
    ]
    data["diagnostic_aggregation"] = _export_record(payload.diagnostic_aggregation)
    data["explanation_aggregation"] = _export_record(payload.explanation_aggregation)
    data["continuity_metadata"] = _export_record(payload.continuity_metadata)
    data["integrity_boundary"] = _export_record(payload.integrity_boundary)
    data["governance"] = _export_record(payload.governance)
    return data


def serialize_diagnostics_explainability_identity(identity: RefreshDiagnosticsExplainabilityIdentity) -> str:
    return stable_serialize(export_diagnostics_explainability_identity(identity))


def serialize_refresh_diagnostics_explainability(payload: RefreshDiagnosticsExplainability) -> str:
    return stable_serialize(export_refresh_diagnostics_explainability(payload))
