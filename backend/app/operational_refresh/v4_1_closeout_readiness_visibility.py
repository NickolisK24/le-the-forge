"""Visibility validation for v4.1 closeout readiness."""

from __future__ import annotations

from .v4_1_closeout_readiness_models import (
    CLOSEOUT_WARNING_CATEGORIES,
    PROHIBITED_CLOSEOUT_DOMAINS,
    V4_1_EXPECTED_MIGRATION_DOC_NAMES,
    V4_1_EXPECTED_PHASE_IDS,
    V4_1_EXPECTED_REPORT_NAMES,
    V4_1_EXPECTED_TEST_NAMES,
    V41CloseoutReadiness,
    V41CloseoutWarning,
    default_v4_1_closeout_readiness,
)


def count_warning_categories(warnings: tuple[V41CloseoutWarning, ...] | list[V41CloseoutWarning]) -> dict[str, int]:
    counts = {category: 0 for category in CLOSEOUT_WARNING_CATEGORIES}
    counts["invalid"] = 0
    for warning in warnings:
        if warning.category in counts:
            counts[warning.category] += 1
        else:
            counts["invalid"] += 1
    return counts


def fail_visible_warning_ids(warnings: tuple[V41CloseoutWarning, ...] | list[V41CloseoutWarning]) -> tuple[str, ...]:
    return tuple(warning.warning_id for warning in warnings if warning.fail_visible and not warning.hidden)


def _warning_action_semantics_enabled(warning: V41CloseoutWarning) -> bool:
    return (
        warning.remediation_enabled
        or warning.automatic_correction_enabled
        or warning.recommendation_enabled
        or warning.ranking_enabled
        or warning.scoring_enabled
        or warning.selection_enabled
        or warning.approval_enabled
        or warning.authorization_enabled
        or warning.orchestration_enabled
        or warning.execution_enabled
        or warning.planner_integration_enabled
        or warning.production_consumption_enabled
        or warning.runtime_mutation_enabled
    )


def validate_v4_1_closeout_visibility(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    phase_ids = tuple(phase.phase_id for phase in source.phase_coverage)
    report_names = tuple(report.report_name for report in source.report_coverage)
    doc_names = tuple(phase.required_migration_doc_name for phase in source.phase_coverage if phase.migration_doc_present)
    test_names = tuple(phase.required_focused_test_name for phase in source.phase_coverage if phase.focused_test_present)
    missing_phases = tuple(phase_id for phase_id in V4_1_EXPECTED_PHASE_IDS if phase_id not in phase_ids)
    missing_reports = tuple(
        report.report_name for report in source.report_coverage if not (report.present and report.json_valid)
    )
    missing_docs = tuple(doc_name for doc_name in V4_1_EXPECTED_MIGRATION_DOC_NAMES if doc_name not in doc_names)
    missing_tests = tuple(test_name for test_name in V4_1_EXPECTED_TEST_NAMES if test_name not in test_names)
    missing_hash_reports = tuple(report.report_name for report in source.report_coverage if not report.deterministic_hash_present)
    missing_integrity = tuple(
        report.report_name for report in source.report_coverage if not report.integrity_coverage_present
    )
    missing_continuity = tuple(
        report.report_name for report in source.report_coverage if not report.continuity_coverage_present
    )
    warning_counts = count_warning_categories(source.warnings)
    warning_ids = fail_visible_warning_ids(source.warnings)
    aggregation = source.warning_aggregation
    boundary = source.integrity_boundary
    warning_categories_visible = all(warning_counts[category] > 0 for category in CLOSEOUT_WARNING_CATEGORIES)
    warning_aggregation_valid = set(warning_ids).issubset(set(aggregation.fail_visible_warning_ids)) and set(
        aggregation.warning_ids
    ).issubset(set(warning.warning_id for warning in source.warnings))
    prohibited_domains_visible = set(PROHIBITED_CLOSEOUT_DOMAINS).issubset(set(boundary.prohibited_domains))
    hidden_phase_count = sum(1 for phase in source.phase_coverage if phase.hidden)
    hidden_report_count = sum(1 for report in source.report_coverage if report.hidden)
    hidden_warning_count = sum(1 for warning in source.warnings if warning.hidden)
    warning_action_count = sum(1 for warning in source.warnings if _warning_action_semantics_enabled(warning))
    phase_coverage_complete = not missing_phases and len(phase_ids) == len(V4_1_EXPECTED_PHASE_IDS)
    report_coverage_complete = not missing_reports and len(report_names) == len(V4_1_EXPECTED_REPORT_NAMES)
    visibility_failures = [
        not phase_coverage_complete,
        not report_coverage_complete,
        bool(missing_docs),
        bool(missing_tests),
        bool(missing_hash_reports),
        bool(missing_integrity),
        bool(missing_continuity),
        not warning_categories_visible,
        not warning_aggregation_valid,
        not prohibited_domains_visible,
        hidden_phase_count != 0,
        hidden_report_count != 0,
        hidden_warning_count != 0,
        warning_action_count != 0,
        warning_counts["invalid"] != 0,
    ]
    return {
        "valid": not any(visibility_failures),
        "phase_coverage_complete": phase_coverage_complete,
        "report_coverage_complete": report_coverage_complete,
        "migration_doc_coverage_complete": not missing_docs,
        "focused_test_coverage_complete": not missing_tests,
        "integrity_coverage_complete": not missing_integrity,
        "continuity_coverage_complete": not missing_continuity,
        "deterministic_hash_coverage_complete": not missing_hash_reports,
        "phase_count": len(source.phase_coverage),
        "expected_phase_count": len(V4_1_EXPECTED_PHASE_IDS),
        "report_count": len(source.report_coverage),
        "expected_report_count": len(V4_1_EXPECTED_REPORT_NAMES),
        "migration_doc_count": len(doc_names),
        "expected_migration_doc_count": len(V4_1_EXPECTED_MIGRATION_DOC_NAMES),
        "focused_test_count": len(test_names),
        "expected_focused_test_count": len(V4_1_EXPECTED_TEST_NAMES),
        "missing_phase_ids": missing_phases,
        "missing_report_names": missing_reports,
        "missing_migration_doc_names": missing_docs,
        "missing_focused_test_names": missing_tests,
        "missing_hash_report_names": missing_hash_reports,
        "missing_integrity_report_names": missing_integrity,
        "missing_continuity_report_names": missing_continuity,
        "warning_category_counts": warning_counts,
        "fail_visible_warning_count": len(warning_ids),
        "warning_categories_visible": warning_categories_visible,
        "unsupported_state_aggregation_visible": bool(aggregation.unsupported_state_warning_ids),
        "prohibited_state_aggregation_visible": bool(aggregation.prohibited_state_warning_ids),
        "blocked_state_aggregation_visible": bool(aggregation.blocked_state_warning_ids),
        "stale_evidence_visibility": bool(aggregation.stale_evidence_warning_ids),
        "cross_layer_continuity_conflict_visible": bool(aggregation.cross_layer_conflict_warning_ids),
        "warning_aggregation_valid": warning_aggregation_valid,
        "prohibited_domains_visible": prohibited_domains_visible,
        "hidden_phase_count": hidden_phase_count,
        "hidden_report_count": hidden_report_count,
        "hidden_warning_count": hidden_warning_count,
        "warning_action_semantics_count": warning_action_count,
    }
