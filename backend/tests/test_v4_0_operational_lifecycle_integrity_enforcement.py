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
from operational_lifecycle.diagnostics_serialization import serialize_operational_diagnostics_report  # noqa: E402
from operational_lifecycle.integrity_enforcement_audit import (  # noqa: E402
    audit_approval_leakage,
    audit_authorization_leakage,
    audit_diagnostic_suppression,
    audit_evidence_continuity,
    audit_execution_leakage,
    audit_fallback_leakage,
    audit_lineage_continuity,
    audit_mutation_leakage,
    audit_operational_lifecycle_integrity,
    audit_orchestration_leakage,
    audit_planner_integration_leakage,
    audit_production_consumption_leakage,
    audit_prohibited_state,
    audit_provenance_continuity,
    audit_ranking_leakage,
    audit_recommendation_leakage,
    audit_remediation_leakage,
    audit_replay_continuity,
    audit_rollback_continuity,
    audit_scoring_leakage,
    audit_selection_leakage,
    build_integrity_leakage_summary,
)
from operational_lifecycle.integrity_enforcement_hashing import hash_operational_integrity_report  # noqa: E402
from operational_lifecycle.integrity_enforcement_models import (  # noqa: E402
    INTEGRITY_FINDING_APPROVAL_LEAKAGE,
    INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE,
    INTEGRITY_FINDING_BOUNDARY,
    INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION,
    INTEGRITY_FINDING_EVIDENCE_CONTINUITY,
    INTEGRITY_FINDING_EXECUTION_LEAKAGE,
    INTEGRITY_FINDING_FALLBACK_LEAKAGE,
    INTEGRITY_FINDING_LINEAGE_CONTINUITY,
    INTEGRITY_FINDING_MUTATION_LEAKAGE,
    INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE,
    INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE,
    INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE,
    INTEGRITY_FINDING_PROHIBITED_STATE,
    INTEGRITY_FINDING_PROVENANCE_CONTINUITY,
    INTEGRITY_FINDING_RANKING_LEAKAGE,
    INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE,
    INTEGRITY_FINDING_REMEDIATION_LEAKAGE,
    INTEGRITY_FINDING_REPLAY_CONTINUITY,
    INTEGRITY_FINDING_ROLLBACK_CONTINUITY,
    INTEGRITY_FINDING_SCORING_LEAKAGE,
    INTEGRITY_FINDING_SELECTION_LEAKAGE,
    INTEGRITY_SEVERITY_CRITICAL,
    INTEGRITY_SEVERITY_INFO,
    INTEGRITY_SEVERITY_PROHIBITED,
    INTEGRITY_STATUS_PROHIBITED,
    INTEGRITY_STATUS_VIOLATION,
    OPERATIONAL_INTEGRITY_FINDING_TYPES,
    V4_0_INTEGRITY_ENFORCEMENT_STATUS_STABLE,
)
from operational_lifecycle.integrity_enforcement_serialization import (  # noqa: E402
    export_operational_integrity_report,
    serialize_operational_integrity_report,
)
from operational_lifecycle.integrity_enforcement_visibility import (  # noqa: E402
    count_integrity_finding_types,
    count_integrity_severities,
    validate_operational_integrity_visibility,
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
from scripts.report_v4_0_operational_lifecycle_integrity_enforcement import (  # noqa: E402
    build_representative_operational_integrity_inputs,
    build_v4_0_operational_lifecycle_integrity_enforcement_report,
)


def _representative_inputs():
    return build_representative_operational_integrity_inputs()


def _representative_report():
    return audit_operational_lifecycle_integrity(*_representative_inputs())


def test_v4_0_integrity_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 21
    assert first.finding_count == len(first.findings)


def test_v4_0_integrity_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_operational_integrity_report(first) == serialize_operational_integrity_report(second)
    assert hash_operational_integrity_report(first) == hash_operational_integrity_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_operational_integrity_report(first)
    exported = json.loads(serialize_operational_integrity_report(first))
    assert exported["finding_count"] == 21
    assert exported["integrity_enforcement_performed"] is True
    assert all(finding["source_phase"] for finding in exported["findings"])
    assert all(finding["diagnostics_reference"] for finding in exported["findings"])


def test_v4_0_integrity_report_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_integrity_finding_types(report.findings)

    assert set(OPERATIONAL_INTEGRITY_FINDING_TYPES) <= set(finding_type_counts)
    for finding_type in OPERATIONAL_INTEGRITY_FINDING_TYPES:
        assert finding_type_counts[finding_type] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_integrity_leakage_checks_are_visible_and_descriptive_only():
    inputs = _representative_inputs()
    leakage = build_integrity_leakage_summary(*inputs)
    findings = (
        audit_execution_leakage(*inputs, leakage),
        audit_orchestration_leakage(*inputs, leakage),
        audit_remediation_leakage(*inputs, leakage),
        audit_recommendation_leakage(*inputs, leakage),
        audit_ranking_leakage(*inputs, leakage),
        audit_scoring_leakage(*inputs, leakage),
        audit_selection_leakage(*inputs, leakage),
        audit_approval_leakage(*inputs, leakage),
        audit_authorization_leakage(*inputs, leakage),
        audit_mutation_leakage(*inputs, leakage),
        audit_production_consumption_leakage(*inputs, leakage),
        audit_planner_integration_leakage(*inputs, leakage),
        audit_fallback_leakage(*inputs, leakage),
    )

    assert all(not value for value in leakage.values())
    assert all(finding.severity == INTEGRITY_SEVERITY_INFO for finding in findings)
    assert all(finding.descriptive_only for finding in findings)
    assert all(not finding.remediation_enabled for finding in findings)
    assert all(not finding.execution_enabled for finding in findings)
    assert all(not finding.orchestration_execution_enabled for finding in findings)
    assert all(not finding.recommendation_enabled for finding in findings)
    assert all(not finding.ranking_enabled for finding in findings)
    assert all(not finding.scoring_enabled for finding in findings)
    assert all(not finding.selection_enabled for finding in findings)


def test_v4_0_integrity_continuity_and_boundary_checks_are_visible():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            audit_diagnostic_suppression(*inputs),
            audit_evidence_continuity(*inputs),
            audit_provenance_continuity(*inputs),
            audit_lineage_continuity(*inputs),
            audit_replay_continuity(*inputs),
            audit_rollback_continuity(*inputs),
            audit_prohibited_state(*inputs),
        )
    }

    assert findings[INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_EVIDENCE_CONTINUITY].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_PROVENANCE_CONTINUITY].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_LINEAGE_CONTINUITY].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_REPLAY_CONTINUITY].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_ROLLBACK_CONTINUITY].severity == INTEGRITY_SEVERITY_INFO
    assert findings[INTEGRITY_FINDING_PROHIBITED_STATE].severity == INTEGRITY_SEVERITY_PROHIBITED


def test_v4_0_integrity_counts_and_visibility_are_fail_visible():
    report = _representative_report()
    visibility = validate_operational_integrity_visibility(report)
    severity_counts = count_integrity_severities(report.findings)
    findings = {finding.finding_type: finding for finding in report.findings}

    assert visibility["valid"] is True
    assert report.integrity_status == INTEGRITY_STATUS_PROHIBITED
    assert report.violation_count == 0
    assert report.warning_count == 0
    assert report.blocked_count == 0
    assert report.prohibited_count == 1
    assert report.unknown_count == 0
    assert report.critical_count == 0
    assert severity_counts[INTEGRITY_SEVERITY_INFO] == 20
    assert severity_counts[INTEGRITY_SEVERITY_PROHIBITED] == 1
    assert findings[INTEGRITY_FINDING_PROHIBITED_STATE].severity == INTEGRITY_SEVERITY_PROHIBITED
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_integrity_leakage_booleans_are_all_implemented_and_false_for_representative_evidence():
    report = _representative_report()

    assert report.execution_leakage_detected is False
    assert report.orchestration_leakage_detected is False
    assert report.remediation_leakage_detected is False
    assert report.recommendation_leakage_detected is False
    assert report.ranking_leakage_detected is False
    assert report.scoring_leakage_detected is False
    assert report.selection_leakage_detected is False
    assert report.approval_leakage_detected is False
    assert report.authorization_leakage_detected is False
    assert report.mutation_leakage_detected is False
    assert report.production_consumption_leakage_detected is False
    assert report.planner_integration_leakage_detected is False
    assert report.integrity_enforcement_performed is True


def test_v4_0_integrity_detects_injected_execution_leakage_without_remediation():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    ) = _representative_inputs()
    changed_validation = replace(validation_report, execution_enabled=True)
    report = audit_operational_lifecycle_integrity(
        lifecycle_foundation,
        drift_report,
        governance_report,
        changed_validation,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )
    findings = {finding.finding_type: finding for finding in report.findings}

    assert report.execution_leakage_detected is True
    assert report.integrity_status == INTEGRITY_STATUS_VIOLATION
    assert findings[INTEGRITY_FINDING_EXECUTION_LEAKAGE].severity == INTEGRITY_SEVERITY_CRITICAL
    assert report.remediation_enabled is False
    assert report.execution_enabled is False


def test_v4_0_integrity_detects_injected_non_execution_leakage_booleans():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    ) = _representative_inputs()
    changed_lifecycle = replace(
        lifecycle_foundation,
        recommendation_enabled=True,
        ranking_enabled=True,
        scoring_enabled=True,
        selection_enabled=True,
        approval_enabled=True,
        authorization_enabled=True,
        runtime_mutation_enabled=True,
    )
    changed_drift = replace(drift_report, remediation_enabled=True)
    changed_governance = replace(governance_report, production_bundle_consumption_enabled=True)
    changed_diagnostics = replace(diagnostics_report, orchestration_execution_enabled=True)
    report = audit_operational_lifecycle_integrity(
        changed_lifecycle,
        changed_drift,
        changed_governance,
        validation_report,
        production_consumption_report,
        recovery_report,
        changed_diagnostics,
    )

    assert report.orchestration_leakage_detected is True
    assert report.remediation_leakage_detected is True
    assert report.recommendation_leakage_detected is True
    assert report.ranking_leakage_detected is True
    assert report.scoring_leakage_detected is True
    assert report.selection_leakage_detected is True
    assert report.approval_leakage_detected is True
    assert report.authorization_leakage_detected is True
    assert report.mutation_leakage_detected is True
    assert report.production_consumption_leakage_detected is True
    assert report.integrity_status == INTEGRITY_STATUS_VIOLATION


def test_v4_0_integrity_audit_does_not_mutate_inputs():
    (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    ) = _representative_inputs()
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)
    governance_before = serialize_trusted_bundle_governance_report(governance_report)
    validation_before = serialize_operational_validation_report(validation_report)
    production_before = serialize_production_consumption_governance_report(production_consumption_report)
    recovery_before = serialize_recovery_certification_report(recovery_report)
    diagnostics_before = serialize_operational_diagnostics_report(diagnostics_report)

    audit_operational_lifecycle_integrity(*_representative_inputs())
    audit_operational_lifecycle_integrity(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )

    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before
    assert serialize_trusted_bundle_governance_report(governance_report) == governance_before
    assert serialize_operational_validation_report(validation_report) == validation_before
    assert serialize_production_consumption_governance_report(production_consumption_report) == production_before
    assert serialize_recovery_certification_report(recovery_report) == recovery_before
    assert serialize_operational_diagnostics_report(diagnostics_report) == diagnostics_before


def test_v4_0_integrity_hash_changes_when_diagnostics_hash_changes():
    inputs = _representative_inputs()
    baseline = audit_operational_lifecycle_integrity(*inputs)
    changed_diagnostics = replace(inputs[-1], deterministic_report_hash="changed_diagnostics_hash")
    changed = audit_operational_lifecycle_integrity(*inputs[:-1], changed_diagnostics)

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash
    assert baseline.diagnostics_report_hash != changed.diagnostics_report_hash


def test_v4_0_generated_integrity_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_operational_lifecycle_integrity_enforcement_report()
    integrity_report = report["operational_integrity_report"]

    assert report["foundation_status"] == V4_0_INTEGRITY_ENFORCEMENT_STATUS_STABLE
    assert report["integrity_mode"] == "descriptive_audit_only"
    assert report["finding_count"] == 21
    assert report["violation_count"] == 0
    assert report["prohibited_count"] == 1
    assert report["integrity_enforcement_performed_status"] is True
    assert report["deterministic_integrity_report_hash"] == integrity_report["deterministic_report_hash"]
    assert set(report["implemented_integrity_finding_types"]) == set(OPERATIONAL_INTEGRITY_FINDING_TYPES)
    assert all(value is False for value in report["leakage_booleans"].values())
    assert report["deterministic_guarantees"]["integrity_hash_stable"] is True
    assert report["deterministic_guarantees"]["all_leakage_booleans_false"] is True
    assert report["non_execution_guarantees"]["remediation_absent"] is True
    assert report["non_execution_guarantees"]["execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["recommendation_absent"] is True
    assert report["non_execution_guarantees"]["ranking_absent"] is True
    assert report["non_execution_guarantees"]["scoring_absent"] is True
    assert report["non_execution_guarantees"]["selection_absent"] is True
    assert "v4.0 Phase 8 does not remediate integrity findings." in report["explicit_limitations"]
