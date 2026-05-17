"""Deterministic operational validation automation engine.

The engine assembles validation evidence from lifecycle, drift, and governance
records. It does not authorize execution, approve deployments, consume bundles,
repair records, or mutate any input evidence.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_models import TrustedBundleGovernanceReport
from .bundle_governance_visibility import count_governance_finding_types
from .lifecycle_drift_models import (
    DRIFT_TYPE_LINEAGE,
    DRIFT_TYPE_PROVENANCE,
    DRIFT_TYPE_REPLAY_CONTINUITY,
    DRIFT_TYPE_ROLLBACK_CONTINUITY,
    LifecycleDriftReport,
)
from .lifecycle_drift_visibility import count_drift_types
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import (
    LIFECYCLE_STATE_BLOCKED,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_EXPERIMENTAL,
    LIFECYCLE_STATE_PROHIBITED,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_UNSUPPORTED,
    PatchLifecycleFoundation,
)
from .lifecycle_serialization import stable_serialize
from .validation_automation_hashing import hash_operational_validation_report
from .validation_automation_models import (
    OPERATIONAL_VALIDATION_SEVERITY_BLOCKING,
    OPERATIONAL_VALIDATION_SEVERITY_CRITICAL,
    OPERATIONAL_VALIDATION_SEVERITY_INFO,
    OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED,
    OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN,
    OPERATIONAL_VALIDATION_SEVERITY_WARNING,
    OPERATIONAL_VALIDATION_STATE_BLOCKED,
    OPERATIONAL_VALIDATION_STATE_NOT_READY,
    OPERATIONAL_VALIDATION_STATE_PROHIBITED,
    OPERATIONAL_VALIDATION_STATE_READY,
    OPERATIONAL_VALIDATION_STATE_UNKNOWN,
    OPERATIONAL_VALIDATION_STATE_UNSUPPORTED,
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
    OperationalValidationFinding,
    OperationalValidationReport,
)
from .validation_automation_visibility import (
    blocked_validation_count,
    critical_validation_count,
    prohibited_validation_count,
    unknown_validation_count,
    unsupported_validation_count,
    warning_validation_count,
)


def build_operational_validation_report(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationReport:
    lifecycle_identity = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    findings = order_operational_validation_findings(
        (
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
    )
    placeholder = OperationalValidationReport(
        lifecycle_identity=lifecycle_identity,
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_state=determine_operational_validation_state(findings),
        finding_count=len(findings),
        findings=findings,
        unsupported_count=unsupported_validation_count(findings),
        prohibited_count=prohibited_validation_count(findings),
        blocked_count=blocked_validation_count(findings),
        unknown_count=unknown_validation_count(findings),
        warning_count=warning_validation_count(findings),
        critical_count=critical_validation_count(findings),
        replay_safe=drift_report.replay_safe and governance_report.replay_safe and _lifecycle_replay_safe(lifecycle_foundation),
        rollback_safe=(
            drift_report.rollback_safe
            and governance_report.rollback_safe
            and _lifecycle_rollback_safe(lifecycle_foundation)
        ),
        provenance_safe=(
            drift_report.provenance_safe
            and governance_report.provenance_safe
            and _lifecycle_provenance_safe(lifecycle_foundation)
        ),
        lineage_safe=governance_report.lineage_safe and _lifecycle_lineage_safe(lifecycle_foundation),
        operational_execution_authorized=False,
        deterministic_report_hash="pending",
    )
    return replace(placeholder, deterministic_report_hash=hash_operational_validation_report(placeholder))


def evaluate_lifecycle_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    states = tuple(sorted({state.state for state in lifecycle_foundation.lifecycle_states}))
    fail_visible_states = tuple(
        state
        for state in states
        if state
        in (
            LIFECYCLE_STATE_UNSUPPORTED,
            LIFECYCLE_STATE_BLOCKED,
            LIFECYCLE_STATE_EXPERIMENTAL,
            LIFECYCLE_STATE_UNKNOWN,
            LIFECYCLE_STATE_DEPRECATED,
            LIFECYCLE_STATE_PROHIBITED,
        )
    )
    severity = OPERATIONAL_VALIDATION_SEVERITY_WARNING if fail_visible_states else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_LIFECYCLE_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Lifecycle validation evidence preserves visible lifecycle states: "
            f"{', '.join(states)}."
        ),
    )


def evaluate_drift_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if drift_report.blocking_drift_count
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if drift_report.finding_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_DRIFT_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Drift validation evidence preserves drift finding counts "
            f"total={drift_report.finding_count}, blocking={drift_report.blocking_drift_count}, "
            f"unknown={drift_report.unknown_drift_count}."
        ),
    )


def evaluate_governance_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if governance_report.blocked_count or governance_report.prohibited_count
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if governance_report.warning_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_GOVERNANCE_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Governance validation evidence preserves governance counts "
            f"blocked={governance_report.blocked_count}, prohibited={governance_report.prohibited_count}, "
            f"warning={governance_report.warning_count}."
        ),
    )


def evaluate_provenance_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    drift_counts = count_drift_types(drift_report.findings)
    provenance_drift_count = drift_counts[DRIFT_TYPE_PROVENANCE]
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if not drift_report.provenance_safe or not governance_report.provenance_safe or not _lifecycle_provenance_safe(lifecycle_foundation)
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if provenance_drift_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_PROVENANCE_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Provenance continuity remains visible with provenance_drift_count={provenance_drift_count}.",
    )


def evaluate_lineage_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    drift_counts = count_drift_types(drift_report.findings)
    governance_counts = count_governance_finding_types(governance_report.findings)
    lineage_drift_count = drift_counts[DRIFT_TYPE_LINEAGE]
    governance_lineage_count = governance_counts["lineage_continuity_visibility"]
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if lineage_drift_count or governance_lineage_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_LINEAGE_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Lineage continuity remains visible with "
            f"lineage_drift_count={lineage_drift_count} and governance_lineage_visibility_count={governance_lineage_count}."
        ),
    )


def evaluate_replay_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    replay_drift_count = count_drift_types(drift_report.findings)[DRIFT_TYPE_REPLAY_CONTINUITY]
    replay_safe = drift_report.replay_safe and governance_report.replay_safe and _lifecycle_replay_safe(lifecycle_foundation)
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if not replay_safe
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if replay_drift_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_REPLAY_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Replay continuity remains evidence-only with replay_continuity_drift_count={replay_drift_count}.",
    )


def evaluate_rollback_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    rollback_drift_count = count_drift_types(drift_report.findings)[DRIFT_TYPE_ROLLBACK_CONTINUITY]
    rollback_safe = (
        drift_report.rollback_safe
        and governance_report.rollback_safe
        and _lifecycle_rollback_safe(lifecycle_foundation)
    )
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if not rollback_safe
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if rollback_drift_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_ROLLBACK_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Rollback continuity remains evidence-only with rollback_continuity_drift_count={rollback_drift_count}.",
    )


def evaluate_unsupported_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    lifecycle_unsupported_count = sum(
        1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_UNSUPPORTED
    )
    total = lifecycle_unsupported_count + drift_report.unsupported_drift_count + governance_report.unsupported_count
    severity = OPERATIONAL_VALIDATION_SEVERITY_WARNING if total else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Unsupported validation states remain visible with unsupported_evidence_count={total}.",
    )


def evaluate_prohibited_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    lifecycle_prohibited_count = sum(
        1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_PROHIBITED
    )
    total = lifecycle_prohibited_count + drift_report.prohibited_drift_count + governance_report.prohibited_count
    severity = OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED if total else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_PROHIBITED_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Prohibited validation states remain visible with prohibited_evidence_count={total}.",
    )


def evaluate_blocked_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    lifecycle_blocked_count = sum(
        1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_BLOCKED
    )
    total = lifecycle_blocked_count + drift_report.blocking_drift_count + governance_report.blocked_count
    severity = OPERATIONAL_VALIDATION_SEVERITY_BLOCKING if total else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_BLOCKED_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Blocked validation states remain visible with blocked_evidence_count={total}.",
    )


def evaluate_validation_warning_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    warning_count = (
        sum(1 for state in lifecycle_foundation.lifecycle_states if state.severity == "warning")
        + governance_report.warning_count
    )
    severity = OPERATIONAL_VALIDATION_SEVERITY_WARNING if warning_count else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_VALIDATION_WARNING_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Validation warnings remain visible with warning_evidence_count={warning_count}.",
    )


def evaluate_critical_validation_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    critical_source_count = drift_report.blocking_drift_count + governance_report.blocked_count + governance_report.prohibited_count
    severity = OPERATIONAL_VALIDATION_SEVERITY_CRITICAL if critical_source_count else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_CRITICAL_VALIDATION_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Critical validation visibility records unresolved blocked or prohibited evidence "
            f"with critical_source_count={critical_source_count}; no repair is attempted."
        ),
    )


def evaluate_operational_execution_prohibition(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_OPERATIONAL_EXECUTION_PROHIBITED,
        severity=OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation="Operational execution is explicitly prohibited and operational_execution_authorized remains false.",
    )


def evaluate_operational_certification_readiness(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    blocking_or_prohibited = drift_report.blocking_drift_count + governance_report.blocked_count + governance_report.prohibited_count
    severity = (
        OPERATIONAL_VALIDATION_SEVERITY_BLOCKING
        if blocking_or_prohibited
        else OPERATIONAL_VALIDATION_SEVERITY_WARNING
        if drift_report.finding_count or governance_report.warning_count
        else OPERATIONAL_VALIDATION_SEVERITY_INFO
    )
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_OPERATIONAL_CERTIFICATION_READINESS,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=(
            "Operational certification readiness is visible as evidence only "
            f"with blocking_or_prohibited_evidence_count={blocking_or_prohibited}."
        ),
    )


def evaluate_unknown_validation_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
) -> OperationalValidationFinding:
    lifecycle_unknown_count = sum(1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_UNKNOWN)
    total = lifecycle_unknown_count + drift_report.unknown_drift_count + governance_report.unknown_count
    severity = OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN if total else OPERATIONAL_VALIDATION_SEVERITY_INFO
    return build_operational_validation_finding(
        finding_type=VALIDATION_FINDING_UNKNOWN_VALIDATION_STATE,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        explanation=f"Unknown validation states remain visible with unknown_evidence_count={total}.",
    )


def build_operational_validation_finding(
    *,
    finding_type: str,
    severity: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    explanation: str,
) -> OperationalValidationFinding:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(lifecycle_foundation, governance_report)
    lineage_reference = _lineage_reference(lifecycle_foundation, governance_report)
    replay_reference = _continuity_reference(lifecycle_foundation, "replay")
    rollback_reference = _continuity_reference(lifecycle_foundation, "rollback")
    deterministic_key = stable_serialize(
        {
            "finding_type": finding_type,
            "severity": severity,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_report.deterministic_report_hash,
            "governance_reference": governance_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "explanation": explanation,
        }
    )
    return OperationalValidationFinding(
        finding_type=finding_type,
        severity=severity,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_report.deterministic_report_hash,
        governance_reference=governance_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def order_operational_validation_findings(
    findings: Iterable[OperationalValidationFinding],
) -> tuple[OperationalValidationFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def determine_operational_validation_state(findings: tuple[OperationalValidationFinding, ...]) -> str:
    severities = {finding.severity for finding in findings}
    if OPERATIONAL_VALIDATION_SEVERITY_PROHIBITED in severities:
        return OPERATIONAL_VALIDATION_STATE_PROHIBITED
    if OPERATIONAL_VALIDATION_SEVERITY_CRITICAL in severities or OPERATIONAL_VALIDATION_SEVERITY_BLOCKING in severities:
        return OPERATIONAL_VALIDATION_STATE_BLOCKED
    if any(
        finding.finding_type == VALIDATION_FINDING_UNSUPPORTED_VALIDATION_VISIBILITY
        and finding.severity != OPERATIONAL_VALIDATION_SEVERITY_INFO
        for finding in findings
    ):
        return OPERATIONAL_VALIDATION_STATE_UNSUPPORTED
    if OPERATIONAL_VALIDATION_SEVERITY_UNKNOWN in severities:
        return OPERATIONAL_VALIDATION_STATE_UNKNOWN
    if OPERATIONAL_VALIDATION_SEVERITY_WARNING in severities:
        return OPERATIONAL_VALIDATION_STATE_NOT_READY
    return OPERATIONAL_VALIDATION_STATE_READY


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
) -> str:
    references = tuple(sorted(record.provenance_reference_id for record in lifecycle_foundation.provenance_records))
    return "|".join((*references, f"governance:{governance_report.deterministic_report_hash}"))


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
) -> str:
    references = tuple(sorted(record.lineage_reference_id for record in lifecycle_foundation.lineage_records))
    return "|".join((*references, f"governance:{governance_report.deterministic_report_hash}"))


def _continuity_reference(lifecycle_foundation: PatchLifecycleFoundation, token: str) -> str:
    references = tuple(
        sorted(
            reference
            for record in lifecycle_foundation.lineage_records
            for reference in (*record.continuity_references, *record.rollback_references)
            if token in reference
        )
    )
    return "|".join(references) if references else f"{token}_continuity_reference_not_visible"


def _lifecycle_replay_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.replay_safe and not record.execution_enabled for record in foundation.lineage_records)


def _lifecycle_rollback_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(record.rollback_safe and not record.execution_enabled for record in foundation.lineage_records)


def _lifecycle_provenance_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(
        record.provenance_preserved and record.no_inferred_provenance and not record.execution_enabled
        for record in foundation.provenance_records
    )


def _lifecycle_lineage_safe(foundation: PatchLifecycleFoundation) -> bool:
    return all(
        record.lineage_preserved
        and record.descriptive_only
        and not record.execution_enabled
        and not record.automatic_transition_enabled
        for record in foundation.lineage_records
    )
