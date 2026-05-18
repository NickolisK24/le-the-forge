"""Deterministic hashing for v4.4 boundary explainability aggregation."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_4_boundary_explainability_aggregation_models import (
    BoundaryExplainabilityAggregationIdentity,
    BoundaryExplainabilityAggregationIntelligence,
    DiagnosticAggregationIdentity,
    DiagnosticAggregationRecord,
    ExplainabilityAggregationRecord,
    ExplanationCoverageSummary,
    ExplanationTraceRecord,
    LineageAggregationSummary,
    PhaseEvidenceSummary,
    ProvenanceAggregationSummary,
    ReplayRollbackAggregationSummary,
    SourceEvidenceReference,
)
from .v4_4_boundary_explainability_aggregation_serialization import (
    export_boundary_explainability_aggregation_identity,
    export_boundary_explainability_aggregation_intelligence,
    export_diagnostic_aggregation_identity,
    export_diagnostic_aggregation_record,
    export_explainability_aggregation_record,
    export_explanation_coverage_summary,
    export_explanation_trace,
    export_lineage_aggregation_summary,
    export_phase_evidence_summary,
    export_provenance_aggregation_summary,
    export_replay_rollback_aggregation_summary,
    export_source_evidence_reference,
    stable_serialize_boundary_explainability_aggregation,
)


def deterministic_boundary_explainability_aggregation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_boundary_explainability_aggregation(payload).encode("utf-8")
    ).hexdigest()


def hash_boundary_explainability_aggregation_identity(
    identity: BoundaryExplainabilityAggregationIdentity,
) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_boundary_explainability_aggregation_identity(identity)
    )


def hash_diagnostic_aggregation_identity(identity: DiagnosticAggregationIdentity) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_diagnostic_aggregation_identity(identity)
    )


def hash_source_evidence_reference(record: SourceEvidenceReference) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_source_evidence_reference(record)
    )


def hash_phase_evidence_summary(summary: PhaseEvidenceSummary) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_phase_evidence_summary(summary)
    )


def hash_explainability_aggregation_record(record: ExplainabilityAggregationRecord) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_explainability_aggregation_record(record)
    )


def hash_diagnostic_aggregation_record(record: DiagnosticAggregationRecord) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_diagnostic_aggregation_record(record)
    )


def hash_explanation_coverage_summary(summary: ExplanationCoverageSummary) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_explanation_coverage_summary(summary)
    )


def hash_explanation_trace(record: ExplanationTraceRecord) -> str:
    return deterministic_boundary_explainability_aggregation_hash(export_explanation_trace(record))


def hash_provenance_aggregation_summary(summary: ProvenanceAggregationSummary) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_provenance_aggregation_summary(summary)
    )


def hash_lineage_aggregation_summary(summary: LineageAggregationSummary) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_lineage_aggregation_summary(summary)
    )


def hash_replay_rollback_aggregation_summary(summary: ReplayRollbackAggregationSummary) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_replay_rollback_aggregation_summary(summary)
    )


def hash_boundary_explainability_aggregation_intelligence(
    intelligence: BoundaryExplainabilityAggregationIntelligence,
) -> str:
    return deterministic_boundary_explainability_aggregation_hash(
        export_boundary_explainability_aggregation_intelligence(intelligence)
    )
