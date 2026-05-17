"""Deterministic hashing for v4.2 coordination diagnostics explainability."""

from __future__ import annotations

import hashlib
from typing import Any

from .coordination_diagnostics_models import (
    CoordinationDiagnosticsExplainability,
    CoordinationDiagnosticsIdentity,
    CoordinationExplanationRecord,
    CrossLayerCoordinationDiagnosticRecord,
    DiagnosticSeverityVisibility,
    FailVisibleExplanationSummary,
    StateAggregationVisibility,
)
from .coordination_diagnostics_serialization import (
    export_coordination_diagnostics_explainability,
    export_coordination_diagnostics_identity,
    export_coordination_explanation_record,
    export_cross_layer_coordination_diagnostic_record,
    export_diagnostic_severity_visibility,
    export_fail_visible_explanation_summary,
    export_state_aggregation_visibility,
    stable_serialize,
)


def deterministic_coordination_diagnostics_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize(payload).encode("utf-8")).hexdigest()


def hash_coordination_diagnostics_identity(identity: CoordinationDiagnosticsIdentity) -> str:
    return deterministic_coordination_diagnostics_hash(export_coordination_diagnostics_identity(identity))


def hash_cross_layer_coordination_diagnostic_record(record: CrossLayerCoordinationDiagnosticRecord) -> str:
    return deterministic_coordination_diagnostics_hash(export_cross_layer_coordination_diagnostic_record(record))


def hash_state_aggregation_visibility(visibility: StateAggregationVisibility) -> str:
    return deterministic_coordination_diagnostics_hash(export_state_aggregation_visibility(visibility))


def hash_diagnostic_severity_visibility(visibility: DiagnosticSeverityVisibility) -> str:
    return deterministic_coordination_diagnostics_hash(export_diagnostic_severity_visibility(visibility))


def hash_coordination_explanation_record(record: CoordinationExplanationRecord) -> str:
    return deterministic_coordination_diagnostics_hash(export_coordination_explanation_record(record))


def hash_fail_visible_explanation_summary(summary: FailVisibleExplanationSummary) -> str:
    return deterministic_coordination_diagnostics_hash(export_fail_visible_explanation_summary(summary))


def hash_coordination_diagnostics_explainability(diagnostics: CoordinationDiagnosticsExplainability) -> str:
    return deterministic_coordination_diagnostics_hash(export_coordination_diagnostics_explainability(diagnostics))
