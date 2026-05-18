"""Deterministic hashing for v4.5A.6 drift diagnostics aggregation."""

from __future__ import annotations

import hashlib
from typing import Any

from .v4_5a_6_drift_diagnostics_aggregation_models import (
    AggregatedDiagnosticRecord,
    BlockerWarningSummaryVisibility,
    ContinuityGapSummaryVisibility,
    DiagnosticAggregationRecord,
    DiagnosticSeveritySummaryVisibility,
    DiagnosticSourceAggregation,
    DriftDiagnosticsAggregationIdentity,
    DriftDiagnosticsAggregationIntelligence,
    EvidenceGapSummaryVisibility,
    UnsupportedAggregationVisibility,
    UnsupportedStateSummaryVisibility,
)
from .v4_5a_6_drift_diagnostics_aggregation_serialization import (
    export_aggregated_diagnostic_record,
    export_blocker_warning_summary_visibility,
    export_continuity_gap_summary_visibility,
    export_diagnostic_aggregation_record,
    export_diagnostic_severity_summary_visibility,
    export_diagnostic_source_aggregation,
    export_drift_diagnostics_aggregation_identity,
    export_evidence_gap_summary_visibility,
    export_unsupported_aggregation_visibility,
    export_unsupported_state_summary_visibility,
    export_v4_5a_6_drift_diagnostics_aggregation,
    stable_serialize_v4_5a_6_drift_diagnostics_aggregation,
)


def deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(payload: Any) -> str:
    return hashlib.sha256(
        stable_serialize_v4_5a_6_drift_diagnostics_aggregation(payload).encode(
            "utf-8"
        )
    ).hexdigest()


def hash_drift_diagnostics_aggregation_identity(
    identity: DriftDiagnosticsAggregationIdentity,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_drift_diagnostics_aggregation_identity(identity)
    )


def hash_diagnostic_aggregation_record(record: DiagnosticAggregationRecord) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_diagnostic_aggregation_record(record)
    )


def hash_diagnostic_source_aggregation(record: DiagnosticSourceAggregation) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_diagnostic_source_aggregation(record)
    )


def hash_unsupported_state_summary_visibility(
    record: UnsupportedStateSummaryVisibility,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_unsupported_state_summary_visibility(record)
    )


def hash_evidence_gap_summary_visibility(record: EvidenceGapSummaryVisibility) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_evidence_gap_summary_visibility(record)
    )


def hash_continuity_gap_summary_visibility(
    record: ContinuityGapSummaryVisibility,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_continuity_gap_summary_visibility(record)
    )


def hash_diagnostic_severity_summary_visibility(
    record: DiagnosticSeveritySummaryVisibility,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_diagnostic_severity_summary_visibility(record)
    )


def hash_blocker_warning_summary_visibility(
    record: BlockerWarningSummaryVisibility,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_blocker_warning_summary_visibility(record)
    )


def hash_aggregated_diagnostic_record(record: AggregatedDiagnosticRecord) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_aggregated_diagnostic_record(record)
    )


def hash_unsupported_aggregation_visibility(
    record: UnsupportedAggregationVisibility,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_unsupported_aggregation_visibility(record)
    )


def hash_v4_5a_6_drift_diagnostics_aggregation(
    intelligence: DriftDiagnosticsAggregationIntelligence,
) -> str:
    return deterministic_v4_5a_6_drift_diagnostics_aggregation_hash(
        export_v4_5a_6_drift_diagnostics_aggregation(intelligence)
    )
