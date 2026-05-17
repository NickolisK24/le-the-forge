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

from operational_lifecycle.bundle_governance_audit import (  # noqa: E402
    audit_trusted_bundle_lifecycle_governance,
    evaluate_support_status_visibility,
    evaluate_trust_status_visibility,
    evaluate_validation_status_visibility,
)
from operational_lifecycle.bundle_governance_hashing import hash_trusted_bundle_governance_report  # noqa: E402
from operational_lifecycle.bundle_governance_models import (  # noqa: E402
    BUNDLE_SUPPORT_STATUS_PROHIBITED,
    BUNDLE_TRUST_STATUS_UNTRUSTED,
    BUNDLE_VALIDATION_STATUS_INVALID,
    GOVERNANCE_FINDING_BLOCKED_DOMAIN_VISIBILITY,
    GOVERNANCE_FINDING_BUNDLE_IDENTITY_VISIBILITY,
    GOVERNANCE_FINDING_BUNDLE_METADATA_VISIBILITY,
    GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY,
    GOVERNANCE_FINDING_INTEGRITY_WARNING_VISIBILITY,
    GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY,
    GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED,
    GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY,
    GOVERNANCE_FINDING_SUPPORT_STATUS_VISIBILITY,
    GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY,
    GOVERNANCE_FINDING_UNKNOWN_GOVERNANCE_STATE,
    GOVERNANCE_FINDING_VALIDATION_STATUS_VISIBILITY,
    GOVERNANCE_SEVERITY_BLOCKING,
    GOVERNANCE_SEVERITY_PROHIBITED,
    GOVERNANCE_SEVERITY_WARNING,
    TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES,
    V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_STABLE,
    TrustedBundleStatus,
    TrustedBundleSupportStatus,
    TrustedBundleValidationStatus,
)
from operational_lifecycle.bundle_governance_serialization import (  # noqa: E402
    export_trusted_bundle_governance_report,
    export_trusted_bundle_identity,
    serialize_trusted_bundle_governance_report,
)
from operational_lifecycle.bundle_governance_visibility import (  # noqa: E402
    count_governance_finding_types,
    count_governance_severities,
    validate_trusted_bundle_governance_visibility,
)
from operational_lifecycle.lifecycle_drift_serialization import serialize_lifecycle_drift_report  # noqa: E402
from operational_lifecycle.lifecycle_identity import lifecycle_identity_key  # noqa: E402
from operational_lifecycle.lifecycle_serialization import serialize_patch_lifecycle_foundation  # noqa: E402
from scripts.report_v4_0_trusted_bundle_lifecycle_governance import (  # noqa: E402
    build_representative_trusted_bundle_governance_inputs,
    build_v4_0_trusted_bundle_lifecycle_governance_report,
)


def _representative_report():
    args = build_representative_trusted_bundle_governance_inputs()
    return audit_trusted_bundle_lifecycle_governance(
        bundle_identity=args[0],
        trust_status=args[1],
        validation_status=args[2],
        support_status=args[3],
        blocked_domains=args[4],
        lifecycle_foundation=args[5],
        drift_report=args[6],
    )


def test_v4_0_governance_finding_ordering_is_deterministic():
    first = _representative_report()
    second = _representative_report()
    first_keys = [finding.deterministic_key for finding in first.findings]
    second_keys = [finding.deterministic_key for finding in second.findings]

    assert first_keys == sorted(first_keys)
    assert first_keys == second_keys
    assert first.finding_count == 18
    assert first.finding_count == len(first.findings)


def test_v4_0_governance_report_serialization_and_hashing_are_stable():
    first = _representative_report()
    second = _representative_report()

    assert serialize_trusted_bundle_governance_report(first) == serialize_trusted_bundle_governance_report(second)
    assert hash_trusted_bundle_governance_report(first) == hash_trusted_bundle_governance_report(second)
    assert first.deterministic_report_hash == second.deterministic_report_hash
    assert first.deterministic_report_hash == hash_trusted_bundle_governance_report(first)
    exported = json.loads(serialize_trusted_bundle_governance_report(first))
    assert exported["finding_count"] == 18
    assert exported["production_consumption_authorized"] is False
    assert all(finding["provenance_reference"] for finding in exported["findings"])
    assert all(finding["lineage_reference"] for finding in exported["findings"])


def test_v4_0_governance_report_contains_all_required_finding_types():
    report = _representative_report()
    finding_type_counts = count_governance_finding_types(report.findings)

    assert set(TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES) <= set(finding_type_counts)
    assert finding_type_counts[GOVERNANCE_FINDING_BUNDLE_IDENTITY_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_BUNDLE_METADATA_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_VALIDATION_STATUS_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_SUPPORT_STATUS_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_BLOCKED_DOMAIN_VISIBILITY] == 4
    assert finding_type_counts[GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_INTEGRITY_WARNING_VISIBILITY] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED] == 1
    assert finding_type_counts[GOVERNANCE_FINDING_UNKNOWN_GOVERNANCE_STATE] == 1
    assert finding_type_counts["invalid"] == 0


def test_v4_0_governance_status_visibility_is_descriptive_only():
    args = build_representative_trusted_bundle_governance_inputs()
    bundle_identity, _, _, _, _, lifecycle_foundation, drift_report = args
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    untrusted = TrustedBundleStatus(
        status=BUNDLE_TRUST_STATUS_UNTRUSTED,
        status_reference="test_untrusted",
        explanation="untrusted test state",
    )
    invalid = TrustedBundleValidationStatus(
        status=BUNDLE_VALIDATION_STATUS_INVALID,
        status_reference="test_invalid",
        explanation="invalid test state",
    )
    prohibited = TrustedBundleSupportStatus(
        status=BUNDLE_SUPPORT_STATUS_PROHIBITED,
        status_reference="test_prohibited",
        explanation="prohibited test state",
    )

    trust_finding = evaluate_trust_status_visibility(bundle_identity, untrusted, lifecycle_identity, drift_report)[0]
    validation_finding = evaluate_validation_status_visibility(
        bundle_identity,
        invalid,
        lifecycle_identity,
        drift_report,
    )[0]
    support_finding = evaluate_support_status_visibility(bundle_identity, prohibited, lifecycle_identity, drift_report)[0]

    assert trust_finding.finding_type == GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY
    assert trust_finding.severity == GOVERNANCE_SEVERITY_WARNING
    assert validation_finding.severity == GOVERNANCE_SEVERITY_BLOCKING
    assert support_finding.severity == GOVERNANCE_SEVERITY_PROHIBITED
    assert all(finding.descriptive_only for finding in (trust_finding, validation_finding, support_finding))
    assert all(not finding.authorization_enabled for finding in (trust_finding, validation_finding, support_finding))
    assert all(not finding.execution_enabled for finding in (trust_finding, validation_finding, support_finding))


def test_v4_0_governance_visibility_counts_unsupported_prohibited_blocked_unknown_and_warnings():
    report = _representative_report()
    visibility = validate_trusted_bundle_governance_visibility(report)
    severity_counts = count_governance_severities(report.findings)

    assert visibility["valid"] is True
    assert report.unsupported_count == 3
    assert report.prohibited_count == 3
    assert report.blocked_count == 6
    assert report.unknown_count == 4
    assert report.warning_count == 7
    assert severity_counts["info"] == 4
    assert severity_counts["warning"] == 7
    assert severity_counts["blocking"] == 2
    assert severity_counts["prohibited"] == 2
    assert severity_counts["unknown"] == 3
    assert visibility["capability_enabled_count"] == 0
    assert visibility["production_consumption_prohibition_visible"] is True


def test_v4_0_governance_alignment_and_safety_findings_are_visible():
    report = _representative_report()
    findings = {finding.finding_type: finding for finding in report.findings}

    assert "patch_version" in findings[GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY].explanation
    assert "drift blockers" in findings[GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY].explanation
    assert findings[GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY].severity == GOVERNANCE_SEVERITY_WARNING
    assert findings[GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY].severity == GOVERNANCE_SEVERITY_BLOCKING
    assert findings[GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY].severity == "info"
    assert findings[GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY].severity == "info"
    assert report.replay_safe is True
    assert report.rollback_safe is True
    assert report.provenance_safe is True
    assert report.lineage_safe is True


def test_v4_0_governance_prohibits_production_consumption():
    report = _representative_report()
    findings = [finding for finding in report.findings if finding.finding_type == GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED]

    assert report.production_consumption_authorized is False
    assert report.production_bundle_consumption_enabled is False
    assert len(findings) == 1
    assert findings[0].severity == GOVERNANCE_SEVERITY_PROHIBITED
    assert findings[0].production_consumption_enabled is False
    assert "production_consumption_authorized remains false" in findings[0].explanation


def test_v4_0_governance_audit_does_not_mutate_bundle_lifecycle_or_drift_report():
    args = build_representative_trusted_bundle_governance_inputs()
    bundle_identity, trust_status, validation_status, support_status, blocked_domains, lifecycle_foundation, drift_report = args
    bundle_before = export_trusted_bundle_identity(bundle_identity)
    lifecycle_before = serialize_patch_lifecycle_foundation(lifecycle_foundation)
    drift_before = serialize_lifecycle_drift_report(drift_report)

    audit_trusted_bundle_lifecycle_governance(
        bundle_identity=bundle_identity,
        trust_status=trust_status,
        validation_status=validation_status,
        support_status=support_status,
        blocked_domains=blocked_domains,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
    )
    audit_trusted_bundle_lifecycle_governance(
        bundle_identity=bundle_identity,
        trust_status=trust_status,
        validation_status=validation_status,
        support_status=support_status,
        blocked_domains=blocked_domains,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
    )

    assert export_trusted_bundle_identity(bundle_identity) == bundle_before
    assert serialize_patch_lifecycle_foundation(lifecycle_foundation) == lifecycle_before
    assert serialize_lifecycle_drift_report(drift_report) == drift_before


def test_v4_0_governance_hash_changes_when_bundle_identity_changes():
    args = build_representative_trusted_bundle_governance_inputs()
    baseline = audit_trusted_bundle_lifecycle_governance(
        bundle_identity=args[0],
        trust_status=args[1],
        validation_status=args[2],
        support_status=args[3],
        blocked_domains=args[4],
        lifecycle_foundation=args[5],
        drift_report=args[6],
    )
    changed_bundle = replace(args[0], metadata_hash="sha256:v4_0_patch_lifecycle_changed_metadata")
    changed = audit_trusted_bundle_lifecycle_governance(
        bundle_identity=changed_bundle,
        trust_status=args[1],
        validation_status=args[2],
        support_status=args[3],
        blocked_domains=args[4],
        lifecycle_foundation=args[5],
        drift_report=args[6],
    )

    assert baseline.deterministic_report_hash != changed.deterministic_report_hash


def test_v4_0_governance_generated_report_contains_required_evidence_and_boundaries():
    report = build_v4_0_trusted_bundle_lifecycle_governance_report()
    governance_report = report["governance_report"]

    assert report["foundation_status"] == V4_0_TRUSTED_BUNDLE_GOVERNANCE_STATUS_STABLE
    assert report["governance_mode"] == "descriptive_only"
    assert report["blocked_domain_count"] == 4
    assert report["total_governance_findings"] == 18
    assert report["unsupported_count"] == 3
    assert report["prohibited_count"] == 3
    assert report["blocked_count"] == 6
    assert report["unknown_count"] == 4
    assert report["warning_count"] == 7
    assert report["production_consumption_authorization_status"] is False
    assert report["deterministic_governance_report_hash"] == governance_report["deterministic_report_hash"]
    assert set(report["implemented_governance_finding_types"]) == set(TRUSTED_BUNDLE_GOVERNANCE_FINDING_TYPES)
    assert report["non_execution_guarantees"]["approval_absent"] is True
    assert report["non_execution_guarantees"]["authorization_absent"] is True
    assert report["non_execution_guarantees"]["execution_absent"] is True
    assert report["non_execution_guarantees"]["orchestration_execution_absent"] is True
    assert report["non_execution_guarantees"]["production_consumption_authorized"] is False
    assert report["summary"]["capability_enabled_count"] == 0
    assert "v4.0 Phase 3 does not authorize production consumption." in report["explicit_limitations"]


def test_v4_0_governance_export_preserves_blocked_domains_and_prohibition():
    report = _representative_report()
    exported = export_trusted_bundle_governance_report(report)

    assert exported["blocked_domains"] == sorted(exported["blocked_domains"])
    assert "blocked_schema_domain" in exported["blocked_domains"]
    assert "prohibited_production_consumption" in exported["blocked_domains"]
    assert "unknown_bundle_state_domain" in exported["blocked_domains"]
    assert "unsupported_modifier_domain" in exported["blocked_domains"]
    assert exported["production_consumption_authorized"] is False
    assert [finding["deterministic_key"] for finding in exported["findings"]] == sorted(
        finding["deterministic_key"] for finding in exported["findings"]
    )
