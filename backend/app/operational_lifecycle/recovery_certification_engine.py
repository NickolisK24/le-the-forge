"""Deterministic rollback and recovery certification engine.

The certification engine assembles recovery visibility across prior v4.0
evidence layers. It never executes rollback or recovery, authorizes recovery,
repairs records, resolves blockers, or mutates input evidence.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_models import TrustedBundleGovernanceReport
from .lifecycle_drift_models import LifecycleDriftReport
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
from .production_consumption_models import ProductionConsumptionGovernanceReport
from .recovery_certification_hashing import hash_recovery_certification_report
from .recovery_certification_models import (
    RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
    RECOVERY_CERTIFICATION_SEVERITY_CRITICAL,
    RECOVERY_CERTIFICATION_SEVERITY_INFO,
    RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
    RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN,
    RECOVERY_CERTIFICATION_SEVERITY_WARNING,
    RECOVERY_CERTIFICATION_STATE_BLOCKED,
    RECOVERY_CERTIFICATION_STATE_CERTIFIABLE,
    RECOVERY_CERTIFICATION_STATE_NOT_CERTIFIABLE,
    RECOVERY_CERTIFICATION_STATE_PROHIBITED,
    RECOVERY_CERTIFICATION_STATE_UNKNOWN,
    RECOVERY_CERTIFICATION_STATE_UNSUPPORTED,
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
    RecoveryCertificationFinding,
    RecoveryCertificationReport,
)
from .recovery_certification_visibility import (
    blocked_recovery_count,
    certifiable_recovery_count,
    critical_recovery_count,
    prohibited_recovery_count,
    unknown_recovery_count,
    unsupported_recovery_count,
    warning_recovery_count,
)
from .validation_automation_models import OperationalValidationReport


def certify_rollback_recovery(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationReport:
    findings = order_recovery_certification_findings(
        (
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
    )
    placeholder = RecoveryCertificationReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        production_consumption_report_hash=production_consumption_report.deterministic_report_hash,
        certification_state=determine_recovery_certification_state(findings),
        finding_count=len(findings),
        findings=findings,
        certifiable_finding_count=certifiable_recovery_count(findings),
        blocked_count=blocked_recovery_count(findings),
        unsupported_count=unsupported_recovery_count(findings),
        prohibited_count=prohibited_recovery_count(findings),
        unknown_count=unknown_recovery_count(findings),
        warning_count=warning_recovery_count(findings),
        critical_count=critical_recovery_count(findings),
        replay_safe=(
            drift_report.replay_safe
            and governance_report.replay_safe
            and validation_report.replay_safe
            and production_consumption_report.replay_safe
        ),
        rollback_safe=(
            drift_report.rollback_safe
            and governance_report.rollback_safe
            and validation_report.rollback_safe
            and production_consumption_report.rollback_safe
        ),
        provenance_safe=(
            drift_report.provenance_safe
            and governance_report.provenance_safe
            and validation_report.provenance_safe
            and production_consumption_report.provenance_safe
        ),
        lineage_safe=governance_report.lineage_safe and validation_report.lineage_safe and production_consumption_report.lineage_safe,
        recovery_execution_authorized=False,
        rollback_execution_authorized=False,
        deterministic_report_hash="pending",
    )
    return replace(placeholder, deterministic_report_hash=hash_recovery_certification_report(placeholder))


def evaluate_lifecycle_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    state_count = len(lifecycle_foundation.lifecycle_states)
    severity = RECOVERY_CERTIFICATION_SEVERITY_WARNING if _lifecycle_fail_visible_state_count(lifecycle_foundation) else RECOVERY_CERTIFICATION_SEVERITY_INFO
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_LIFECYCLE_RECOVERY_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Lifecycle recovery evidence is visible with lifecycle_state_count={state_count}.",
    )


def evaluate_drift_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    severity = RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if drift_report.blocking_drift_count else RECOVERY_CERTIFICATION_SEVERITY_WARNING
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_DRIFT_RECOVERY_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Drift recovery evidence is visible with "
            f"drift_finding_count={drift_report.finding_count} and blocking_drift_count={drift_report.blocking_drift_count}."
        ),
    )


def evaluate_bundle_governance_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    severity = RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if governance_report.blocked_count else RECOVERY_CERTIFICATION_SEVERITY_WARNING
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_BUNDLE_GOVERNANCE_RECOVERY_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Bundle governance recovery evidence is visible with "
            f"blocked_count={governance_report.blocked_count} and prohibited_count={governance_report.prohibited_count}."
        ),
    )


def evaluate_operational_validation_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    severity = RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if validation_report.blocked_count else RECOVERY_CERTIFICATION_SEVERITY_WARNING
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_OPERATIONAL_VALIDATION_RECOVERY_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Operational validation recovery evidence is visible with "
            f"validation_state={validation_report.validation_state} and blocked_count={validation_report.blocked_count}."
        ),
    )


def evaluate_production_consumption_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    severity = RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if production_consumption_report.blocked_gate_count else RECOVERY_CERTIFICATION_SEVERITY_WARNING
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_PRODUCTION_CONSUMPTION_RECOVERY_VISIBILITY,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Production-consumption recovery evidence is visible with "
            f"blocked_gate_count={production_consumption_report.blocked_gate_count}; production consumption remains disabled."
        ),
    )


def evaluate_provenance_recovery_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    safe = (
        drift_report.provenance_safe
        and governance_report.provenance_safe
        and validation_report.provenance_safe
        and production_consumption_report.provenance_safe
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_PROVENANCE_RECOVERY_CONTINUITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_WARNING if safe else RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Provenance recovery continuity is visible with provenance_safe={safe}.",
    )


def evaluate_lineage_recovery_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_LINEAGE_RECOVERY_CONTINUITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if validation_report.blocked_count else RECOVERY_CERTIFICATION_SEVERITY_WARNING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Lineage recovery continuity remains visible with "
            f"validation_blocked_count={validation_report.blocked_count}; gaps are not repaired."
        ),
    )


def evaluate_replay_recovery_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    safe = (
        drift_report.replay_safe
        and governance_report.replay_safe
        and validation_report.replay_safe
        and production_consumption_report.replay_safe
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_REPLAY_RECOVERY_CONTINUITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_WARNING if safe else RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Replay recovery continuity is visible with replay_safe={safe}; replay execution is not enabled.",
    )


def evaluate_rollback_recovery_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    safe = (
        drift_report.rollback_safe
        and governance_report.rollback_safe
        and validation_report.rollback_safe
        and production_consumption_report.rollback_safe
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_ROLLBACK_RECOVERY_CONTINUITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_WARNING if safe else RECOVERY_CERTIFICATION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Rollback recovery continuity is visible with rollback_safe={safe}; rollback execution is not enabled.",
    )


def evaluate_unsupported_recovery_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNSUPPORTED)
        + drift_report.unsupported_drift_count
        + governance_report.unsupported_count
        + validation_report.unsupported_count
        + production_consumption_report.unsupported_gate_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE,
        severity=RECOVERY_CERTIFICATION_SEVERITY_WARNING if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Unsupported recovery states remain visible with unsupported_recovery_evidence_count={total}.",
    )


def evaluate_prohibited_recovery_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_PROHIBITED)
        + drift_report.prohibited_drift_count
        + governance_report.prohibited_count
        + validation_report.prohibited_count
        + production_consumption_report.prohibited_gate_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_PROHIBITED_RECOVERY_STATE,
        severity=RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Prohibited recovery states remain visible with prohibited_recovery_evidence_count={total}.",
    )


def evaluate_blocked_recovery_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_BLOCKED)
        + drift_report.blocking_drift_count
        + governance_report.blocked_count
        + validation_report.blocked_count
        + production_consumption_report.blocked_gate_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_BLOCKED_RECOVERY_STATE,
        severity=RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Blocked recovery states remain visible with blocked_recovery_evidence_count={total}.",
    )


def evaluate_unknown_recovery_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNKNOWN)
        + drift_report.unknown_drift_count
        + governance_report.unknown_count
        + validation_report.unknown_count
        + production_consumption_report.unknown_gate_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_UNKNOWN_RECOVERY_STATE,
        severity=RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Unknown recovery states remain visible with unknown_recovery_evidence_count={total}.",
    )


def evaluate_recovery_warning_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_DEPRECATED)
        + _state_count(lifecycle_foundation, LIFECYCLE_STATE_EXPERIMENTAL)
        + governance_report.warning_count
        + validation_report.warning_count
        + production_consumption_report.warning_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_RECOVERY_WARNING_VISIBILITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_WARNING if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Recovery warning states remain visible with warning_recovery_evidence_count={total}.",
    )


def evaluate_critical_recovery_visibility(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    total = validation_report.critical_count + production_consumption_report.critical_count
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_CRITICAL_RECOVERY_VISIBILITY,
        severity=RECOVERY_CERTIFICATION_SEVERITY_CRITICAL if total else RECOVERY_CERTIFICATION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=f"Critical recovery states remain visible with critical_recovery_evidence_count={total}.",
    )


def evaluate_recovery_certification_readiness(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    blocker_total = (
        drift_report.blocking_drift_count
        + governance_report.blocked_count
        + validation_report.blocked_count
        + production_consumption_report.blocked_gate_count
        + validation_report.critical_count
        + production_consumption_report.critical_count
    )
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_RECOVERY_CERTIFICATION_READINESS,
        severity=RECOVERY_CERTIFICATION_SEVERITY_BLOCKING if blocker_total else RECOVERY_CERTIFICATION_SEVERITY_WARNING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation=(
            "Recovery certification readiness is visible as evidence only with "
            f"recovery_blocker_count={blocker_total}; certifiable does not authorize rollback or recovery."
        ),
    )


def evaluate_rollback_execution_prohibition(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_ROLLBACK_EXECUTION_PROHIBITED,
        severity=RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation="Rollback execution is explicitly prohibited and rollback_execution_authorized remains false.",
    )


def evaluate_recovery_execution_prohibition(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> RecoveryCertificationFinding:
    return build_recovery_certification_finding(
        finding_type=RECOVERY_FINDING_RECOVERY_EXECUTION_PROHIBITED,
        severity=RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        explanation="Recovery execution is explicitly prohibited and recovery_execution_authorized remains false.",
    )


def build_recovery_certification_finding(
    *,
    finding_type: str,
    severity: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    explanation: str,
) -> RecoveryCertificationFinding:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
    )
    lineage_reference = _lineage_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
    )
    replay_reference = _continuity_reference(lifecycle_foundation, "replay")
    rollback_reference = _continuity_reference(lifecycle_foundation, "rollback")
    recovery_reference = (
        f"recovery:{production_consumption_report.deterministic_report_hash}|"
        f"validation:{validation_report.deterministic_report_hash}"
    )
    deterministic_key = stable_serialize(
        {
            "finding_type": finding_type,
            "severity": severity,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_report.deterministic_report_hash,
            "governance_reference": governance_report.deterministic_report_hash,
            "validation_reference": validation_report.deterministic_report_hash,
            "production_consumption_reference": production_consumption_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "recovery_reference": recovery_reference,
            "explanation": explanation,
        }
    )
    return RecoveryCertificationFinding(
        finding_type=finding_type,
        severity=severity,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_report.deterministic_report_hash,
        governance_reference=governance_report.deterministic_report_hash,
        validation_reference=validation_report.deterministic_report_hash,
        production_consumption_reference=production_consumption_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        recovery_reference=recovery_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def order_recovery_certification_findings(
    findings: Iterable[RecoveryCertificationFinding],
) -> tuple[RecoveryCertificationFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def determine_recovery_certification_state(findings: tuple[RecoveryCertificationFinding, ...]) -> str:
    severities = {finding.severity for finding in findings}
    if RECOVERY_CERTIFICATION_SEVERITY_PROHIBITED in severities:
        return RECOVERY_CERTIFICATION_STATE_PROHIBITED
    if RECOVERY_CERTIFICATION_SEVERITY_CRITICAL in severities or RECOVERY_CERTIFICATION_SEVERITY_BLOCKING in severities:
        return RECOVERY_CERTIFICATION_STATE_BLOCKED
    if any(
        finding.finding_type == RECOVERY_FINDING_UNSUPPORTED_RECOVERY_STATE
        and finding.severity != RECOVERY_CERTIFICATION_SEVERITY_INFO
        for finding in findings
    ):
        return RECOVERY_CERTIFICATION_STATE_UNSUPPORTED
    if RECOVERY_CERTIFICATION_SEVERITY_UNKNOWN in severities:
        return RECOVERY_CERTIFICATION_STATE_UNKNOWN
    if RECOVERY_CERTIFICATION_SEVERITY_WARNING in severities:
        return RECOVERY_CERTIFICATION_STATE_NOT_CERTIFIABLE
    return RECOVERY_CERTIFICATION_STATE_CERTIFIABLE


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> str:
    references = tuple(sorted(record.provenance_reference_id for record in lifecycle_foundation.provenance_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
        )
    )


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
) -> str:
    references = tuple(sorted(record.lineage_reference_id for record in lifecycle_foundation.lineage_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
        )
    )


def _continuity_reference(lifecycle_foundation: PatchLifecycleFoundation, token: str) -> str:
    references = tuple(
        sorted(
            reference
            for record in lifecycle_foundation.lineage_records
            for reference in (*record.continuity_references, *record.rollback_references)
            if token in reference
        )
    )
    return "|".join(references) if references else f"{token}_recovery_reference_not_visible"


def _state_count(foundation: PatchLifecycleFoundation, state: str) -> int:
    return sum(1 for lifecycle_state in foundation.lifecycle_states if lifecycle_state.state == state)


def _lifecycle_fail_visible_state_count(foundation: PatchLifecycleFoundation) -> int:
    return sum(
        1
        for state in foundation.lifecycle_states
        if state.state
        in (
            LIFECYCLE_STATE_UNSUPPORTED,
            LIFECYCLE_STATE_BLOCKED,
            LIFECYCLE_STATE_EXPERIMENTAL,
            LIFECYCLE_STATE_UNKNOWN,
            LIFECYCLE_STATE_DEPRECATED,
            LIFECYCLE_STATE_PROHIBITED,
        )
    )
