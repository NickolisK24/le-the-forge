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
from operational_lifecycle.continuity_certification_engine import (  # noqa: E402
    certify_bundle_governance_continuity,
    certify_diagnostics_continuity,
    certify_drift_continuity,
    certify_hashing_continuity,
    certify_integrity_continuity,
    certify_lifecycle_continuity,
    certify_lineage_continuity,
    certify_non_authorization_continuity,
    certify_non_execution_continuity,
    certify_non_remediation_continuity,
    certify_operational_lifecycle_continuity,
    certify_operational_validation_continuity,
    certify_production_consumption_continuity,
    certify_production_consumption_disabled_continuity,
    certify_prohibited_state_continuity,
    certify_provenance_continuity,
    certify_recovery_continuity,
    certify_replay_continuity,
    certify_rollback_continuity,
    certify_serialization_continuity,
    certify_unknown_state_continuity,
    certify_visibility_continuity,
)
from operational_lifecycle.continuity_certification_hashing import (  # noqa: E402
    hash_operational_continuity_certification_report,
)
from operational_lifecycle.continuity_certification_models import (  # noqa: E402
    CONTINUITY_FINDING_BUNDLE_GOVERNANCE,
    CONTINUITY_FINDING_DIAGNOSTICS,
    CONTINUITY_FINDING_DRIFT,
    CONTINUITY_FINDING_HASHING,
    CONTINUITY_FINDING_INTEGRITY,
    CONTINUITY_FINDING_LIFECYCLE,
    CONTINUITY_FINDING_LINEAGE,
    CONTINUITY_FINDING_NON_AUTHORIZATION,
    CONTINUITY_FINDING_NON_EXECUTION,
    CONTINUITY_FINDING_NON_REMEDIATION,
    CONTINUITY_FINDING_OPERATIONAL_VALIDATION,
    CONTINUITY_FINDING_PRODUCTION_CONSUMPTION,
    CONTINUITY_FINDING_PRODUCTION_DISABLED,
    CONTINUITY_FINDING_PROHIBITED_STATE,
    CONTINUITY_FINDING_PROVENANCE,
    CONTINUITY_FINDING_RECOVERY,
    CONTINUITY_FINDING_REPLAY,
    CONTINUITY_FINDING_ROLLBACK,
    CONTINUITY_FINDING_SERIALIZATION,
    CONTINUITY_FINDING_UNKNOWN_STATE,
    CONTINUITY_FINDING_VISIBILITY,
    CONTINUITY_SEVERITY_CRITICAL,
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_PROHIBITED,
    CONTINUITY_SEVERITY_UNKNOWN,
    CONTINUITY_STATUS_BROKEN,
    CONTINUITY_STATUS_PROHIBITED,
    OPERATIONAL_CONTINUITY_FINDING_TYPES,
    V4_0_CONTINUITY_CERTIFICATION_STATUS_STABLE,
)
from operational_lifecycle.continuity_certification_serialization import (  # noqa: E402
    serialize_operational_continuity_certification_report,
)
from operational_lifecycle.continuity_certification_visibility import (  # noqa: E402
    count_continuity_finding_types,
    count_continuity_severities,
    validate_operational_continuity_visibility,
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
from operational_lifecycle.validation_automation_serialization import (  # noqa: E402
    serialize_operational_validation_report,
)
from scripts.report_v4_0_operational_lifecycle_continuity_certification import (  # noqa: E402
    build_representative_operational_continuity_inputs,
    build_v4_0_operational_lifecycle_continuity_certification_report,
)


def _representative_inputs():
    return build_representative_operational_continuity_inputs()


def _representative_report():
    return certify_operational_lifecycle_continuity(*_representative_inputs())


def test_v4_0_continuity_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 21
    assert first.finding_count == len(first.findings)


def test_v4_0_continuity_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_operational_continuity_certification_report(first) == (
        serialize_operational_continuity_certification_report(second)
    )
    assert hash_operational_continuity_certification_report(first) == (
        hash_operational_continuity_certification_report(second)
    )
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_operational_continuity_certification_report(first)
    exported = json.loads(serialize_operational_continuity_certification_report(first))
    assert exported["finding_count"] == 21
    assert exported["execution_authorized"] is False
    assert exported["remediation_authorized"] is False
    assert exported["production_consumption_enabled"] is False
    assert all(finding["integrity_reference"] for finding in exported["findings"])


def test_v4_0_continuity_report_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_continuity_finding_types(report.findings)

    assert set(OPERATIONAL_CONTINUITY_FINDING_TYPES) <= set(finding_type_counts)
    for finding_type in OPERATIONAL_CONTINUITY_FINDING_TYPES:
        assert finding_type_counts[finding_type] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_continuity_certifies_all_phase_evidence_layers():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            certify_lifecycle_continuity(*inputs),
            certify_drift_continuity(*inputs),
            certify_bundle_governance_continuity(*inputs),
            certify_operational_validation_continuity(*inputs),
            certify_production_consumption_continuity(*inputs),
            certify_recovery_continuity(*inputs),
            certify_diagnostics_continuity(*inputs),
            certify_integrity_continuity(*inputs),
        )
    }

    assert findings[CONTINUITY_FINDING_LIFECYCLE].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_DRIFT].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_BUNDLE_GOVERNANCE].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_OPERATIONAL_VALIDATION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_PRODUCTION_CONSUMPTION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_RECOVERY].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_DIAGNOSTICS].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_INTEGRITY].severity == CONTINUITY_SEVERITY_INFO


def test_v4_0_continuity_certifies_provenance_lineage_replay_and_rollback():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            certify_provenance_continuity(*inputs),
            certify_lineage_continuity(*inputs),
            certify_replay_continuity(*inputs),
            certify_rollback_continuity(*inputs),
        )
    }

    assert findings[CONTINUITY_FINDING_PROVENANCE].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_LINEAGE].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_REPLAY].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_ROLLBACK].severity == CONTINUITY_SEVERITY_INFO


def test_v4_0_continuity_certifies_serialization_hashing_and_visibility():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            certify_serialization_continuity(*inputs),
            certify_hashing_continuity(*inputs),
            certify_visibility_continuity(*inputs),
        )
    }

    assert findings[CONTINUITY_FINDING_SERIALIZATION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_HASHING].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_VISIBILITY].severity == CONTINUITY_SEVERITY_INFO


def test_v4_0_continuity_preserves_non_execution_non_remediation_and_non_authorization():
    inputs = _representative_inputs()
    findings = {
        finding.finding_type: finding
        for finding in (
            certify_non_execution_continuity(*inputs),
            certify_non_remediation_continuity(*inputs),
            certify_non_authorization_continuity(*inputs),
            certify_production_consumption_disabled_continuity(*inputs),
        )
    }
    report = _representative_report()

    assert findings[CONTINUITY_FINDING_NON_EXECUTION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_NON_REMEDIATION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_NON_AUTHORIZATION].severity == CONTINUITY_SEVERITY_INFO
    assert findings[CONTINUITY_FINDING_PRODUCTION_DISABLED].severity == CONTINUITY_SEVERITY_INFO
    assert report.execution_authorized is False
    assert report.remediation_authorized is False
    assert report.production_consumption_enabled is False
    assert report.recommendation_enabled is False
    assert report.ranking_enabled is False
    assert report.scoring_enabled is False
    assert report.selection_enabled is False


def test_v4_0_continuity_exposes_prohibited_and_unknown_state_visibility():
    inputs = _representative_inputs()
    prohibited = certify_prohibited_state_continuity(*inputs)
    unknown = certify_unknown_state_continuity(*inputs)
    report = _representative_report()
    severity_counts = count_continuity_severities(report.findings)

    assert prohibited.severity == CONTINUITY_SEVERITY_PROHIBITED
    assert unknown.severity == CONTINUITY_SEVERITY_UNKNOWN
    assert report.continuity_status == CONTINUITY_STATUS_PROHIBITED
    assert report.prohibited_count == 1
    assert report.unknown_count == 1
    assert severity_counts[CONTINUITY_SEVERITY_PROHIBITED] == 1
    assert severity_counts[CONTINUITY_SEVERITY_UNKNOWN] == 1


def test_v4_0_continuity_detects_broken_hashing_without_repair():
    inputs = _representative_inputs()
    changed_integrity = replace(inputs[-1], deterministic_report_hash="changed_integrity_hash")
    changed = certify_operational_lifecycle_continuity(*inputs[:-1], changed_integrity)
    findings = {finding.finding_type: finding for finding in changed.findings}

    assert changed.continuity_status == CONTINUITY_STATUS_BROKEN
    assert changed.broken_count == 1
    assert changed.critical_count == 1
    assert changed.hashing_stable is False
    assert findings[CONTINUITY_FINDING_HASHING].severity == CONTINUITY_SEVERITY_CRITICAL
    assert changed.execution_authorized is False
    assert changed.remediation_authorized is False


def test_v4_0_continuity_detects_execution_leakage_without_authorization():
    inputs = _representative_inputs()
    changed_validation = replace(inputs[3], execution_enabled=True)
    changed = certify_operational_lifecycle_continuity(
        inputs[0],
        inputs[1],
        inputs[2],
        changed_validation,
        inputs[4],
        inputs[5],
        inputs[6],
        inputs[7],
    )
    findings = {finding.finding_type: finding for finding in changed.findings}

    assert changed.continuity_status == CONTINUITY_STATUS_BROKEN
    assert findings[CONTINUITY_FINDING_NON_EXECUTION].severity == CONTINUITY_SEVERITY_CRITICAL
    assert changed.execution_authorized is False
    assert changed.production_consumption_enabled is False


def test_v4_0_continuity_certification_does_not_mutate_inputs():
    inputs = _representative_inputs()
    lifecycle_before = serialize_patch_lifecycle_foundation(inputs[0])
    drift_before = serialize_lifecycle_drift_report(inputs[1])
    governance_before = serialize_trusted_bundle_governance_report(inputs[2])
    validation_before = serialize_operational_validation_report(inputs[3])
    production_before = serialize_production_consumption_governance_report(inputs[4])
    recovery_before = serialize_recovery_certification_report(inputs[5])
    diagnostics_before = serialize_operational_diagnostics_report(inputs[6])
    integrity_before = serialize_operational_integrity_report(inputs[7])

    certify_operational_lifecycle_continuity(*_representative_inputs())
    certify_operational_lifecycle_continuity(*inputs)

    assert serialize_patch_lifecycle_foundation(inputs[0]) == lifecycle_before
    assert serialize_lifecycle_drift_report(inputs[1]) == drift_before
    assert serialize_trusted_bundle_governance_report(inputs[2]) == governance_before
    assert serialize_operational_validation_report(inputs[3]) == validation_before
    assert serialize_production_consumption_governance_report(inputs[4]) == production_before
    assert serialize_recovery_certification_report(inputs[5]) == recovery_before
    assert serialize_operational_diagnostics_report(inputs[6]) == diagnostics_before
    assert serialize_operational_integrity_report(inputs[7]) == integrity_before


def test_v4_0_generated_continuity_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_operational_lifecycle_continuity_certification_report()
    continuity_report = report["operational_continuity_certification_report"]
    visibility = validate_operational_continuity_visibility(_representative_report())

    assert report["foundation_status"] == V4_0_CONTINUITY_CERTIFICATION_STATUS_STABLE
    assert report["certification_mode"] == "descriptive_certification_only"
    assert report["finding_count"] == 21
    assert report["prohibited_count"] == 1
    assert report["unknown_count"] == 1
    assert report["deterministic_continuity_report_hash"] == continuity_report["deterministic_report_hash"]
    assert set(report["implemented_continuity_finding_types"]) == set(OPERATIONAL_CONTINUITY_FINDING_TYPES)
    assert report["deterministic_guarantees"]["continuity_hash_stable"] is True
    assert report["deterministic_guarantees"]["serialization_stable"] is True
    assert report["deterministic_guarantees"]["hashing_stable"] is True
    assert report["deterministic_guarantees"]["visibility_preserved"] is True
    assert report["deterministic_guarantees"]["integrity_preserved"] is True
    assert report["non_execution_guarantees"]["execution_authorization_absent"] is True
    assert report["non_execution_guarantees"]["remediation_authorization_absent"] is True
    assert report["non_execution_guarantees"]["production_consumption_disabled"] is True
    assert visibility["valid"] is True
