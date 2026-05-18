"""Deterministic hashing for v4.3 orchestration diagnostics aggregation."""

from __future__ import annotations

import hashlib
from typing import Any

from .orchestration_diagnostics_models import (
    AggregatedDiagnosticFinding,
    AggregatedExplainabilitySummary,
    CrossLayerStateSummary,
    DiagnosticsAggregationIdentity,
    GovernanceLayerDiagnosticSummary,
    OrchestrationDiagnosticsAggregation,
)
from .orchestration_diagnostics_serialization import (
    export_aggregated_diagnostic_finding,
    export_aggregated_explainability_summary,
    export_cross_layer_state_summary,
    export_diagnostics_aggregation_identity,
    export_governance_layer_diagnostic_summary,
    export_orchestration_diagnostics_aggregation,
    stable_serialize,
)


def deterministic_diagnostics_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_diagnostics_aggregation_identity(identity: DiagnosticsAggregationIdentity) -> str:
    return deterministic_diagnostics_hash(export_diagnostics_aggregation_identity(identity))


def hash_governance_layer_diagnostic_summary(
    summary: GovernanceLayerDiagnosticSummary,
) -> str:
    return deterministic_diagnostics_hash(export_governance_layer_diagnostic_summary(summary))


def hash_aggregated_diagnostic_finding(diagnostic: AggregatedDiagnosticFinding) -> str:
    return deterministic_diagnostics_hash(export_aggregated_diagnostic_finding(diagnostic))


def hash_aggregated_explainability_summary(
    summary: AggregatedExplainabilitySummary,
) -> str:
    return deterministic_diagnostics_hash(export_aggregated_explainability_summary(summary))


def hash_cross_layer_state_summary(summary: CrossLayerStateSummary) -> str:
    return deterministic_diagnostics_hash(export_cross_layer_state_summary(summary))


def hash_orchestration_diagnostics_aggregation(
    aggregation: OrchestrationDiagnosticsAggregation,
) -> str:
    return deterministic_diagnostics_hash(export_orchestration_diagnostics_aggregation(aggregation))
