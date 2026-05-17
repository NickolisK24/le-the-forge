from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from operational_lifecycle.bundle_governance_serialization import (  # noqa: E402
    serialize_trusted_bundle_governance_report,
)
from operational_lifecycle.diagnostics_engine import (  # noqa: E402
    build_operational_diagnostics_report,
    evaluate_blocked_state_diagnostic,
    evaluate_bundle_governance_diagnostic,
    evaluate_critical_diagnostic,
    evaluate_drift_diagnostic,
    evaluate_execution_boundary_diagnostic,
    evaluate_lifecycle_diagnostic,
    evaluate_lineage_diagnostic,
    evaluate_production_consumption_diagnostic,
    evaluate_prohibited_state_diagnostic,
    evaluate_provenance_diagnostic,
    evaluate_recovery_diagnostic,
    evaluate_replay_diagnostic,
    evaluate_rollback_diagnostic,
    evaluate_unknown_state_diagnostic,
    evaluate_unsupported_state_diagnostic,
    evaluate_validation_diagnostic,
    evaluate_warning_diagnostic,
)
from operational_lifecycle.diagnostics_hashing import hash_operational_diagnostics_report  # noqa: E402
from operational_lifecycle.diagnostics_models import (  # noqa: E402
    DIAGNOSTIC_CATEGORY_BLOCKED,
    DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_CATEGORY_CRITICAL,
    DIAGNOSTIC_CATEGORY_DRIFT,
    DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY,
    DIAGNOSTIC_CATEGORY_LIFECYCLE,
    DIAGNOSTIC_CATEGORY_LINEAGE,
    DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_CATEGORY_PROHIBITED,
    DIAGNOSTIC_CATEGORY_PROVENANCE,
    DIAGNOSTIC_CATEGORY_RECOVERY,
    DIAGNOSTIC_CATEGORY_REPLAY,
    DIAGNOSTIC_CATEGORY_ROLLBACK,
    DIAGNOSTIC_CATEGORY_UNKNOWN,
    DIAGNOSTIC_CATEGORY_UNSUPPORTED,
    DIAGNOSTIC_CATEGORY_VALIDATION,
    DIAGNOSTIC_CATEGORY_WARNING,
    DIAGNOSTIC_SEVERITY_BLOCKING,
    DIAGNOSTIC_SEVERITY_CRITICAL,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
    DIAGNOSTIC_SEVERITY_UNKNOWN,
    DIAGNOSTIC_SEVERITY_WARNING,
    OPERATIONAL_DIAGNOSTIC_CATEGORIES,
    OPERATIONAL_DIAGNOSTIC_TYPES,
    V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_STABLE,
)
from operational_lifecycle.diagnostics_serialization import (  # noqa: E402
    export_operational_diagnostics_report,
    serialize_operational_diagnostics_report,
)
from operational_lifecycle.diagnostics_visibility import (  # noqa: E402
    count_diagnostic_categories,
    count_diagnostic_severities,
    count_diagnostic_types,
    validate_operational_diagnostics_visibility,
)
from operational_lifecycle.lifecycle_drift_serialization import serialize_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from operational_lifecycle.production_consumption_serialization import (  # noqa: E402
    serialize_production_consumption_governance_report,
)
from operational_lifecycle.recovery_certification_serialization import (  # noqa: E402
    serialize_recovery_certification_report,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    serialize_operational_validation_report,
)
from scripts.report_v4_0_operational_explainability_diagnostics import (  # noqa: E402
    build_representative_operational_diagnostics_inputs,
    build_v4_0_operational_explainability_diagnostics_report,
)


def _representative_inputs():
    return build_representative_operational_diagnostics_inputs()


def _representative_report():
    return build_operational_diagnostics_report(*_representative_inputs())


def test_v4_0_diagnostic_entry_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [entry.deterministic_key for entry in first.entries]
    second_keys = [entry.deterministic_key for entry in second.entries]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.entry_count == 17
    assert first.entry_count == len(first.entries)


def test_v4_0_diagnostics_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_operational_diagnostics_report(first) == serialize_operational_diagnostics_report(second)
    assert hash_operational_diagnostics_report(first) == hash_operational_diagnostics_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_operational_diagnostics_report(first)
    exported = json.loads(serialize_operational_diagnostics_report(first))
    assert exported["entry_count"] == 17
    assert exported["recommendations_present"] is False
    assert exported["execution_authorized"] is False
    assert all(entry["title"] for entry in exported["entries"])
    assert all(entry["explanation"] for entry in exported["entries"])
    assert all(entry["limitation"] for entry in exported["entries"])


def test_v4_0_diagnostics_report_contains_all_required_categories_and_types():
    report = _representative_report()
    category_counts = count_diagnostic_categories(report.entries)
    diagnostic_type_counts = count_diagnostic_types(report.entries)

    assert set(OPERATIONAL_DIAGNOSTIC_CATEGORIES) <= set(category_counts)
    assert set(OPERATIONAL_DIAGNOSTIC_TYPES) <= set(diagnostic_type_counts)
    for category in OPERATIONAL_DIAGNOSTIC_CATEGORIES:
        assert category_counts[category] == 1
    for diagnostic_type in OPERATIONAL_DIAGNOSTIC_TYPES:
        assert diagnostic_type_counts[diagnostic_type] == 1
    assert category_counts["invalid"] == 0
    assert diagnostic_type_counts["invalid"] == 0


def test_v4_0_diagnostic_functions_are_descriptive_only():
    inputs = _representative_inputs()
    entries = (
        evaluate_lifecycle_diagnostic(*inputs),
        evaluate_drift_diagnostic(*inputs),
        evaluate_bundle_governance_diagnostic(*inputs),
        evaluate_validation_diagnostic(*inputs),
        evaluate_production_consumption_diagnostic(*inputs),
        evaluate_recovery_diagnostic(*inputs),
        evaluate_provenance_diagnostic(*inputs),
        evaluate_lineage_diagnostic(*inputs),
        evaluate_replay_diagnostic(*inputs),
        evaluate_rollback_diagnostic(*inputs),
        evaluate_unsupported_state_diagnostic(*inputs),
        evaluate_prohibited_state_diagnostic(*inputs),
        evaluate_blocked_state_diagnostic(*inputs),
        evaluate_unknown_state_diagnostic(*inputs),
        evaluate_warning_diagnostic(*inputs),
        evaluate_critical_diagnostic(*inputs),
        evaluate_execution_boundary_diagnostic(*inputs),
    )

    assert all(entry.descriptive_only for entry in entries)
    assert all(not entry.recommendations_present for entry in entries)
    assert all(not entry.recommendation_enabled for entry in entries)
    assert all(not entry.ranking_enabled for entry in entries)
    assert all(not entry.scoring_enabled for entry in entries)
    assert all(not entry.selection_enabled for entry in entries)
    assert all(not entry.optimization_enabled for entry in entries)
    assert all(not entry.approval_enabled for entry in entries)
    assert all(not entry.authorization_enabled for entry in entries)
    assert all(not entry.remediation_enabled for entry in entries)
    assert all(not entry.execution_authorized for entry in entries)
    assert all(not entry.execution_enabled for entry in entries)
    assert all(not entry.orchestration_execution_enabled for entry in entries)


def test_v4_0_diagnostic_layer_visibility_is_present():
    report = _representative_report()
    entries = {entry.category: entry for entry in report.entries}

    assert entries[DIAGNOSTIC_CATEGORY_LIFECYCLE].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_DRIFT].severity == DIAGNOSTIC_SEVERITY_BLOCKING
    assert entries[DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE].severity == DIAGNOSTIC_SEVERITY_BLOCKING
    assert entries[DIAGNOSTIC_CATEGORY_VALIDATION].severity == DIAGNOSTIC_SEVERITY_BLOCKING
    assert entries[DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION].severity == DIAGNOSTIC_SEVERITY_BLOCKING
    assert entries[DIAGNOSTIC_CATEGORY_RECOVERY].severity == DIAGNOSTIC_SEVERITY_PROHIBITED
    assert entries[DIAGNOSTIC_CATEGORY_PROVENANCE].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_LINEAGE].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_REPLAY].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_ROLLBACK].severity == DIAGNOSTIC_SEVERITY_WARNING


def test_v4_0_diagnostics_expose_fail_visible_states_and_counts():
    report = _representative_report()
    visibility = validate_operational_diagnostics_visibility(report)
    severity_counts = count_diagnostic_severities(report.entries)
    entries = {entry.category: entry for entry in report.entries}

    assert visibility["valid"] is True
    assert report.entry_count == 17
    assert report.unsupported_count == 1
    assert report.prohibited_count == 3
    assert report.blocked_count == 5
    assert report.unknown_count == 1
    assert report.warning_count == 7
    assert report.critical_count == 1
    assert severity_counts[DIAGNOSTIC_SEVERITY_WARNING] == 7
    assert severity_counts[DIAGNOSTIC_SEVERITY_BLOCKING] == 5
    assert severity_counts[DIAGNOSTIC_SEVERITY_PROHIBITED] == 3
    assert severity_counts[DIAGNOSTIC_SEVERITY_UNKNOWN] == 1
    assert severity_counts[DIAGNOSTIC_SEVERITY_CRITICAL] == 1
    assert entries[DIAGNOSTIC_CATEGORY_UNSUPPORTED].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_PROHIBITED].severity == DIAGNOSTIC_SEVERITY_PROHIBITED
    assert entries[DIAGNOSTIC_CATEGORY_BLOCKED].severity == DIAGNOSTIC_SEVERITY_BLOCKING
    assert entries[DIAGNOSTIC_CATEGORY_UNKNOWN].severity == DIAGNOSTIC_SEVERITY_UNKNOWN
    assert entries[DIAGNOSTIC_CATEGORY_WARNING].severity == DIAGNOSTIC_SEVERITY_WARNING
    assert entries[DIAGNOSTIC_CATEGORY_CRITICAL].severity == DIAGNOSTIC_SEVERITY_CRITICAL
    assert entries[DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY].severity == DIAGNOSTIC_SEVERITY_PROHIBITED
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_diagnostics_do_not_contain_recommendation_language():
    report = _representative_report()
    blocked_terms = (
        "recommend",
        "suggest",
        "next step",
        "should",
        "must",
        "rank",
        "score",
        "select",
        "optimize",
    )

    for entry in report.entries:
        rendered = " ".join((entry.title, entry.explanation, entry.limitation)).lower()
        for term in blocked_terms:
            assert term not in rendered


def test_v4_0_recommendations_and_execution_authorization_remain_false():
    report = _representative_report()
    exported = export_operational_diagnostics_report(report)

    assert report.recommendations_present is False
    assert report.execution_authorized is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False
    assert report.optimization_enabled is False
    assert report.approval_enabled is False
    assert report.authorization_enabled is False
    assert report.remediation_enabled is False
    assert report.execution_enabled is False
    assert report.orchestration_execution_enabled is False
    assert exported["recommendations_present"] is False
    assert exported["execution_authorized"] is False


def test_v4_0_diagnostics_do_not_mutate_inputs():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    ) = _representative_inputs()
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)
    governance_before = serialize_trusted_bundle_governance_report(governance_report)
    validation_before = serialize_operational_validation_report(validation_report)
    production_before = serialize_production_consumption_governance_report(production_consumption_report)
    recovery_before = serialize_recovery_certification_report(recovery_report)

    build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )
    build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )

    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before
    assert serialize_trusted_bundle_governance_report(governance_report) == governance_before
    assert serialize_operational_validation_report(validation_report) == validation_before
    assert serialize_production_consumption_governance_report(production_consumption_report) == production_before
    assert serialize_recovery_certification_report(recovery_report) == recovery_before


def test_v4_0_diagnostics_hash_changes_when_recovery_hash_changes():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    ) = _representative_inputs()
    baseline = build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )
    changed_recovery = replace(recovery_report, deterministic_report_hash="changed_recovery_hash")
    changed = build_operational_diagnostics_report(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        changed_recovery,
    )

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash
    assert baseline.recovery_report_hash != changed.recovery_report_hash


def test_v4_0_generated_diagnostics_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_operational_explainability_diagnostics_report()
    diagnostics_report = report["operational_diagnostics_report"]

    assert report["foundation_status"] == V4_0_OPERATIONAL_DIAGNOSTICS_STATUS_STABLE
    assert report["diagnostics_mode"] == "descriptive_only"
    assert report["diagnostic_entry_count"] == 17
    assert report["unsupported_count"] == 1
    assert report["prohibited_count"] == 3
    assert report["blocked_count"] == 5
    assert report["unknown_count"] == 1
    assert report["warning_count"] == 7
    assert report["critical_count"] == 1
    assert report["recommendations_present_status"] is False
    assert report["execution_authorized_status"] is False
    assert report["deterministic_diagnostics_report_hash"] == diagnostics_report["deterministic_report_hash"]
    assert set(report["implemented_diagnostic_categories"]) == set(OPERATIONAL_DIAGNOSTIC_CATEGORIES)
    assert set(report["implemented_diagnostic_types"]) == set(OPERATIONAL_DIAGNOSTIC_TYPES)
    assert report["non_execution_guarantees"]["recommendations_present"] is False
    assert report["non_execution_guarantees"]["ranking_absent"] is True
    assert report["non_execution_guarantees"]["scoring_absent"] is True
    assert report["non_execution_guarantees"]["selection_absent"] is True
    assert report["non_execution_guarantees"]["optimization_absent"] is True
    assert report["non_execution_guarantees"]["remediation_absent"] is True
    assert report["non_execution_guarantees"]["execution_authorized"] is False
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 7 does not generate recommendations." in report["explicit_limitations"]
    assert "v4.0 Phase 7 does not authorize execution." in report["explicit_limitations"]
