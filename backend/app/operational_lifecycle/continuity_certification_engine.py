"""Deterministic operational lifecycle continuity certification engine.

The certification engine assembles v4.0 Phase 1-8 continuity evidence. It
does not authorize execution, remediate continuity gaps, enable production
consumption, approve behavior, or mutate source reports.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_hashing import hash_trusted_bundle_governance_report
from .bundle_governance_models import TrustedBundleGovernanceReport
from .bundle_governance_serialization import serialize_trusted_bundle_governance_report
from .bundle_governance_visibility import validate_trusted_bundle_governance_visibility
from .continuity_certification_hashing import hash_operational_continuity_certification_report
from .continuity_certification_models import (
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
    CONTINUITY_SEVERITY_BLOCKING,
    CONTINUITY_SEVERITY_CRITICAL,
    CONTINUITY_SEVERITY_INFO,
    CONTINUITY_SEVERITY_PROHIBITED,
    CONTINUITY_SEVERITY_UNKNOWN,
    CONTINUITY_SEVERITY_WARNING,
    CONTINUITY_STATUS_BLOCKED,
    CONTINUITY_STATUS_BROKEN,
    CONTINUITY_STATUS_CERTIFIED,
    CONTINUITY_STATUS_PROHIBITED,
    CONTINUITY_STATUS_UNKNOWN,
    CONTINUITY_STATUS_WARNING,
    OperationalContinuityCertificationReport,
    OperationalContinuityFinding,
)
from .continuity_certification_visibility import (
    blocked_continuity_count,
    broken_continuity_count,
    certified_continuity_count,
    critical_continuity_count,
    prohibited_continuity_count,
    unknown_continuity_count,
    warning_continuity_count,
)
from .diagnostics_hashing import hash_operational_diagnostics_report
from .diagnostics_models import OperationalDiagnosticsReport
from .diagnostics_serialization import serialize_operational_diagnostics_report
from .diagnostics_visibility import validate_operational_diagnostics_visibility
from .integrity_enforcement_hashing import hash_operational_integrity_report
from .integrity_enforcement_models import OperationalIntegrityReport
from .integrity_enforcement_serialization import serialize_operational_integrity_report
from .integrity_enforcement_visibility import validate_operational_integrity_visibility
from .lifecycle_drift_hashing import hash_lifecycle_drift_report
from .lifecycle_drift_models import LifecycleDriftReport
from .lifecycle_drift_serialization import serialize_lifecycle_drift_report
from .lifecycle_drift_visibility import validate_lifecycle_drift_visibility
from .lifecycle_hashing import hash_patch_lifecycle_foundation
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import (
    LIFECYCLE_STATE_PROHIBITED,
    LIFECYCLE_STATE_UNKNOWN,
    PatchLifecycleFoundation,
)
from .lifecycle_serialization import serialize_patch_lifecycle_foundation, stable_serialize
from .lifecycle_visibility import validate_lifecycle_visibility
from .production_consumption_hashing import hash_production_consumption_governance_report
from .production_consumption_models import ProductionConsumptionGovernanceReport
from .production_consumption_serialization import serialize_production_consumption_governance_report
from .production_consumption_visibility import validate_production_consumption_visibility
from .recovery_certification_hashing import hash_recovery_certification_report
from .recovery_certification_models import RecoveryCertificationReport
from .recovery_certification_serialization import serialize_recovery_certification_report
from .recovery_certification_visibility import validate_recovery_certification_visibility
from .validation_automation_hashing import hash_operational_validation_report
from .validation_automation_models import OperationalValidationReport
from .validation_automation_serialization import serialize_operational_validation_report
from .validation_automation_visibility import validate_operational_validation_visibility


def certify_operational_lifecycle_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> OperationalContinuityCertificationReport:
    findings = order_operational_continuity_findings(
        (
            certify_lifecycle_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_drift_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_bundle_governance_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_operational_validation_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_production_consumption_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_recovery_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_diagnostics_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_integrity_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_provenance_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_lineage_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_replay_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_rollback_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_serialization_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_hashing_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_visibility_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_non_execution_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_non_remediation_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_non_authorization_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_production_consumption_disabled_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_prohibited_state_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
            certify_unknown_state_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                integrity_report,
            ),
        )
    )
    report = OperationalContinuityCertificationReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        production_consumption_report_hash=production_consumption_report.deterministic_report_hash,
        recovery_report_hash=recovery_report.deterministic_report_hash,
        diagnostics_report_hash=diagnostics_report.deterministic_report_hash,
        integrity_report_hash=integrity_report.deterministic_report_hash,
        continuity_status=determine_operational_continuity_status(findings),
        finding_count=len(findings),
        findings=findings,
        certified_count=certified_continuity_count(findings),
        warning_count=warning_continuity_count(findings),
        broken_count=broken_continuity_count(findings),
        blocked_count=blocked_continuity_count(findings),
        prohibited_count=prohibited_continuity_count(findings),
        unknown_count=unknown_continuity_count(findings),
        critical_count=critical_continuity_count(findings),
        replay_safe=_replay_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        rollback_safe=_rollback_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        provenance_safe=_provenance_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        lineage_safe=_lineage_safe(
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        serialization_stable=_serialization_stable(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        hashing_stable=_hashing_stable(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        visibility_preserved=_visibility_preserved(
            lifecycle_foundation,
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
        ),
        integrity_preserved=_integrity_preserved(integrity_report),
        execution_authorized=False,
        remediation_authorized=False,
        production_consumption_enabled=False,
        deterministic_report_hash="pending",
    )
    return replace(report, deterministic_report_hash=hash_operational_continuity_certification_report(report))


def certify_lifecycle_continuity(*args: object) -> OperationalContinuityFinding:
    lifecycle_foundation = args[0]
    visible = bool(lifecycle_identity_key(lifecycle_foundation.patch_identity))
    return _build_boolean_finding(CONTINUITY_FINDING_LIFECYCLE, "v4_0_phase_1", visible, "lifecycle_continuity_visible", *args)


def certify_drift_continuity(*args: object) -> OperationalContinuityFinding:
    drift_report = args[1]
    visible = bool(drift_report.deterministic_report_hash)
    return _build_boolean_finding(CONTINUITY_FINDING_DRIFT, "v4_0_phase_2", visible, "drift_continuity_visible", *args)


def certify_bundle_governance_continuity(*args: object) -> OperationalContinuityFinding:
    governance_report = args[2]
    visible = bool(governance_report.deterministic_report_hash)
    return _build_boolean_finding(
        CONTINUITY_FINDING_BUNDLE_GOVERNANCE,
        "v4_0_phase_3",
        visible,
        "bundle_governance_continuity_visible",
        *args,
    )


def certify_operational_validation_continuity(*args: object) -> OperationalContinuityFinding:
    validation_report = args[3]
    visible = bool(validation_report.deterministic_report_hash)
    return _build_boolean_finding(
        CONTINUITY_FINDING_OPERATIONAL_VALIDATION,
        "v4_0_phase_4",
        visible,
        "operational_validation_continuity_visible",
        *args,
    )


def certify_production_consumption_continuity(*args: object) -> OperationalContinuityFinding:
    production_consumption_report = args[4]
    visible = bool(production_consumption_report.deterministic_report_hash)
    return _build_boolean_finding(
        CONTINUITY_FINDING_PRODUCTION_CONSUMPTION,
        "v4_0_phase_5",
        visible,
        "production_consumption_continuity_visible",
        *args,
    )


def certify_recovery_continuity(*args: object) -> OperationalContinuityFinding:
    recovery_report = args[5]
    visible = bool(recovery_report.deterministic_report_hash)
    return _build_boolean_finding(CONTINUITY_FINDING_RECOVERY, "v4_0_phase_6", visible, "recovery_continuity_visible", *args)


def certify_diagnostics_continuity(*args: object) -> OperationalContinuityFinding:
    diagnostics_report = args[6]
    visible = bool(diagnostics_report.deterministic_report_hash)
    return _build_boolean_finding(
        CONTINUITY_FINDING_DIAGNOSTICS,
        "v4_0_phase_7",
        visible,
        "diagnostics_continuity_visible",
        *args,
    )


def certify_integrity_continuity(*args: object) -> OperationalContinuityFinding:
    integrity_report = args[7]
    preserved = _integrity_preserved(integrity_report)
    return _build_boolean_finding(
        CONTINUITY_FINDING_INTEGRITY,
        "v4_0_phase_8",
        preserved,
        "integrity_continuity_preserved",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_provenance_continuity(*args: object) -> OperationalContinuityFinding:
    safe = _provenance_safe(*args[1:])
    return _build_boolean_finding(CONTINUITY_FINDING_PROVENANCE, "v4_0_phase_1_to_8", safe, "provenance_safe", *args)


def certify_lineage_continuity(*args: object) -> OperationalContinuityFinding:
    safe = _lineage_safe(*args[2:])
    return _build_boolean_finding(CONTINUITY_FINDING_LINEAGE, "v4_0_phase_1_to_8", safe, "lineage_safe", *args)


def certify_replay_continuity(*args: object) -> OperationalContinuityFinding:
    safe = _replay_safe(*args[1:])
    return _build_boolean_finding(CONTINUITY_FINDING_REPLAY, "v4_0_phase_1_to_8", safe, "replay_safe", *args)


def certify_rollback_continuity(*args: object) -> OperationalContinuityFinding:
    safe = _rollback_safe(*args[1:])
    return _build_boolean_finding(CONTINUITY_FINDING_ROLLBACK, "v4_0_phase_1_to_8", safe, "rollback_safe", *args)


def certify_serialization_continuity(*args: object) -> OperationalContinuityFinding:
    stable = _serialization_stable(*args)
    return _build_boolean_finding(CONTINUITY_FINDING_SERIALIZATION, "v4_0_phase_1_to_8", stable, "serialization_stable", *args)


def certify_hashing_continuity(*args: object) -> OperationalContinuityFinding:
    stable = _hashing_stable(*args)
    return _build_boolean_finding(
        CONTINUITY_FINDING_HASHING,
        "v4_0_phase_1_to_8",
        stable,
        "hashing_stable",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_visibility_continuity(*args: object) -> OperationalContinuityFinding:
    visible = _visibility_preserved(*args)
    return _build_boolean_finding(CONTINUITY_FINDING_VISIBILITY, "v4_0_phase_1_to_8", visible, "visibility_preserved", *args)


def certify_non_execution_continuity(*args: object) -> OperationalContinuityFinding:
    preserved = _non_execution_preserved(*args)
    return _build_boolean_finding(
        CONTINUITY_FINDING_NON_EXECUTION,
        "v4_0_phase_1_to_8",
        preserved,
        "execution_authorized=False",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_non_remediation_continuity(*args: object) -> OperationalContinuityFinding:
    preserved = _non_remediation_preserved(*args)
    return _build_boolean_finding(
        CONTINUITY_FINDING_NON_REMEDIATION,
        "v4_0_phase_1_to_8",
        preserved,
        "remediation_authorized=False",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_non_authorization_continuity(*args: object) -> OperationalContinuityFinding:
    preserved = _non_authorization_preserved(*args)
    return _build_boolean_finding(
        CONTINUITY_FINDING_NON_AUTHORIZATION,
        "v4_0_phase_1_to_8",
        preserved,
        "authorization_absent",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_production_consumption_disabled_continuity(*args: object) -> OperationalContinuityFinding:
    preserved = _production_consumption_disabled(*args)
    return _build_boolean_finding(
        CONTINUITY_FINDING_PRODUCTION_DISABLED,
        "v4_0_phase_3_to_8",
        preserved,
        "production_consumption_enabled=False",
        *args,
        fail_severity=CONTINUITY_SEVERITY_CRITICAL,
    )


def certify_prohibited_state_continuity(*args: object) -> OperationalContinuityFinding:
    total = _prohibited_total(*args)
    return build_operational_continuity_finding(
        finding_type=CONTINUITY_FINDING_PROHIBITED_STATE,
        severity=CONTINUITY_SEVERITY_PROHIBITED if total else CONTINUITY_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_8",
        lifecycle_foundation=args[0],
        drift_report=args[1],
        governance_report=args[2],
        validation_report=args[3],
        production_consumption_report=args[4],
        recovery_report=args[5],
        diagnostics_report=args[6],
        integrity_report=args[7],
        explanation=f"prohibited_state_continuity_visible=True; prohibited_evidence_count={total}.",
    )


def certify_unknown_state_continuity(*args: object) -> OperationalContinuityFinding:
    total = _unknown_total(*args)
    return build_operational_continuity_finding(
        finding_type=CONTINUITY_FINDING_UNKNOWN_STATE,
        severity=CONTINUITY_SEVERITY_UNKNOWN if total else CONTINUITY_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_8",
        lifecycle_foundation=args[0],
        drift_report=args[1],
        governance_report=args[2],
        validation_report=args[3],
        production_consumption_report=args[4],
        recovery_report=args[5],
        diagnostics_report=args[6],
        integrity_report=args[7],
        explanation=f"unknown_state_continuity_visible=True; unknown_evidence_count={total}.",
    )


def build_operational_continuity_finding(
    *,
    finding_type: str,
    severity: str,
    source_phase: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
    explanation: str,
) -> OperationalContinuityFinding:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
        integrity_report,
    )
    lineage_reference = _lineage_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
        integrity_report,
    )
    replay_reference = _continuity_reference(lifecycle_foundation, "replay")
    rollback_reference = _continuity_reference(lifecycle_foundation, "rollback")
    deterministic_key = stable_serialize(
        {
            "finding_type": finding_type,
            "severity": severity,
            "source_phase": source_phase,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_report.deterministic_report_hash,
            "governance_reference": governance_report.deterministic_report_hash,
            "validation_reference": validation_report.deterministic_report_hash,
            "production_consumption_reference": production_consumption_report.deterministic_report_hash,
            "recovery_reference": recovery_report.deterministic_report_hash,
            "diagnostics_reference": diagnostics_report.deterministic_report_hash,
            "integrity_reference": integrity_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "explanation": explanation,
        }
    )
    return OperationalContinuityFinding(
        finding_type=finding_type,
        severity=severity,
        source_phase=source_phase,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_report.deterministic_report_hash,
        governance_reference=governance_report.deterministic_report_hash,
        validation_reference=validation_report.deterministic_report_hash,
        production_consumption_reference=production_consumption_report.deterministic_report_hash,
        recovery_reference=recovery_report.deterministic_report_hash,
        diagnostics_reference=diagnostics_report.deterministic_report_hash,
        integrity_reference=integrity_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def determine_operational_continuity_status(findings: tuple[OperationalContinuityFinding, ...]) -> str:
    severities = {finding.severity for finding in findings}
    if CONTINUITY_SEVERITY_CRITICAL in severities:
        return CONTINUITY_STATUS_BROKEN
    if CONTINUITY_SEVERITY_BLOCKING in severities:
        return CONTINUITY_STATUS_BLOCKED
    if CONTINUITY_SEVERITY_PROHIBITED in severities:
        return CONTINUITY_STATUS_PROHIBITED
    if CONTINUITY_SEVERITY_UNKNOWN in severities:
        return CONTINUITY_STATUS_UNKNOWN
    if CONTINUITY_SEVERITY_WARNING in severities:
        return CONTINUITY_STATUS_WARNING
    return CONTINUITY_STATUS_CERTIFIED


def order_operational_continuity_findings(
    findings: Iterable[OperationalContinuityFinding],
) -> tuple[OperationalContinuityFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def _build_boolean_finding(
    finding_type: str,
    source_phase: str,
    preserved: bool,
    label: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
    *,
    fail_severity: str = CONTINUITY_SEVERITY_BLOCKING,
) -> OperationalContinuityFinding:
    return build_operational_continuity_finding(
        finding_type=finding_type,
        severity=CONTINUITY_SEVERITY_INFO if preserved else fail_severity,
        source_phase=source_phase,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        integrity_report=integrity_report,
        explanation=f"{label}={preserved}.",
    )


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> str:
    references = tuple(sorted(record.provenance_reference_id for record in lifecycle_foundation.provenance_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
            f"recovery:{recovery_report.deterministic_report_hash}",
            f"diagnostics:{diagnostics_report.deterministic_report_hash}",
            f"integrity:{integrity_report.deterministic_report_hash}",
        )
    )


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> str:
    references = tuple(sorted(record.lineage_reference_id for record in lifecycle_foundation.lineage_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
            f"production_consumption:{production_consumption_report.deterministic_report_hash}",
            f"recovery:{recovery_report.deterministic_report_hash}",
            f"diagnostics:{diagnostics_report.deterministic_report_hash}",
            f"integrity:{integrity_report.deterministic_report_hash}",
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
    return "|".join(references) if references else f"{token}_continuity_certification_reference_not_visible"


def _provenance_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "provenance_safe", True)) for report in reports)


def _lineage_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "lineage_safe", True)) for report in reports)


def _replay_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "replay_safe", True)) for report in reports)


def _rollback_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "rollback_safe", True)) for report in reports)


def _serialization_stable(*args: object) -> bool:
    first = _serialized_inputs(*args)
    second = _serialized_inputs(*args)
    return first == second and all(bool(value) for value in first)


def _serialized_inputs(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> tuple[str, ...]:
    return (
        serialize_patch_lifecycle_foundation(lifecycle_foundation),
        serialize_lifecycle_drift_report(drift_report),
        serialize_trusted_bundle_governance_report(governance_report),
        serialize_operational_validation_report(validation_report),
        serialize_production_consumption_governance_report(production_consumption_report),
        serialize_recovery_certification_report(recovery_report),
        serialize_operational_diagnostics_report(diagnostics_report),
        serialize_operational_integrity_report(integrity_report),
    )


def _hashing_stable(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> bool:
    lifecycle_hash = hash_patch_lifecycle_foundation(lifecycle_foundation)
    return all(
        (
            lifecycle_hash == hash_patch_lifecycle_foundation(lifecycle_foundation),
            hash_lifecycle_drift_report(drift_report) == drift_report.deterministic_report_hash,
            hash_trusted_bundle_governance_report(governance_report) == governance_report.deterministic_report_hash,
            hash_operational_validation_report(validation_report) == validation_report.deterministic_report_hash,
            hash_production_consumption_governance_report(production_consumption_report)
            == production_consumption_report.deterministic_report_hash,
            hash_recovery_certification_report(recovery_report) == recovery_report.deterministic_report_hash,
            hash_operational_diagnostics_report(diagnostics_report) == diagnostics_report.deterministic_report_hash,
            hash_operational_integrity_report(integrity_report) == integrity_report.deterministic_report_hash,
        )
    )


def _visibility_preserved(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> bool:
    return all(
        bool(result["valid"])
        for result in (
            validate_lifecycle_visibility(lifecycle_foundation),
            validate_lifecycle_drift_visibility(drift_report),
            validate_trusted_bundle_governance_visibility(governance_report),
            validate_operational_validation_visibility(validation_report),
            validate_production_consumption_visibility(production_consumption_report),
            validate_recovery_certification_visibility(recovery_report),
            validate_operational_diagnostics_visibility(diagnostics_report),
            validate_operational_integrity_visibility(integrity_report),
        )
    )


def _integrity_preserved(report: OperationalIntegrityReport) -> bool:
    leakage_values = (
        report.execution_leakage_detected,
        report.orchestration_leakage_detected,
        report.remediation_leakage_detected,
        report.recommendation_leakage_detected,
        report.ranking_leakage_detected,
        report.scoring_leakage_detected,
        report.selection_leakage_detected,
        report.approval_leakage_detected,
        report.authorization_leakage_detected,
        report.mutation_leakage_detected,
        report.production_consumption_leakage_detected,
        report.planner_integration_leakage_detected,
    )
    return report.integrity_enforcement_performed and report.violation_count == 0 and not any(leakage_values)


def _prohibited_total(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> int:
    lifecycle_count = sum(1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_PROHIBITED)
    return (
        lifecycle_count
        + drift_report.prohibited_drift_count
        + governance_report.prohibited_count
        + validation_report.prohibited_count
        + production_consumption_report.prohibited_gate_count
        + recovery_report.prohibited_count
        + diagnostics_report.prohibited_count
        + integrity_report.prohibited_count
    )


def _unknown_total(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
) -> int:
    lifecycle_count = sum(1 for state in lifecycle_foundation.lifecycle_states if state.state == LIFECYCLE_STATE_UNKNOWN)
    return (
        lifecycle_count
        + drift_report.unknown_drift_count
        + governance_report.unknown_count
        + validation_report.unknown_count
        + production_consumption_report.unknown_gate_count
        + recovery_report.unknown_count
        + diagnostics_report.unknown_count
        + integrity_report.unknown_count
    )


def _non_execution_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _EXECUTION_FIELDS) for report in reports)


def _non_remediation_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _REMEDIATION_FIELDS) for report in reports)


def _non_authorization_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _AUTHORIZATION_FIELDS) for report in reports)


def _production_consumption_disabled(*reports: object) -> bool:
    return not any(_any_truthy(report, _PRODUCTION_CONSUMPTION_FIELDS) for report in reports)


def _truthy(source: object, field_name: str) -> bool:
    return bool(getattr(source, field_name, False))


def _any_truthy(source: object, field_names: tuple[str, ...]) -> bool:
    return any(_truthy(source, field_name) for field_name in field_names)


_EXECUTION_FIELDS = (
    "lifecycle_execution_enabled",
    "patch_execution_enabled",
    "patch_application_enabled",
    "deployment_execution_enabled",
    "execution_enabled",
    "deployment_enabled",
    "operational_execution_authorized",
    "recovery_execution_authorized",
    "rollback_execution_authorized",
    "execution_authorized",
)
_REMEDIATION_FIELDS = (
    "remediation_enabled",
    "remediation_authorized",
    "correction_enabled",
    "repair_enabled",
    "automatic_resolution_enabled",
    "corrective_behavior_enabled",
)
_AUTHORIZATION_FIELDS = (
    "approval_enabled",
    "authorization_enabled",
    "operational_execution_authorized",
    "production_consumption_authorized",
    "recovery_execution_authorized",
    "rollback_execution_authorized",
    "execution_authorized",
)
_PRODUCTION_CONSUMPTION_FIELDS = (
    "production_consumption_authorized",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
)
