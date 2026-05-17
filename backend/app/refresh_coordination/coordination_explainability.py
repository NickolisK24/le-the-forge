"""Deterministic explainability helpers for v4.2 coordination diagnostics."""

from __future__ import annotations

from typing import Any

from .coordination_diagnostics_hashing import (
    hash_coordination_explanation_record,
    hash_fail_visible_explanation_summary,
)
from .coordination_diagnostics_models import (
    CoordinationDiagnosticsExplainability,
    CoordinationExplanationRecord,
    CrossLayerCoordinationDiagnosticRecord,
    FailVisibleExplanationSummary,
    default_coordination_explanation_records,
    default_fail_visible_explanation_summary,
)


def build_coordination_explanation_records(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...],
) -> tuple[CoordinationExplanationRecord, ...]:
    return default_coordination_explanation_records(records)


def build_fail_visible_explanation_summary(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...],
    explanations: tuple[CoordinationExplanationRecord, ...],
) -> FailVisibleExplanationSummary:
    return default_fail_visible_explanation_summary(records, explanations)


def validate_fail_visible_explanation_summary(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, object]:
    fail_visible_records = tuple(record for record in diagnostics.diagnostic_records if record.fail_visible)
    explanation_by_record = {
        explanation.diagnostic_record_id: explanation for explanation in diagnostics.explanation_records
    }
    missing_explanation_ids = tuple(
        record.diagnostic_record_id
        for record in fail_visible_records
        if record.diagnostic_record_id not in explanation_by_record
    )
    summary_record_ids = set(diagnostics.fail_visible_explanation_summary.diagnostic_record_ids)
    summary_explanation_ids = set(diagnostics.fail_visible_explanation_summary.explanation_ids)
    expected_explanation_ids = tuple(
        explanation_by_record[record.diagnostic_record_id].explanation_id
        for record in fail_visible_records
        if record.diagnostic_record_id in explanation_by_record
    )
    corrective_count = sum(
        1
        for item in (*diagnostics.explanation_records, diagnostics.fail_visible_explanation_summary)
        if getattr(item, "remediation_enabled", False)
        or getattr(item, "automatic_correction_enabled", False)
        or getattr(item, "drift_correction_enabled", False)
        or getattr(item, "drift_remediation_enabled", False)
        or getattr(item, "routing_execution_enabled", False)
        or getattr(item, "orchestration_execution_enabled", False)
        or getattr(item, "refresh_execution_enabled", False)
        or getattr(item, "dependency_resolution_enabled", False)
        or getattr(item, "runtime_mutation_enabled", False)
    )
    return {
        "valid": (
            len(missing_explanation_ids) == 0
            and set(record.diagnostic_record_id for record in fail_visible_records).issubset(summary_record_ids)
            and set(expected_explanation_ids).issubset(summary_explanation_ids)
            and diagnostics.fail_visible_explanation_summary.fail_visible
            and diagnostics.fail_visible_explanation_summary.descriptive_only
            and corrective_count == 0
        ),
        "fail_visible_record_ids": tuple(record.diagnostic_record_id for record in fail_visible_records),
        "summary_diagnostic_record_ids": diagnostics.fail_visible_explanation_summary.diagnostic_record_ids,
        "summary_explanation_ids": diagnostics.fail_visible_explanation_summary.explanation_ids,
        "missing_explanation_ids": missing_explanation_ids,
        "summary_lines": diagnostics.fail_visible_explanation_summary.summary_lines,
        "aggregation_state_counts": diagnostics.fail_visible_explanation_summary.aggregation_state_counts,
        "corrective_count": corrective_count,
    }


def build_coordination_explainability_evidence(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, Any]:
    summary_validation = validate_fail_visible_explanation_summary(diagnostics)
    return {
        "explanation_hashes": [
            hash_coordination_explanation_record(record) for record in diagnostics.explanation_records
        ],
        "fail_visible_summary_hash": hash_fail_visible_explanation_summary(
            diagnostics.fail_visible_explanation_summary
        ),
        "explanation_count": len(diagnostics.explanation_records),
        "fail_visible_explanation_count": sum(1 for record in diagnostics.explanation_records if record.fail_visible),
        "summary_validation": summary_validation,
        "summary_lines": diagnostics.fail_visible_explanation_summary.summary_lines,
    }
