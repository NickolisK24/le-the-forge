"""Deterministic trusted bundle lifecycle governance audit.

Governance audit functions produce evidence only. They do not approve bundles,
authorize bundles, consume bundles, deploy bundles, repair drift, execute patch
refresh behavior, or mutate lifecycle state.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_hashing import hash_trusted_bundle_governance_report
from .bundle_governance_models import (
    BUNDLE_SUPPORT_STATUS_BLOCKED,
    BUNDLE_SUPPORT_STATUS_PROHIBITED,
    BUNDLE_SUPPORT_STATUS_UNKNOWN,
    BUNDLE_SUPPORT_STATUS_UNSUPPORTED,
    BUNDLE_TRUST_STATUS_BLOCKED,
    BUNDLE_TRUST_STATUS_PROHIBITED,
    BUNDLE_TRUST_STATUS_UNKNOWN,
    BUNDLE_TRUST_STATUS_UNSUPPORTED,
    BUNDLE_TRUST_STATUS_UNTRUSTED,
    BUNDLE_VALIDATION_STATUS_BLOCKED,
    BUNDLE_VALIDATION_STATUS_INVALID,
    BUNDLE_VALIDATION_STATUS_MISSING,
    BUNDLE_VALIDATION_STATUS_PROHIBITED,
    BUNDLE_VALIDATION_STATUS_STALE,
    BUNDLE_VALIDATION_STATUS_UNKNOWN,
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
    GOVERNANCE_SEVERITY_INFO,
    GOVERNANCE_SEVERITY_PROHIBITED,
    GOVERNANCE_SEVERITY_UNKNOWN,
    GOVERNANCE_SEVERITY_WARNING,
    TrustedBundleGovernanceFinding,
    TrustedBundleGovernanceReport,
    TrustedBundleIdentity,
    TrustedBundleStatus,
    TrustedBundleSupportStatus,
    TrustedBundleValidationStatus,
)
from .bundle_governance_visibility import (
    blocked_governance_count,
    prohibited_governance_count,
    unknown_governance_count,
    unsupported_governance_count,
    warning_governance_count,
)
from .lifecycle_drift_models import LifecycleDriftReport
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import PatchLifecycleFoundation
from .lifecycle_serialization import stable_serialize


def audit_trusted_bundle_lifecycle_governance(
    *,
    bundle_identity: TrustedBundleIdentity,
    trust_status: TrustedBundleStatus,
    validation_status: TrustedBundleValidationStatus,
    support_status: TrustedBundleSupportStatus,
    blocked_domains: tuple[str, ...] | list[str],
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
) -> TrustedBundleGovernanceReport:
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    findings = order_trusted_bundle_governance_findings(
        (
            *evaluate_bundle_identity_visibility(bundle_identity, lifecycle_identity, drift_report),
            *evaluate_bundle_metadata_visibility(bundle_identity, lifecycle_identity, drift_report),
            *evaluate_trust_status_visibility(bundle_identity, trust_status, lifecycle_identity, drift_report),
            *evaluate_validation_status_visibility(bundle_identity, validation_status, lifecycle_identity, drift_report),
            *evaluate_support_status_visibility(bundle_identity, support_status, lifecycle_identity, drift_report),
            *evaluate_blocked_domain_visibility(bundle_identity, tuple(blocked_domains), lifecycle_identity, drift_report),
            *evaluate_lifecycle_alignment_visibility(bundle_identity, lifecycle_foundation, drift_report),
            *evaluate_drift_alignment_visibility(bundle_identity, lifecycle_identity, drift_report),
            *evaluate_provenance_continuity_visibility(bundle_identity, lifecycle_foundation, drift_report),
            *evaluate_lineage_continuity_visibility(bundle_identity, lifecycle_foundation, drift_report),
            *evaluate_replay_continuity_visibility(bundle_identity, lifecycle_foundation, lifecycle_identity, drift_report),
            *evaluate_rollback_continuity_visibility(bundle_identity, lifecycle_foundation, lifecycle_identity, drift_report),
            *evaluate_integrity_warning_visibility(
                bundle_identity,
                trust_status,
                validation_status,
                support_status,
                tuple(blocked_domains),
                lifecycle_identity,
                drift_report,
            ),
            *evaluate_unknown_governance_state(
                bundle_identity,
                trust_status,
                validation_status,
                support_status,
                lifecycle_identity,
                drift_report,
            ),
            evaluate_production_consumption_prohibition(bundle_identity, lifecycle_identity, drift_report),
        )
    )
    placeholder = TrustedBundleGovernanceReport(
        bundle_identity=bundle_identity,
        lifecycle_identity=lifecycle_identity,
        drift_report_hash=drift_report.deterministic_report_hash,
        trust_status=trust_status.status,
        validation_status=validation_status.status,
        support_status=support_status.status,
        blocked_domains=tuple(sorted(blocked_domains)),
        finding_count=len(findings),
        findings=findings,
        unsupported_count=unsupported_governance_count(findings),
        prohibited_count=prohibited_governance_count(findings),
        blocked_count=blocked_governance_count(findings),
        unknown_count=unknown_governance_count(findings),
        warning_count=warning_governance_count(findings),
        replay_safe=drift_report.replay_safe and _lineage_replay_safe(lifecycle_foundation),
        rollback_safe=drift_report.rollback_safe and _lineage_rollback_safe(lifecycle_foundation),
        provenance_safe=drift_report.provenance_safe and _provenance_safe(lifecycle_foundation),
        lineage_safe=_lineage_safe(lifecycle_foundation),
        production_consumption_authorized=False,
        deterministic_report_hash="pending",
    )
    return replace(placeholder, deterministic_report_hash=hash_trusted_bundle_governance_report(placeholder))


def evaluate_bundle_identity_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    missing_fields = [
        field
        for field in (
            "bundle_id",
            "patch_version",
            "extraction_version",
            "schema_version",
            "generated_timestamp",
            "bundle_hash",
            "manifest_hash",
            "metadata_hash",
        )
        if not getattr(bundle_identity, field)
    ]
    severity = GOVERNANCE_SEVERITY_UNKNOWN if missing_fields else GOVERNANCE_SEVERITY_INFO
    explanation = (
        f"Bundle identity fields are visible for `{bundle_identity.bundle_id}`."
        if not missing_fields
        else f"Bundle identity is missing visible fields: {', '.join(sorted(missing_fields))}."
    )
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_BUNDLE_IDENTITY_VISIBILITY,
            severity=severity,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=explanation,
        ),
    )


def evaluate_bundle_metadata_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_BUNDLE_METADATA_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_INFO,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=(
                "Bundle hash, manifest hash, and metadata hash are visible as governance evidence only."
            ),
        ),
    )


def evaluate_trust_status_visibility(
    bundle_identity: TrustedBundleIdentity,
    trust_status: TrustedBundleStatus,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_TRUST_STATUS_VISIBILITY,
            severity=_status_severity(trust_status.status),
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Trust status `{trust_status.status}` is visible and has no approval semantics.",
        ),
    )


def evaluate_validation_status_visibility(
    bundle_identity: TrustedBundleIdentity,
    validation_status: TrustedBundleValidationStatus,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_VALIDATION_STATUS_VISIBILITY,
            severity=_validation_severity(validation_status.status),
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Validation status `{validation_status.status}` is visible without automatic validation fixes.",
        ),
    )


def evaluate_support_status_visibility(
    bundle_identity: TrustedBundleIdentity,
    support_status: TrustedBundleSupportStatus,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_SUPPORT_STATUS_VISIBILITY,
            severity=_support_severity(support_status.status),
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Support status `{support_status.status}` is visible without implicit support upgrade.",
        ),
    )


def evaluate_blocked_domain_visibility(
    bundle_identity: TrustedBundleIdentity,
    blocked_domains: tuple[str, ...],
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return tuple(
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_BLOCKED_DOMAIN_VISIBILITY,
            severity=_domain_severity(domain),
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Blocked domain `{domain}` remains visible and uncorrected.",
        )
        for domain in sorted(blocked_domains)
    )


def evaluate_lifecycle_alignment_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    mismatches = _bundle_lifecycle_mismatches(bundle_identity, lifecycle_foundation)
    severity = GOVERNANCE_SEVERITY_WARNING if mismatches else GOVERNANCE_SEVERITY_INFO
    explanation = (
        f"Bundle lifecycle metadata differs from lifecycle identity fields: {', '.join(mismatches)}."
        if mismatches
        else "Bundle lifecycle metadata aligns with lifecycle identity fields."
    )
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_LIFECYCLE_ALIGNMENT_VISIBILITY,
            severity=severity,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=explanation,
        ),
    )


def evaluate_drift_alignment_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    bundle_patch_visible = bundle_identity.patch_version in (
        drift_report.source_lifecycle_identity + "|" + drift_report.target_lifecycle_identity
    )
    severity = GOVERNANCE_SEVERITY_WARNING if not bundle_patch_visible or drift_report.blocking_drift_count else GOVERNANCE_SEVERITY_INFO
    explanation = (
        "Bundle patch identity is visible in drift evidence, and drift blockers remain governance-visible."
        if bundle_patch_visible
        else "Bundle patch identity is not visible in source or target drift evidence."
    )
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_DRIFT_ALIGNMENT_VISIBILITY,
            severity=severity,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=explanation,
        ),
    )


def evaluate_provenance_continuity_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    trusted_references = tuple(record.trusted_bundle_reference for record in lifecycle_foundation.provenance_records)
    visible = bundle_identity.bundle_id in trusted_references
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_PROVENANCE_CONTINUITY_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_WARNING if not visible else GOVERNANCE_SEVERITY_INFO,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=(
                "Bundle identity is present in lifecycle provenance trusted bundle references."
                if visible
                else "Bundle identity is not present in lifecycle provenance trusted bundle references."
            ),
        ),
    )


def evaluate_lineage_continuity_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    trusted_references = tuple(
        item for record in lifecycle_foundation.lineage_records for item in record.trusted_bundle_references
    )
    visible = bundle_identity.bundle_id in trusted_references
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_LINEAGE_CONTINUITY_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_BLOCKING if not visible else GOVERNANCE_SEVERITY_INFO,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=(
                "Bundle identity is present in lifecycle lineage trusted bundle references."
                if visible
                else "Bundle identity is not present in lifecycle lineage trusted bundle references."
            ),
        ),
    )


def evaluate_replay_continuity_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    replay_safe = drift_report.replay_safe and _lineage_replay_safe(lifecycle_foundation)
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_REPLAY_CONTINUITY_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_INFO if replay_safe else GOVERNANCE_SEVERITY_BLOCKING,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation="Replay safety is visible as governance evidence and does not enable replay execution.",
        ),
    )


def evaluate_rollback_continuity_visibility(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    rollback_safe = drift_report.rollback_safe and _lineage_rollback_safe(lifecycle_foundation)
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_ROLLBACK_CONTINUITY_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_INFO if rollback_safe else GOVERNANCE_SEVERITY_BLOCKING,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation="Rollback safety is visible as governance evidence and does not enable rollback execution.",
        ),
    )


def evaluate_integrity_warning_visibility(
    bundle_identity: TrustedBundleIdentity,
    trust_status: TrustedBundleStatus,
    validation_status: TrustedBundleValidationStatus,
    support_status: TrustedBundleSupportStatus,
    blocked_domains: tuple[str, ...],
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    warnings = tuple(
        sorted(
            item
            for item in (
                trust_status.status,
                validation_status.status,
                support_status.status,
                *blocked_domains,
            )
            if any(token in item for token in ("stale", "unsupported", "blocked", "unknown", "prohibited"))
        )
    )
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_INTEGRITY_WARNING_VISIBILITY,
            severity=GOVERNANCE_SEVERITY_WARNING,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Governance warning states remain visible: {', '.join(warnings)}.",
        ),
    )


def evaluate_unknown_governance_state(
    bundle_identity: TrustedBundleIdentity,
    trust_status: TrustedBundleStatus,
    validation_status: TrustedBundleValidationStatus,
    support_status: TrustedBundleSupportStatus,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    unknowns = tuple(
        sorted(
            item
            for item in (trust_status.status, validation_status.status, support_status.status)
            if item == "unknown"
        )
    )
    if not unknowns:
        return ()
    return (
        build_trusted_bundle_governance_finding(
            finding_type=GOVERNANCE_FINDING_UNKNOWN_GOVERNANCE_STATE,
            severity=GOVERNANCE_SEVERITY_UNKNOWN,
            bundle_identity=bundle_identity,
            lifecycle_reference=lifecycle_identity,
            drift_reference=drift_report.deterministic_report_hash,
            explanation=f"Unknown governance states remain visible: {', '.join(unknowns)}.",
        ),
    )


def evaluate_production_consumption_prohibition(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_identity: str,
    drift_report: LifecycleDriftReport,
) -> TrustedBundleGovernanceFinding:
    return build_trusted_bundle_governance_finding(
        finding_type=GOVERNANCE_FINDING_PRODUCTION_CONSUMPTION_PROHIBITED,
        severity=GOVERNANCE_SEVERITY_PROHIBITED,
        bundle_identity=bundle_identity,
        lifecycle_reference=lifecycle_identity,
        drift_reference=drift_report.deterministic_report_hash,
        explanation="Production consumption is explicitly prohibited and production_consumption_authorized remains false.",
    )


def build_trusted_bundle_governance_finding(
    *,
    finding_type: str,
    severity: str,
    bundle_identity: TrustedBundleIdentity,
    lifecycle_reference: str,
    drift_reference: str,
    explanation: str,
) -> TrustedBundleGovernanceFinding:
    deterministic_key = stable_serialize(
        {
            "finding_type": finding_type,
            "severity": severity,
            "bundle_reference": bundle_identity.bundle_id,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_reference,
            "explanation": explanation,
        }
    )
    return TrustedBundleGovernanceFinding(
        finding_type=finding_type,
        severity=severity,
        bundle_reference=bundle_identity.bundle_id,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_reference,
        provenance_reference=f"bundle:{bundle_identity.bundle_hash}|manifest:{bundle_identity.manifest_hash}",
        lineage_reference=f"bundle:{bundle_identity.bundle_id}|metadata:{bundle_identity.metadata_hash}",
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def order_trusted_bundle_governance_findings(
    findings: Iterable[TrustedBundleGovernanceFinding],
) -> tuple[TrustedBundleGovernanceFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def _status_severity(status: str) -> str:
    if status in (BUNDLE_TRUST_STATUS_PROHIBITED,):
        return GOVERNANCE_SEVERITY_PROHIBITED
    if status in (BUNDLE_TRUST_STATUS_BLOCKED,):
        return GOVERNANCE_SEVERITY_BLOCKING
    if status in (BUNDLE_TRUST_STATUS_UNKNOWN,):
        return GOVERNANCE_SEVERITY_UNKNOWN
    if status in (BUNDLE_TRUST_STATUS_UNTRUSTED, BUNDLE_TRUST_STATUS_UNSUPPORTED):
        return GOVERNANCE_SEVERITY_WARNING
    return GOVERNANCE_SEVERITY_INFO


def _validation_severity(status: str) -> str:
    if status == BUNDLE_VALIDATION_STATUS_PROHIBITED:
        return GOVERNANCE_SEVERITY_PROHIBITED
    if status in (BUNDLE_VALIDATION_STATUS_BLOCKED, BUNDLE_VALIDATION_STATUS_INVALID, BUNDLE_VALIDATION_STATUS_MISSING):
        return GOVERNANCE_SEVERITY_BLOCKING
    if status == BUNDLE_VALIDATION_STATUS_UNKNOWN:
        return GOVERNANCE_SEVERITY_UNKNOWN
    if status == BUNDLE_VALIDATION_STATUS_STALE:
        return GOVERNANCE_SEVERITY_WARNING
    return GOVERNANCE_SEVERITY_INFO


def _support_severity(status: str) -> str:
    if status == BUNDLE_SUPPORT_STATUS_PROHIBITED:
        return GOVERNANCE_SEVERITY_PROHIBITED
    if status == BUNDLE_SUPPORT_STATUS_BLOCKED:
        return GOVERNANCE_SEVERITY_BLOCKING
    if status == BUNDLE_SUPPORT_STATUS_UNKNOWN:
        return GOVERNANCE_SEVERITY_UNKNOWN
    if status == BUNDLE_SUPPORT_STATUS_UNSUPPORTED:
        return GOVERNANCE_SEVERITY_WARNING
    return GOVERNANCE_SEVERITY_INFO


def _domain_severity(domain: str) -> str:
    lowered = domain.lower()
    if "prohibited" in lowered:
        return GOVERNANCE_SEVERITY_PROHIBITED
    if "blocked" in lowered:
        return GOVERNANCE_SEVERITY_BLOCKING
    if "unknown" in lowered:
        return GOVERNANCE_SEVERITY_UNKNOWN
    return GOVERNANCE_SEVERITY_WARNING


def _bundle_lifecycle_mismatches(
    bundle_identity: TrustedBundleIdentity,
    lifecycle_foundation: PatchLifecycleFoundation,
) -> tuple[str, ...]:
    lifecycle_identity = lifecycle_foundation.patch_identity
    mismatches = []
    for field_name in ("patch_version", "extraction_version", "schema_version"):
        if getattr(bundle_identity, field_name) != getattr(lifecycle_identity, field_name):
            mismatches.append(field_name)
    return tuple(sorted(mismatches))


def _lineage_replay_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.replay_safe and not record.execution_enabled for record in foundation.lineage_records)


def _lineage_rollback_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.rollback_safe and not record.execution_enabled for record in foundation.lineage_records)


def _provenance_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(
        record.provenance_preserved and record.no_inferred_provenance and not record.execution_enabled
        for record in foundation.provenance_records
    )


def _lineage_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(
        record.lineage_preserved
        and record.descriptive_only
        and not record.execution_enabled
        and not record.automatic_transition_enabled
        for record in foundation.lineage_records
    )
