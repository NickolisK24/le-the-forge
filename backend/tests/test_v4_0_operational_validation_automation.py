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
from operational_lifecycle.validation_automation_engine import (  # noqa: E402
    build_operational_validation_report,
    evaluate_blocked_validation_visibility,
    evaluate_critical_validation_visibility,
    evaluate_drift_validation_visibility,
    evaluate_governance_validation_visibility,
    evaluate_lifecycle_validation_visibility,
    evaluate_lineage_validation_visibility,
    evaluate_operational_certification_readiness,
    evaluate_operational_execution_prohibition,
    evaluate_prohibited_validation_visibility,
    evaluate_provenance_validation_visibility,
    evaluate_replay_validation_visibility,
    evaluate_rollback_validation_visibility,
    evaluate_unknown_validation_state,
    evaluate_unsupported_validation_visibility,
    evaluate_validation_warning_visibility,
)
from operational_lifecycle.validation_automation_hashing import hash_operational_validation_report  # noqa: E402
from operational_lifecycle.validation_automation_models import (  # noqa: E402
    OPERATIONAL_VALIDATION_FINDING_TYPES,
    OPERATIONAL_VALIDATION_SEVERITY_BLOCKING,
    OPERATIONAL_VALIDATION_SEVERITY_CRITICAL,
    OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED,
    OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN,
    OPERATIONAL_VALIDATION_SEVERITY_WARNING,
    OPERATIONAL_VALIDATION_STATE_PROHIBITED,
    VALIDATION_FINDING_BLOCKED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_CRITICAL_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS,
    VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED,
    VALIDATION_FINDING_PROHIBITED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_UNKNOWN_VALIDATION_STATE,
    VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY,
    VALIDATION_FINDING_VALIDATION_WARNING_VISIBILITY,
    V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_STABLE,
)
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    export_operational_validation_report,
    serialize_operational_validation_report,
)
from operational_lifecycle.validation_automation_visibility import (  # noqa: E402
    count_validation_finding_types,
    count_validation_severities,
    validate_operational_validation_visibility,
)
from scripts.report_v4_0_operational_validation_automation import (  # noqa: E402
    build_representative_operational_validation_inputs,
    build_v4_0_operational_validation_automation_report,
)


def _representative_report():
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    return build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)


def test_v4_0_validation_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 15
    assert first.finding_count == len(first.findings)


def test_v4_0_validation_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_operational_validation_report(first) == serialize_operational_validation_report(second)
    assert hash_operational_validation_report(first) == hash_operational_validation_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_operational_validation_report(first)
    exported = json.loads(serialize_operational_validation_report(first))
    assert exported["finding_count"] == 15
    assert exported["operational_execution_authorized"] is False
    assert all(finding["lifecycle_reference"] for finding in exported["findings"])
    assert all(finding["drift_reference"] for finding in exported["findings"])
    assert all(finding["governance_reference"] for finding in exported["findings"])
    assert all(finding["provenance_reference"] for finding in exported["findings"])
    assert all(finding["lineage_reference"] for finding in exported["findings"])
    assert all(finding["replay_reference"] for finding in exported["findings"])
    assert all(finding["rollback_reference"] for finding in exported["findings"])


def test_v4_0_validation_report_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_validation_finding_types(report.findings)

    assert set(OPERATIONAL_VALIDATION_FINDING_TYPES) <= set(finding_type_counts)
    assert finding_type_counts[VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_PROHIBITED_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_BLOCKED_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_VALIDATION_WARNING_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_CRITICAL_VALIDATION_VISIBILITY] == 1
    assert finding_type_counts[VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED] == 1
    assert finding_type_counts[VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS] == 1
    assert finding_type_counts[VALIDATION_FINDING_UNKNOWN_VALIDATION_STATE] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_validation_visibility_functions_are_descriptive_only():
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    findings = (
        evaluate_lifecycle_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_drift_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_governance_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_provenance_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_lineage_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_replay_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_rollback_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_unsupported_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_prohibited_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_blocked_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_validation_warning_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_critical_validation_visibility(lifecycle_foundation, drift_report, governance_report),
        evaluate_operational_execution_prohibition(lifecycle_foundation, drift_report, governance_report),
        evaluate_operational_certification_readiness(lifecycle_foundation, drift_report, governance_report),
        evaluate_unknown_validation_state(lifecycle_foundation, drift_report, governance_report),
    )

    assert all(finding.descriptive_only for finding in findings)
    assert all(not finding.authorization_enabled for finding in findings)
    assert all(not finding.approval_enabled for finding in findings)
    assert all(not finding.deployment_enabled for finding in findings)
    assert all(not finding.remediation_enabled for finding in findings)
    assert all(not finding.execution_enabled for finding in findings)
    assert all(not finding.orchestration_execution_enabled for finding in findings)
    assert all(not finding.runtime_mutation_enabled for finding in findings)


def test_v4_0_validation_exposes_continuity_and_fail_visible_states():
    report = _representative_report()
    visibility = validate_operational_validation_visibility(report)
    severity_counts = count_validation_severities(report.findings)
    findings = {finding.finding_type: finding for finding in report.findings}

    assert visibility["valid"] is True
    assert report.validation_state == OPERATIONAL_VALIDATION_STATE_PROHIBITED
    assert report.unsupported_count > 0
    assert report.prohibited_count > 0
    assert report.blocked_count > 0
    assert report.unknown_count > 0
    assert report.warning_count > 0
    assert report.critical_count > 0
    assert severity_counts[OPERATIONAL_VALIDATION_SEVERITY_WARNING] > 0
    assert severity_counts[OPERATIONAL_VALIDATION_SEVERITY_BLOCKING] > 0
    assert severity_counts[OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED] > 0
    assert severity_counts[OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN] > 0
    assert severity_counts[OPERATIONAL_VALIDATION_SEVERITY_CRITICAL] > 0
    assert findings[VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY].severity == OPERATIONAL_VALIDATION_SEVERITY_WARNING
    assert findings[VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY].severity == OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
    assert findings[VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY].severity == OPERATIONAL_VALIDATION_SEVERITY_WARNING
    assert findings[VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY].severity == OPERATIONAL_VALIDATION_SEVERITY_WARNING
    assert visibility["capability_enabled_count"] == 0


def test_v4_0_validation_prohibits_operational_execution():
    report = _representative_report()
    findings = [
        finding
        for finding in report.findings
        if finding.finding_type == VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED
    ]

    assert report.operational_execution_authorized is False
    assert report.production_consumption_authorized is False
    assert report.execution_enabled is False
    assert report.orchestration_execution_enabled is False
    assert len(findings) == 1
    assert findings[0].severity == OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED
    assert "operational_execution_authorized remains false" in findings[0].explanation


def test_v4_0_validation_does_not_mutate_lifecycle_drift_or_governance_records():
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)
    governance_before = serialize_trusted_bundle_governance_report(governance_report)

    build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)
    build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)

    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before
    assert serialize_trusted_bundle_governance_report(governance_report) == governance_before


def test_v4_0_validation_hash_changes_when_governance_hash_changes():
    lifecycle_foundation, drift_report, governance_report = build_representative_operational_validation_inputs()
    baseline = build_operational_validation_report(lifecycle_foundation, drift_report, governance_report)
    changed_governance = replace(governance_report, deterministic_report_hash="changed_governance_hash")
    changed = build_operational_validation_report(lifecycle_foundation, drift_report, changed_governance)

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash
    assert baseline.governance_report_hash != changed.governance_report_hash


def test_v4_0_validation_generated_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_operational_validation_automation_report()
    validation_report = report["validation_report"]

    assert report["foundation_status"] == V4_0_OPERATIONAL_VALIDATION_AUTOMATION_STATUS_STABLE
    assert report["validation_mode"] == "descriptive_only"
    assert report["total_findings"] == 15
    assert report["unsupported_count"] > 0
    assert report["prohibited_count"] > 0
    assert report["blocked_count"] > 0
    assert report["unknown_count"] > 0
    assert report["warning_count"] > 0
    assert report["critical_count"] > 0
    assert report["operational_execution_authorization_status"] is False
    assert report["operational_certification_readiness_visibility"] is True
    assert report["deterministic_validation_report_hash"] == validation_report["deterministic_report_hash"]
    assert set(report["implemented_validation_finding_types"]) == set(OPERATIONAL_VALIDATION_FINDING_TYPES)
    assert report["non_execution_guarantees"]["approval_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
    assert report["non_execution_guarantees"]["execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["operational_execution_authorized"] is False
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 4 does not authorize operational execution." in report["explicit_limitations"]


def test_v4_0_validation_export_preserves_order_and_operational_execution_prohibition():
    report = _representative_report()
    exported = export_operational_validation_report(report)

    assert exported["operational_execution_authorized"] is False
    assert exported["production_consumption_authorized"] is False
    assert [finding["deterministic_key"] for finding in exported["findings"]] == sorted(
        finding["deterministic_key"] for finding in exported["findings"]
    )
    assert any(
        finding["finding_type"] == VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED
        for finding in exported["findings"]
    )
