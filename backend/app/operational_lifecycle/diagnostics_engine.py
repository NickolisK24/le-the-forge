"""Deterministic operational explainability and diagnostics engine.

The diagnostics engine explains the evidence chain produced by v4.0 Phases 1-6.
It does not recommend, rank, score, select, optimize, authorize, remediate,
execute, orchestrate, or mutate source evidence.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_models import TrustedBundleGovernanceReport
from .diagnostics_hashing import hash_operational_diagnostics_report
from .diagnostics_models import (
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
    DIAGNOSTIC_SEVERITY_INFO,
    DIAGNOSTIC_SEVERITY_PROHIBITED,
    DIAGNOSTIC_SEVERITY_UNKNOWN,
    DIAGNOSTIC_SEVERITY_WARNING,
    DIAGNOSTIC_TYPE_BLOCKED_STATE,
    DIAGNOSTIC_TYPE_BUNDLE_GOVERNANCE,
    DIAGNOSTIC_TYPE_CRITICAL,
    DIAGNOSTIC_TYPE_DRIFT,
    DIAGNOSTIC_TYPE_EXECUTION_BOUNDARY,
    DIAGNOSTIC_TYPE_LIFECYCLE,
    DIAGNOSTIC_TYPE_LINEAGE,
    DIAGNOSTIC_TYPE_PRODUCTION_CONSUMPTION,
    DIAGNOSTIC_TYPE_PROHIBITED_STATE,
    DIAGNOSTIC_TYPE_PROVENANCE,
    DIAGNOSTIC_TYPE_RECOVERY,
    DIAGNOSTIC_TYPE_REPLAY,
    DIAGNOSTIC_TYPE_ROLLBACK,
    DIAGNOSTIC_TYPE_UNKNOWN_STATE,
    DIAGNOSTIC_TYPE_UNSUPPORTED_STATE,
    DIAGNOSTIC_TYPE_VALIDATION,
    DIAGNOSTIC_TYPE_WARNING,
    OperationalDiagnosticEntry,
    OperationalDiagnosticsReport,
)
from .diagnostics_visibility import (
    blocked_diagnostic_count,
    count_diagnostic_categories,
    count_diagnostic_severities,
    critical_diagnostic_count,
    prohibited_diagnostic_count,
    unknown_diagnostic_count,
    unsupported_diagnostic_count,
    warning_diagnostic_count,
)
from .lifecycle_drift_models import LifecycleDriftReport
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import (
    LIFECYCLE_STATE_BLOCKED,
    LIFECYCLE_STATE_DEPRECATED,
    LIFECYCLE_STATE_EXPERIMENTAL,
    LIFECYCLE_STATE_PROHIBITED,
    LIFECYCLE_STATE_SUPPORTED,
    LIFECYCLE_STATE_UNKNOWN,
    LIFECYCLE_STATE_UNSUPPORTED,
    PatchLifecycleFoundation,
)
from .lifecycle_serialization import stable_serialize
from .production_consumption_models import ProductionConsumptionGovernanceReport
from .recovery_certification_models import RecoveryCertificationReport
from .validation_automation_models import OperationalValidationReport


def build_operational_diagnostics_report(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticsReport:
    entries = order_operational_diagnostic_entries(
        (
            evaluate_lifecycle_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_drift_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_bundle_governance_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_validation_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_production_consumption_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_recovery_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_provenance_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_lineage_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_replay_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_rollback_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_unsupported_state_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_prohibited_state_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_blocked_state_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_unknown_state_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_warning_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_critical_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
            evaluate_execution_boundary_diagnostic(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
            ),
        )
    )
    category_counts = count_diagnostic_categories(entries)
    severity_counts = count_diagnostic_severities(entries)
    placeholder = OperationalDiagnosticsReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        production_consumption_report_hash=production_consumption_report.deterministic_report_hash,
        recovery_report_hash=recovery_report.deterministic_report_hash,
        entry_count=len(entries),
        entries=entries,
        category_counts=category_counts,
        severity_counts=severity_counts,
        unsupported_count=unsupported_diagnostic_count(entries),
        prohibited_count=prohibited_diagnostic_count(entries),
        blocked_count=blocked_diagnostic_count(entries),
        unknown_count=unknown_diagnostic_count(entries),
        warning_count=warning_diagnostic_count(entries),
        critical_count=critical_diagnostic_count(entries),
        replay_safe=(
            drift_report.replay_safe
            and governance_report.replay_safe
            and validation_report.replay_safe
            and production_consumption_report.replay_safe
            and recovery_report.replay_safe
        ),
        rollback_safe=(
            drift_report.rollback_safe
            and governance_report.rollback_safe
            and validation_report.rollback_safe
            and production_consumption_report.rollback_safe
            and recovery_report.rollback_safe
        ),
        provenance_safe=(
            drift_report.provenance_safe
            and governance_report.provenance_safe
            and validation_report.provenance_safe
            and production_consumption_report.provenance_safe
            and recovery_report.provenance_safe
        ),
        lineage_safe=governance_report.lineage_safe
        and validation_report.lineage_safe
        and production_consumption_report.lineage_safe
        and recovery_report.lineage_safe,
        recommendations_present=False,
        execution_authorized=False,
        deterministic_report_hash="pending",
    )
    return replace(placeholder, deterministic_report_hash=hash_operational_diagnostics_report(placeholder))


def evaluate_lifecycle_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    state_count = len(lifecycle_foundation.lifecycle_states)
    fail_visible_count = _lifecycle_fail_visible_state_count(lifecycle_foundation)
    severity = DIAGNOSTIC_SEVERITY_WARNING if fail_visible_count else DIAGNOSTIC_SEVERITY_INFO
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_LIFECYCLE,
        category=DIAGNOSTIC_CATEGORY_LIFECYCLE,
        severity=severity,
        title="Lifecycle Evidence",
        explanation=f"Lifecycle foundation exposes {state_count} lifecycle states with {fail_visible_count} fail-visible states.",
        limitation="This diagnostic is descriptive-only and does not change lifecycle state.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_drift_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    severity = DIAGNOSTIC_SEVERITY_BLOCKING if drift_report.blocking_drift_count else DIAGNOSTIC_SEVERITY_WARNING
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_DRIFT,
        category=DIAGNOSTIC_CATEGORY_DRIFT,
        severity=severity,
        title="Drift Evidence",
        explanation=(
            f"Drift report exposes {drift_report.finding_count} findings with "
            f"{drift_report.blocking_drift_count} blocking drift findings."
        ),
        limitation="This diagnostic describes drift only and does not correct drift.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_bundle_governance_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    severity = DIAGNOSTIC_SEVERITY_BLOCKING if governance_report.blocked_count else DIAGNOSTIC_SEVERITY_WARNING
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_BUNDLE_GOVERNANCE,
        category=DIAGNOSTIC_CATEGORY_BUNDLE_GOVERNANCE,
        severity=severity,
        title="Bundle Governance Evidence",
        explanation=(
            f"Bundle governance exposes trust={governance_report.trust_status}, "
            f"validation={governance_report.validation_status}, support={governance_report.support_status}, "
            f"blocked domains={len(governance_report.blocked_domains)}."
        ),
        limitation="This diagnostic does not authorize trusted bundle consumption.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_validation_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    severity = DIAGNOSTIC_SEVERITY_BLOCKING if validation_report.blocked_count else DIAGNOSTIC_SEVERITY_WARNING
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_VALIDATION,
        category=DIAGNOSTIC_CATEGORY_VALIDATION,
        severity=severity,
        title="Validation Evidence",
        explanation=(
            f"Validation report state is {validation_report.validation_state} with "
            f"{validation_report.blocked_count} blocked findings and {validation_report.critical_count} critical findings."
        ),
        limitation="This diagnostic does not authorize operational execution.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_production_consumption_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    severity = (
        DIAGNOSTIC_SEVERITY_BLOCKING
        if production_consumption_report.blocked_gate_count
        else DIAGNOSTIC_SEVERITY_WARNING
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_PRODUCTION_CONSUMPTION,
        category=DIAGNOSTIC_CATEGORY_PRODUCTION_CONSUMPTION,
        severity=severity,
        title="Production Consumption Evidence",
        explanation=(
            f"Production consumption report exposes {production_consumption_report.gate_count} gates with "
            f"{production_consumption_report.blocked_gate_count} blocked gates; enabled=false."
        ),
        limitation="This diagnostic does not enable production consumption.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_recovery_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    severity = DIAGNOSTIC_SEVERITY_PROHIBITED if recovery_report.prohibited_count else DIAGNOSTIC_SEVERITY_BLOCKING
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_RECOVERY,
        category=DIAGNOSTIC_CATEGORY_RECOVERY,
        severity=severity,
        title="Recovery Certification Evidence",
        explanation=(
            f"Recovery certification state is {recovery_report.certification_state} with "
            f"{recovery_report.blocked_count} blocked findings and {recovery_report.prohibited_count} prohibited findings."
        ),
        limitation="This diagnostic does not execute rollback or recovery.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_provenance_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    safe = (
        drift_report.provenance_safe
        and governance_report.provenance_safe
        and validation_report.provenance_safe
        and production_consumption_report.provenance_safe
        and recovery_report.provenance_safe
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_PROVENANCE,
        category=DIAGNOSTIC_CATEGORY_PROVENANCE,
        severity=DIAGNOSTIC_SEVERITY_WARNING if safe else DIAGNOSTIC_SEVERITY_BLOCKING,
        title="Provenance Evidence",
        explanation=f"Provenance diagnostic context is visible with provenance_safe={safe}.",
        limitation="This diagnostic preserves provenance evidence without inferred provenance.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_lineage_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    safe = governance_report.lineage_safe and validation_report.lineage_safe and production_consumption_report.lineage_safe
    safe = safe and recovery_report.lineage_safe
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_LINEAGE,
        category=DIAGNOSTIC_CATEGORY_LINEAGE,
        severity=DIAGNOSTIC_SEVERITY_WARNING if safe else DIAGNOSTIC_SEVERITY_BLOCKING,
        title="Lineage Evidence",
        explanation=f"Lineage diagnostic context is visible with lineage_safe={safe}.",
        limitation="This diagnostic preserves lineage evidence without automatic lineage correction.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_replay_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    safe = (
        drift_report.replay_safe
        and governance_report.replay_safe
        and validation_report.replay_safe
        and production_consumption_report.replay_safe
        and recovery_report.replay_safe
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_REPLAY,
        category=DIAGNOSTIC_CATEGORY_REPLAY,
        severity=DIAGNOSTIC_SEVERITY_WARNING if safe else DIAGNOSTIC_SEVERITY_BLOCKING,
        title="Replay Evidence",
        explanation=f"Replay diagnostic context is visible with replay_safe={safe}.",
        limitation="This diagnostic does not execute replay.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_rollback_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    safe = (
        drift_report.rollback_safe
        and governance_report.rollback_safe
        and validation_report.rollback_safe
        and production_consumption_report.rollback_safe
        and recovery_report.rollback_safe
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_ROLLBACK,
        category=DIAGNOSTIC_CATEGORY_ROLLBACK,
        severity=DIAGNOSTIC_SEVERITY_WARNING if safe else DIAGNOSTIC_SEVERITY_BLOCKING,
        title="Rollback Evidence",
        explanation=f"Rollback diagnostic context is visible with rollback_safe={safe}.",
        limitation="This diagnostic does not execute rollback.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_unsupported_state_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNSUPPORTED)
        + drift_report.unsupported_drift_count
        + governance_report.unsupported_count
        + validation_report.unsupported_count
        + production_consumption_report.unsupported_gate_count
        + recovery_report.unsupported_count
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_UNSUPPORTED_STATE,
        category=DIAGNOSTIC_CATEGORY_UNSUPPORTED,
        severity=DIAGNOSTIC_SEVERITY_WARNING if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Unsupported State Evidence",
        explanation=f"Unsupported diagnostic context is visible with unsupported_evidence_count={total}.",
        limitation="This diagnostic exposes unsupported state evidence without support escalation.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_prohibited_state_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_PROHIBITED)
        + drift_report.prohibited_drift_count
        + governance_report.prohibited_count
        + validation_report.prohibited_count
        + production_consumption_report.prohibited_gate_count
        + recovery_report.prohibited_count
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_PROHIBITED_STATE,
        category=DIAGNOSTIC_CATEGORY_PROHIBITED,
        severity=DIAGNOSTIC_SEVERITY_PROHIBITED if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Prohibited State Evidence",
        explanation=f"Prohibited diagnostic context is visible with prohibited_evidence_count={total}.",
        limitation="This diagnostic preserves prohibited state evidence without authorization.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_blocked_state_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_BLOCKED)
        + drift_report.blocking_drift_count
        + governance_report.blocked_count
        + validation_report.blocked_count
        + production_consumption_report.blocked_gate_count
        + recovery_report.blocked_count
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_BLOCKED_STATE,
        category=DIAGNOSTIC_CATEGORY_BLOCKED,
        severity=DIAGNOSTIC_SEVERITY_BLOCKING if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Blocked State Evidence",
        explanation=f"Blocked diagnostic context is visible with blocked_evidence_count={total}.",
        limitation="This diagnostic preserves blocker evidence without resolving blockers.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_unknown_state_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNKNOWN)
        + drift_report.unknown_drift_count
        + governance_report.unknown_count
        + validation_report.unknown_count
        + production_consumption_report.unknown_gate_count
        + recovery_report.unknown_count
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_UNKNOWN_STATE,
        category=DIAGNOSTIC_CATEGORY_UNKNOWN,
        severity=DIAGNOSTIC_SEVERITY_UNKNOWN if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Unknown State Evidence",
        explanation=f"Unknown diagnostic context is visible with unknown_evidence_count={total}.",
        limitation="This diagnostic preserves unknown state evidence without classification changes.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_warning_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_DEPRECATED)
        + _state_count(lifecycle_foundation, LIFECYCLE_STATE_EXPERIMENTAL)
        + governance_report.warning_count
        + validation_report.warning_count
        + production_consumption_report.warning_count
        + recovery_report.warning_count
    )
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_WARNING,
        category=DIAGNOSTIC_CATEGORY_WARNING,
        severity=DIAGNOSTIC_SEVERITY_WARNING if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Warning Evidence",
        explanation=f"Warning diagnostic context is visible with warning_evidence_count={total}.",
        limitation="This diagnostic preserves warning evidence without escalation.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_critical_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    total = validation_report.critical_count + production_consumption_report.critical_count + recovery_report.critical_count
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_CRITICAL,
        category=DIAGNOSTIC_CATEGORY_CRITICAL,
        severity=DIAGNOSTIC_SEVERITY_CRITICAL if total else DIAGNOSTIC_SEVERITY_INFO,
        title="Critical Evidence",
        explanation=f"Critical diagnostic context is visible with critical_evidence_count={total}.",
        limitation="This diagnostic preserves critical evidence without runtime mutation.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def evaluate_execution_boundary_diagnostic(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    return build_operational_diagnostic_entry(
        diagnostic_type=DIAGNOSTIC_TYPE_EXECUTION_BOUNDARY,
        category=DIAGNOSTIC_CATEGORY_EXECUTION_BOUNDARY,
        severity=DIAGNOSTIC_SEVERITY_PROHIBITED,
        title="Execution Boundary Evidence",
        explanation="Execution boundary diagnostics are visible with execution_authorized=false.",
        limitation="This diagnostic preserves the execution prohibition boundary.",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
    )


def build_operational_diagnostic_entry(
    *,
    diagnostic_type: str,
    category: str,
    severity: str,
    title: str,
    explanation: str,
    limitation: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> OperationalDiagnosticEntry:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )
    lineage_reference = _lineage_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
    )
    replay_reference = _continuity_reference(lifecycle_foundation, "replay")
    rollback_reference = _continuity_reference(lifecycle_foundation, "rollback")
    deterministic_key = stable_serialize(
        {
            "diagnostic_type": diagnostic_type,
            "category": category,
            "severity": severity,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_report.deterministic_report_hash,
            "governance_reference": governance_report.deterministic_report_hash,
            "validation_reference": validation_report.deterministic_report_hash,
            "production_consumption_reference": production_consumption_report.deterministic_report_hash,
            "recovery_reference": recovery_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "title": title,
            "explanation": explanation,
            "limitation": limitation,
        }
    )
    return OperationalDiagnosticEntry(
        diagnostic_type=diagnostic_type,
        category=category,
        severity=severity,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_report.deterministic_report_hash,
        governance_reference=governance_report.deterministic_report_hash,
        validation_reference=validation_report.deterministic_report_hash,
        production_consumption_reference=production_consumption_report.deterministic_report_hash,
        recovery_reference=recovery_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        title=title,
        explanation=explanation,
        limitation=limitation,
        deterministic_key=deterministic_key,
    )


def order_operational_diagnostic_entries(
    entries: Iterable[OperationalDiagnosticEntry],
) -> tuple[OperationalDiagnosticEntry, ...]:
    return tuple(sorted(tuple(entries), key=lambda item: item.deterministic_key))


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> str:
    references = tuple(sorted(record.provenance_reference_id for record in lifecycle_foundation.provenance_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
            f"recovery:{recovery_report.deterministic_report_hash}",
        )
    )


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
) -> str:
    references = tuple(sorted(record.lineage_reference_id for record in lifecycle_foundation.lineage_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
            f"recovery:{recovery_report.deterministic_report_hash}",
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
    return "|".join(references) if references else f"{token}_diagnostic_reference_not_visible"


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
