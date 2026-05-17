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
from operational_lifecycle.continuity_certification_serialization import (  # noqa: E402
    serialize_operational_continuity_certification_report,
)
from operational_lifecycle.diagnostics_serialization import serialize_operational_diagnostics_report  # noqa: E402
from operational_lifecycle.integrity_enforcement_serialization import (  # noqa: E402
    serialize_operational_integrity_report,
)
from operational_lifecycle.lifecycle_drift_serialization import serialize_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from operational_lifecycle.production_consumption_serialization import (  # noqa: E402
    serialize_production_consumption_governance_report,
)
from operational_lifecycle.recovery_certification_serialization import (  # noqa: E402
    serialize_recovery_certification_report,
)
from operational_lifecycle.v4_closeout_audit import (  # noqa: E402
    audit_bundle_governance_closeout,
    audit_continuity_closeout,
    audit_diagnostics_closeout,
    audit_drift_closeout,
    audit_hashing_stability,
    audit_integrity_closeout,
    audit_lifecycle_closeout,
    audit_lineage_closeout,
    audit_non_authorization,
    audit_non_execution,
    audit_non_remediation,
    audit_orchestration_disabled,
    audit_planner_integration_disabled,
    audit_production_consumption_closeout,
    audit_production_consumption_disabled,
    audit_prohibited_state_visibility,
    audit_provenance_closeout,
    audit_recovery_closeout,
    audit_replay_closeout,
    audit_rollback_closeout,
    audit_serialization_stability,
    audit_unknown_state_visibility,
    audit_v4_1_readiness,
    audit_v4_closeout_and_v4_1_readiness,
    audit_validation_closeout,
    audit_visibility_preservation,
    audit_warning_visibility,
)
from operational_lifecycle.v4_closeout_hashing import hash_v4_closeout_report  # noqa: E402
from operational_lifecycle.v4_closeout_models import (  # noqa: E402
    CLOSEOUT_FINDING_BUNDLE_GOVERNANCE,
    CLOSEOUT_FINDING_CONTINUITY,
    CLOSEOUT_FINDING_DIAGNOSTICS,
    CLOSEOUT_FINDING_DRIFT,
    CLOSEOUT_FINDING_HASHING,
    CLOSEOUT_FINDING_INTEGRITY,
    CLOSEOUT_FINDING_LIFECYCLE,
    CLOSEOUT_FINDING_LINEAGE,
    CLOSEOUT_FINDING_NON_AUTHORIZATION,
    CLOSEOUT_FINDING_NON_EXECUTION,
    CLOSEOUT_FINDING_NON_REMEDIATION,
    CLOSEOUT_FINDING_ORCHESTRATION_DISABLED,
    CLOSEOUT_FINDING_PLANNER_DISABLED,
    CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION,
    CLOSEOUT_FINDING_PRODUCTION_DISABLED,
    CLOSEOUT_FINDING_PROHIBITED_VISIBILITY,
    CLOSEOUT_FINDING_PROVENANCE,
    CLOSEOUT_FINDING_RECOVERY,
    CLOSEOUT_FINDING_REPLAY,
    CLOSEOUT_FINDING_ROLLBACK,
    CLOSEOUT_FINDING_SERIALIZATION,
    CLOSEOUT_FINDING_UNKNOWN_VISIBILITY,
    CLOSEOUT_FINDING_V41_READINESS,
    CLOSEOUT_FINDING_VALIDATION,
    CLOSEOUT_FINDING_VISIBILITY,
    CLOSEOUT_FINDING_WARNING_VISIBILITY,
    CLOSEOUT_SEVERITY_CRITICAL,
    CLOSEOUT_SEVERITY_INFO,
    CLOSEOUT_SEVERITY_WARNING,
    CLOSEOUT_STATUS_BLOCKED,
    CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS,
    V41_READINESS_NOT_READY,
    V41_READINESS_READY_WITH_WARNINGS,
    V4_CLOSEOUT_FINDING_TYPES,
    V4_0_CLOSEOUT_STATUS_STABLE,
)
from operational_lifecycle.v4_closeout_serialization import serialize_v4_closeout_report  # noqa: E402
from operational_lifecycle.v4_closeout_visibility import (  # noqa: E402
    count_v4_closeout_finding_types,
    count_v4_closeout_severities,
    validate_v4_closeout_visibility,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    serialize_operational_validation_report,
)
from scripts.report_v4_0_closeout_and_v4_1_readiness import (  # noqa: E402
    build_representative_v4_closeout_inputs,
    build_v4_0_closeout_and_v4_1_readiness_report,
)


def _representative_inputs():
    return build_representative_v4_closeout_inputs()


def _representative_report():
    return audit_v4_closeout_and_v4_1_readiness(*_representative_inputs())


def test_v4_0_closeout_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 26
    assert first.finding_count == len(first.findings)


def test_v4_0_closeout_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_v4_closeout_report(first) == serialize_v4_closeout_report(second)
    assert hash_v4_closeout_report(first) == hash_v4_closeout_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_v4_closeout_report(first)
    exported = json.loads(serialize_v4_closeout_report(first))
    assert exported["finding_count"] == 26
    assert exported["execution_authorized"] is False
    assert exported["remediation_authorized"] is False
    assert exported["production_consumption_enabled"] is False
    assert exported["orchestration_enabled"] is False
    assert exported["planner_integration_enabled"] is False


def test_v4_0_closeout_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_v4_closeout_finding_types(report.findings)

    assert set(V4_CLOSEOUT_FINDING_TYPES) <= set(finding_type_counts)
    for finding_type in V4_CLOSEOUT_FINDING_TYPES:
        assert finding_type_counts[finding_type] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_closeout_certifies_phase_preservation():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            audit_lifecycle_closeout(*inputs),
            audit_drift_closeout(*inputs),
            audit_bundle_governance_closeout(*inputs),
            audit_validation_closeout(*inputs),
            audit_production_consumption_closeout(*inputs),
            audit_recovery_closeout(*inputs),
            audit_diagnostics_closeout(*inputs),
            audit_integrity_closeout(*inputs),
            audit_continuity_closeout(*inputs),
        )
    }

    assert findings[CLOSEOUT_FINDING_LIFECYCLE].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_DRIFT].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_BUNDLE_GOVERNANCE].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_VALIDATION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_RECOVERY].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_DIAGNOSTICS].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_INTEGRITY].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_CONTINUITY].severity == CLOSEOUT_SEVERITY_INFO


def test_v4_0_closeout_certifies_safety_and_stability_preservation():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            audit_provenance_closeout(*inputs),
            audit_lineage_closeout(*inputs),
            audit_replay_closeout(*inputs),
            audit_rollback_closeout(*inputs),
            audit_serialization_stability(*inputs),
            audit_hashing_stability(*inputs),
            audit_visibility_preservation(*inputs),
        )
    }

    assert findings[CLOSEOUT_FINDING_PROVENANCE].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_LINEAGE].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_REPLAY].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_ROLLBACK].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_SERIALIZATION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_HASHING].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_VISIBILITY].severity == CLOSEOUT_SEVERITY_INFO


def test_v4_0_closeout_certifies_disabled_operational_boundaries():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            audit_non_execution(*inputs),
            audit_non_remediation(*inputs),
            audit_non_authorization(*inputs),
            audit_production_consumption_disabled(*inputs),
            audit_orchestration_disabled(*inputs),
            audit_planner_integration_disabled(*inputs),
        )
    }
    report = _representative_report()

    assert findings[CLOSEOUT_FINDING_NON_EXECUTION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_NON_REMEDIATION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_NON_AUTHORIZATION].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_PRODUCTION_DISABLED].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_ORCHESTRATION_DISABLED].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_PLANNER_DISABLED].severity == CLOSEOUT_SEVERITY_INFO
    assert report.execution_authorized is False
    assert report.remediation_authorized is False
    assert report.production_consumption_enabled is False
    assert report.orchestration_enabled is False
    assert report.planner_integration_enabled is False


def test_v4_0_closeout_exposes_v4_1_readiness_and_visibility_findings():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            audit_v4_1_readiness(*inputs),
            audit_prohibited_state_visibility(*inputs),
            audit_unknown_state_visibility(*inputs),
            audit_warning_visibility(*inputs),
        )
    }
    report = _representative_report()
    severity_counts = count_v4_closeout_severities(report.findings)

    assert findings[CLOSEOUT_FINDING_V41_READINESS].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_PROHIBITED_VISIBILITY].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_UNKNOWN_VISIBILITY].severity == CLOSEOUT_SEVERITY_INFO
    assert findings[CLOSEOUT_FINDING_WARNING_VISIBILITY].severity == CLOSEOUT_SEVERITY_WARNING
    assert report.closeout_status == CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS
    assert report.v4_1_readiness_status == V41_READINESS_READY_WITH_WARNINGS
    assert report.warning_count == 1
    assert report.blocked_count == 0
    assert report.prohibited_count == 0
    assert report.unknown_count == 0
    assert report.critical_count == 0
    assert severity_counts[CLOSEOUT_SEVERITY_WARNING] == 1


def test_v4_0_closeout_detects_broken_hashing_without_repair():
    inputs = _representative_inputs()
    changed_continuity = replace(inputs[-1], deterministic_report_hash="changed_continuity_hash")
    changed = audit_v4_closeout_and_v4_1_readiness(*inputs[:-1], changed_continuity)
    findings = {finding.finding_type: finding for finding in changed.findings}

    assert changed.closeout_status == CLOSEOUT_STATUS_BLOCKED
    assert changed.v4_1_readiness_status == V41_READINESS_NOT_READY
    assert changed.hashing_stable is False
    assert findings[CLOSEOUT_FINDING_HASHING].severity == CLOSEOUT_SEVERITY_CRITICAL
    assert changed.execution_authorized is False
    assert changed.remediation_authorized is False


def test_v4_0_closeout_detects_execution_orchestration_and_planner_leakage_without_enabling_them():
    inputs = _representative_inputs()
    changed_validation = replace(inputs[3], execution_enabled=True)
    changed_production = replace(inputs[4], orchestration_execution_enabled=True)
    changed_integrity = replace(inputs[7], planner_integration_leakage_detected=True)
    changed = audit_v4_closeout_and_v4_1_readiness(
        inputs[0],
        inputs[1],
        inputs[2],
        changed_validation,
        changed_production,
        inputs[5],
        inputs[6],
        changed_integrity,
        inputs[8],
    )
    findings = {finding.finding_type: finding for finding in changed.findings}

    assert changed.closeout_status == CLOSEOUT_STATUS_BLOCKED
    assert findings[CLOSEOUT_FINDING_NON_EXECUTION].severity == CLOSEOUT_SEVERITY_CRITICAL
    assert findings[CLOSEOUT_FINDING_ORCHESTRATION_DISABLED].severity == CLOSEOUT_SEVERITY_CRITICAL
    assert findings[CLOSEOUT_FINDING_PLANNER_DISABLED].severity == CLOSEOUT_SEVERITY_CRITICAL
    assert changed.execution_authorized is False
    assert changed.orchestration_enabled is False
    assert changed.planner_integration_enabled is False


def test_v4_0_closeout_does_not_mutate_source_reports():
    inputs = _representative_inputs()
    lifecycle_before = serialize_patch_lifecycle_foundation(inputs[0])
    drift_before = serialize_lifecycle_drift_report(inputs[1])
    governance_before = serialize_trusted_bundle_governance_report(inputs[2])
    validation_before = serialize_operational_validation_report(inputs[3])
    production_before = serialize_production_consumption_governance_report(inputs[4])
    recovery_before = serialize_recovery_certification_report(inputs[5])
    diagnostics_before = serialize_operational_diagnostics_report(inputs[6])
    integrity_before = serialize_operational_integrity_report(inputs[7])
    continuity_before = serialize_operational_continuity_certification_report(inputs[8])

    audit_v4_closeout_and_v4_1_readiness(*_representative_inputs())
    audit_v4_closeout_and_v4_1_readiness(*inputs)

    assert serialize_patch_lifecycle_foundation(inputs[0]) == lifecycle_before
    assert serialize_lifecycle_drift_report(inputs[1]) == drift_before
    assert serialize_trusted_bundle_governance_report(inputs[2]) == governance_before
    assert serialize_operational_validation_report(inputs[3]) == validation_before
    assert serialize_production_consumption_governance_report(inputs[4]) == production_before
    assert serialize_recovery_certification_report(inputs[5]) == recovery_before
    assert serialize_operational_diagnostics_report(inputs[6]) == diagnostics_before
    assert serialize_operational_integrity_report(inputs[7]) == integrity_before
    assert serialize_operational_continuity_certification_report(inputs[8]) == continuity_before


def test_v4_0_generated_closeout_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_closeout_and_v4_1_readiness_report()
    closeout_report = report["v4_closeout_report"]
    visibility = validate_v4_closeout_visibility(_representative_report())

    assert report["foundation_status"] == V4_0_CLOSEOUT_STATUS_STABLE
    assert report["closeout_mode"] == "descriptive_closeout_only"
    assert report["closeout_status"] == CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS
    assert report["v4_1_readiness_status"] == V41_READINESS_READY_WITH_WARNINGS
    assert report["finding_count"] == 26
    assert report["warning_count"] == 1
    assert report["deterministic_closeout_report_hash"] == closeout_report["deterministic_report_hash"]
    assert set(report["implemented_closeout_finding_types"]) == set(V4_CLOSEOUT_FINDING_TYPES)
    assert report["deterministic_guarantees"]["closeout_hash_stable"] is True
    assert report["deterministic_guarantees"]["serialization_stable"] is True
    assert report["deterministic_guarantees"]["hashing_stable"] is True
    assert report["deterministic_guarantees"]["visibility_preserved"] is True
    assert report["deterministic_guarantees"]["integrity_preserved"] is True
    assert report["deterministic_guarantees"]["continuity_preserved"] is True
    assert report["non_execution_guarantees"]["execution_authorization_absent"] is True
    assert report["non_execution_guarantees"]["remediation_authorization_absent"] is True
    assert report["non_execution_guarantees"]["production_consumption_disabled"] is True
    assert report["non_execution_guarantees"]["orchestration_disabled"] is True
    assert report["non_execution_guarantees"]["planner_integration_disabled"] is True
    assert visibility["valid"] is True
