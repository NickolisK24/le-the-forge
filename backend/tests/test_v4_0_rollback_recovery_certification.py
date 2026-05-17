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
from operational_lifecycle.lifecycle_drift_serialization import serialize_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from operational_lifecycle.production_consumption_serialization import (  # noqa: E402
    serialize_production_consumption_governance_report,
)
from operational_lifecycle.recovery_certification_engine import (  # noqa: E402
    certify_rollback_recovery,
    evaluate_blocked_recovery_state,
    evaluate_bundle_governance_recovery_visibility,
    evaluate_critical_recovery_visibility,
    evaluate_drift_recovery_visibility,
    evaluate_lifecycle_recovery_visibility,
    evaluate_lineage_recovery_continuity,
    evaluate_operational_validation_recovery_visibility,
    evaluate_production_consumption_recovery_visibility,
    evaluate_prohibited_recovery_state,
    evaluate_provenance_recovery_continuity,
    evaluate_recovery_certification_readiness,
    evaluate_recovery_execution_prohibition,
    evaluate_recovery_warning_visibility,
    evaluate_replay_recovery_continuity,
    evaluate_rollback_execution_prohibition,
    evaluate_rollback_recovery_continuity,
    evaluate_unknown_recovery_state,
    evaluate_unsupported_recovery_state,
)
from operational_lifecycle.recovery_certification_hashing import hash_recovery_certification_report  # noqa: E402
from operational_lifecycle.recovery_certification_models import (  # noqa: E402
    RECOVERY_CERTIFICATION_FINDING_TYPES,
    RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
    RECOVERY_CERTIFICATION_SEVERITY_CRITICAL,
    RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
    RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN,
    RECOVERY_CERTIFICATION_SEVERITY_WARNING,
    RECOVERY_CERTIFICATION_STATE_PROHIBITED,
    RECOVERY_FINDING_BLOCKED_RECOVERY_STATE,
    RECOVERY_FINDING_BUNDLE_GOVERNANCE_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_CRITICAL_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_DRIFT_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_LIFECYCLE_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_LINEAGE_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_OPERATIONAL_VALIDATION_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_PRODUCTION_CONSUMPTION_RECOVERY_VISIBILITY,
    RECOVERY_FINDING_PROHIBITED_RECOVERY_STATE,
    RECOVERY_FINDING_PROVENANCE_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS,
    RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED,
    RECOVERY_FINDING_RECOVERY_WARNING_VISIBILITY,
    RECOVERY_FINDING_REPLAY_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED,
    RECOVERY_FINDING_ROLLBACK_RECOVERY_CONTINUITY,
    RECOVERY_FINDING_UNKNOWN_RECOVERY_STATE,
    RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE,
    V4_0_RECOVERY_CERTIFICATION_STATUS_STABLE,
)
from operational_lifecycle.recovery_certification_serialization import (  # noqa: E402
    export_recovery_certification_report,
    serialize_recovery_certification_report,
)
from operational_lifecycle.recovery_certification_visibility import (  # noqa: E402
    count_recovery_finding_types,
    count_recovery_severities,
    validate_recovery_certification_visibility,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    serialize_operational_validation_report,
)
from scripts.report_v4_0_rollback_recovery_certification import (  # noqa: E402
    build_representative_rollback_recovery_certification_inputs,
    build_v4_0_rollback_recovery_certification_report,
)


def _representative_report():
    lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report = (
        build_representative_rollback_recovery_certification_inputs()
    )
    return certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    )


def test_v4_0_recovery_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 18
    assert first.finding_count == len(first.findings)


def test_v4_0_recovery_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_recovery_certification_report(first) == serialize_recovery_certification_report(second)
    assert hash_recovery_certification_report(first) == hash_recovery_certification_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_recovery_certification_report(first)
    exported = json.loads(serialize_recovery_certification_report(first))
    assert exported["finding_count"] == 18
    assert exported["recovery_execution_authorized"] is False
    assert exported["rollback_execution_authorized"] is False
    assert all(finding["production_consumption_reference"] for finding in exported["findings"])
    assert all(finding["recovery_reference"] for finding in exported["findings"])
    assert all(finding["rollback_reference"] for finding in exported["findings"])


def test_v4_0_recovery_report_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_recovery_finding_types(report.findings)

    assert set(RECOVERY_CERTIFICATION_FINDING_TYPES) <= set(finding_type_counts)
    for finding_type in RECOVERY_CERTIFICATION_FINDING_TYPES:
        assert finding_type_counts[finding_type] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_recovery_visibility_functions_are_descriptive_only():
    lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report = (
        build_representative_rollback_recovery_certification_inputs()
    )
    findings = (
        evaluate_lifecycle_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_drift_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_bundle_governance_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_operational_validation_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_production_consumption_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_provenance_recovery_continuity(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_lineage_recovery_continuity(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_replay_recovery_continuity(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_rollback_recovery_continuity(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_unsupported_recovery_state(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_prohibited_recovery_state(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_blocked_recovery_state(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_unknown_recovery_state(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_recovery_warning_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_critical_recovery_visibility(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_recovery_certification_readiness(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_rollback_execution_prohibition(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
        evaluate_recovery_execution_prohibition(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
        ),
    )

    assert all(finding.descriptive_only for finding in findings)
    assert all(not finding.approval_enabled for finding in findings)
    assert all(not finding.authorization_enabled for finding in findings)
    assert all(not finding.remediation_enabled for finding in findings)
    assert all(not finding.recovery_execution_authorized for finding in findings)
    assert all(not finding.rollback_execution_authorized for finding in findings)
    assert all(not finding.execution_enabled for finding in findings)
    assert all(not finding.orchestration_execution_enabled for finding in findings)


def test_v4_0_recovery_evidence_layer_visibility_is_present():
    report = _representative_report()
    findings = {finding.finding_type: finding for finding in report.findings}

    assert findings[RECOVERY_FINDING_LIFECYCLE_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING
    assert findings[RECOVERY_FINDING_DRIFT_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_BUNDLE_GOVERNANCE_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_OPERATIONAL_VALIDATION_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_PRODUCTION_CONSUMPTION_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_PROVENANCE_RECOVERY_CONTINUITY].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING
    assert findings[RECOVERY_FINDING_LINEAGE_RECOVERY_CONTINUITY].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_REPLAY_RECOVERY_CONTINUITY].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING
    assert findings[RECOVERY_FINDING_ROLLBACK_RECOVERY_CONTINUITY].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING


def test_v4_0_recovery_exposes_fail_visible_states_and_counts():
    report = _representative_report()
    visibility = validate_recovery_certification_visibility(report)
    severity_counts = count_recovery_severities(report.findings)
    findings = {finding.finding_type: finding for finding in report.findings}

    assert visibility["valid"] is True
    assert report.certification_state == RECOVERY_CERTIFICATION_STATE_PROHIBITED
    assert report.certifiable_finding_count == 6
    assert report.blocked_count == 7
    assert report.unsupported_count == 1
    assert report.prohibited_count == 5
    assert report.unknown_count == 1
    assert report.warning_count == 6
    assert report.critical_count == 1
    assert severity_counts[RECOVERY_CERTIFICATION_SEVERITY_WARNING] == 6
    assert severity_counts[RECOVERY_CERTIFICATION_SEVERITY_BLOCKING] == 7
    assert severity_counts[RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED] == 3
    assert severity_counts[RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN] == 1
    assert severity_counts[RECOVERY_CERTIFICATION_SEVERITY_CRITICAL] == 1
    assert findings[RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING
    assert findings[RECOVERY_FINDING_PROHIBITED_RECOVERY_STATE].severity == RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED
    assert findings[RECOVERY_FINDING_BLOCKED_RECOVERY_STATE].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_UNKNOWN_RECOVERY_STATE].severity == RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN
    assert findings[RECOVERY_FINDING_RECOVERY_WARNING_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_WARNING
    assert findings[RECOVERY_FINDING_CRITICAL_RECOVERY_VISIBILITY].severity == RECOVERY_CERTIFICATION_SEVERITY_CRITICAL
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_recovery_certification_readiness_and_execution_prohibitions_are_visible():
    report = _representative_report()
    findings = {finding.finding_type: finding for finding in report.findings}

    assert findings[RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS].severity == RECOVERY_CERTIFICATION_SEVERITY_BLOCKING
    assert findings[RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED].severity == RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED
    assert findings[RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED].severity == RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED
    assert report.recovery_execution_authorized is False
    assert report.rollback_execution_authorized is False
    assert report.recovery_execution_enabled is False
    assert report.rollback_execution_enabled is False
    assert "recovery_execution_authorized remains false" in findings[RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED].explanation
    assert "rollback_execution_authorized remains false" in findings[RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED].explanation


def test_v4_0_recovery_certification_does_not_mutate_inputs():
    lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report = (
        build_representative_rollback_recovery_certification_inputs()
    )
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)
    governance_before = serialize_trusted_bundle_governance_report(governance_report)
    validation_before = serialize_operational_validation_report(validation_report)
    production_before = serialize_production_consumption_governance_report(production_consumption_report)

    certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    )
    certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    )

    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before
    assert serialize_trusted_bundle_governance_report(governance_report) == governance_before
    assert serialize_operational_validation_report(validation_report) == validation_before
    assert serialize_production_consumption_governance_report(production_consumption_report) == production_before


def test_v4_0_recovery_hash_changes_when_production_consumption_hash_changes():
    lifecycle_foundation, drift_report, governance_report, validation_report, production_consumption_report = (
        build_representative_rollback_recovery_certification_inputs()
    )
    baseline = certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
    )
    changed_production = replace(production_consumption_report, deterministic_report_hash="changed_production_hash")
    changed = certify_rollback_recovery(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        changed_production,
    )

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash
    assert baseline.production_consumption_report_hash != changed.production_consumption_report_hash


def test_v4_0_recovery_generated_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_rollback_recovery_certification_report()
    recovery_report = report["recovery_certification_report"]

    assert report["foundation_status"] == V4_0_RECOVERY_CERTIFICATION_STATUS_STABLE
    assert report["certification_mode"] == "descriptive_only"
    assert report["finding_count"] == 18
    assert report["certifiable_finding_count"] == 6
    assert report["blocked_count"] == 7
    assert report["unsupported_count"] == 1
    assert report["prohibited_count"] == 5
    assert report["unknown_count"] == 1
    assert report["warning_count"] == 6
    assert report["critical_count"] == 1
    assert report["recovery_execution_authorization_status"] is False
    assert report["rollback_execution_authorization_status"] is False
    assert report["deterministic_recovery_certification_report_hash"] == recovery_report["deterministic_report_hash"]
    assert set(report["implemented_recovery_certification_finding_types"]) == set(RECOVERY_CERTIFICATION_FINDING_TYPES)
    assert report["non_execution_guarantees"]["approval_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
    assert report["non_execution_guarantees"]["remediation_absent"] is True
    assert report["non_execution_guarantees"]["recovery_execution_authorized"] is False
    assert report["non_execution_guarantees"]["rollback_execution_authorized"] is False
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 6 does not execute recovery." in report["explicit_limitations"]
    assert "v4.0 Phase 6 does not execute rollback." in report["explicit_limitations"]


def test_v4_0_recovery_export_preserves_order_and_authorization_flags():
    report = _representative_report()
    exported = export_recovery_certification_report(report)

    assert exported["recovery_execution_authorized"] is False
    assert exported["rollback_execution_authorized"] is False
    assert exported["recovery_execution_enabled"] is False
    assert exported["rollback_execution_enabled"] is False
    assert [finding["deterministic_key"] for finding in exported["findings"]] == sorted(
        finding["deterministic_key"] for finding in exported["findings"]
    )
    assert any(
        finding["finding_type"] == RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED
        for finding in exported["findings"]
    )
    assert any(
        finding["finding_type"] == RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED
        for finding in exported["findings"]
    )
