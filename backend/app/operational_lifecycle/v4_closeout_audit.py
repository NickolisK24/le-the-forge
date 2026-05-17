"""Deterministic v4.0 closeout and v4.1 readiness audit.

The audit certifies the completed v4.0 operational lifecycle governance chain.
It never authorizes execution, remediation, production consumption,
orchestration, planner integration, approval, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_hashing import hash_trusted_bundle_governance_report
from .bundle_governance_models import TrustedBundleGovernanceReport
from .bundle_governance_serialization import serialize_trusted_bundle_governance_report
from .bundle_governance_visibility import validate_trusted_bundle_governance_visibility
from .continuity_certification_hashing import hash_operational_continuity_certification_report
from .continuity_certification_models import OperationalContinuityCertificationReport
from .continuity_certification_serialization import serialize_operational_continuity_certification_report
from .continuity_certification_visibility import validate_operational_continuity_visibility
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
from .lifecycle_models import LIFECYCLE_STATE_PROHIBITED, LIFECYCLE_STATE_UNKNOWN, PatchLifecycleFoundation
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
from .v4_closeout_hashing import hash_v4_closeout_report
from .v4_closeout_models import (
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
    CLOSEOUT_SEVERITY_BLOCKING,
    CLOSEOUT_SEVERITY_CRITICAL,
    CLOSEOUT_SEVERITY_INFO,
    CLOSEOUT_SEVERITY_PROHIBITED,
    CLOSEOUT_SEVERITY_UNKNOWN,
    CLOSEOUT_SEVERITY_WARNING,
    CLOSEOUT_STATUS_BLOCKED,
    CLOSEOUT_STATUS_CLOSED_OUT,
    CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS,
    CLOSEOUT_STATUS_PROHIBITED,
    CLOSEOUT_STATUS_UNKNOWN,
    V41_READINESS_BLOCKED,
    V41_READINESS_NOT_READY,
    V41_READINESS_PROHIBITED,
    V41_READINESS_READY,
    V41_READINESS_READY_WITH_WARNINGS,
    V41_READINESS_UNKNOWN,
    V4CloseoutFinding,
    V4CloseoutReport,
)
from .v4_closeout_visibility import (
    blocked_v4_closeout_count,
    critical_v4_closeout_count,
    prohibited_v4_closeout_count,
    unknown_v4_closeout_count,
    warning_v4_closeout_count,
)
from .validation_automation_hashing import hash_operational_validation_report
from .validation_automation_models import OperationalValidationReport
from .validation_automation_serialization import serialize_operational_validation_report
from .validation_automation_visibility import validate_operational_validation_visibility


def audit_v4_closeout_and_v4_1_readiness(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
    continuity_report: OperationalContinuityCertificationReport,
) -> V4CloseoutReport:
    findings = order_v4_closeout_findings(
        (
            audit_lifecycle_closeout(*_args(locals())),
            audit_drift_closeout(*_args(locals())),
            audit_bundle_governance_closeout(*_args(locals())),
            audit_validation_closeout(*_args(locals())),
            audit_production_consumption_closeout(*_args(locals())),
            audit_recovery_closeout(*_args(locals())),
            audit_diagnostics_closeout(*_args(locals())),
            audit_integrity_closeout(*_args(locals())),
            audit_continuity_closeout(*_args(locals())),
            audit_provenance_closeout(*_args(locals())),
            audit_lineage_closeout(*_args(locals())),
            audit_replay_closeout(*_args(locals())),
            audit_rollback_closeout(*_args(locals())),
            audit_serialization_stability(*_args(locals())),
            audit_hashing_stability(*_args(locals())),
            audit_visibility_preservation(*_args(locals())),
            audit_non_execution(*_args(locals())),
            audit_non_remediation(*_args(locals())),
            audit_non_authorization(*_args(locals())),
            audit_production_consumption_disabled(*_args(locals())),
            audit_orchestration_disabled(*_args(locals())),
            audit_planner_integration_disabled(*_args(locals())),
            audit_v4_1_readiness(*_args(locals())),
            audit_prohibited_state_visibility(*_args(locals())),
            audit_unknown_state_visibility(*_args(locals())),
            audit_warning_visibility(*_args(locals())),
        )
    )
    report = V4CloseoutReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        production_consumption_report_hash=production_consumption_report.deterministic_report_hash,
        recovery_report_hash=recovery_report.deterministic_report_hash,
        diagnostics_report_hash=diagnostics_report.deterministic_report_hash,
        integrity_report_hash=integrity_report.deterministic_report_hash,
        continuity_report_hash=continuity_report.deterministic_report_hash,
        closeout_status=determine_v4_closeout_status(findings),
        v4_1_readiness_status=determine_v4_1_readiness_status(findings),
        finding_count=len(findings),
        findings=findings,
        warning_count=warning_v4_closeout_count(findings),
        blocked_count=blocked_v4_closeout_count(findings),
        prohibited_count=prohibited_v4_closeout_count(findings),
        unknown_count=unknown_v4_closeout_count(findings),
        critical_count=critical_v4_closeout_count(findings),
        replay_safe=_replay_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
            continuity_report,
        ),
        rollback_safe=_rollback_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
            continuity_report,
        ),
        provenance_safe=_provenance_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
            continuity_report,
        ),
        lineage_safe=_lineage_safe(
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
            integrity_report,
            continuity_report,
        ),
        serialization_stable=_serialization_stable(*_args(locals())),
        hashing_stable=_hashing_stable(*_args(locals())),
        visibility_preserved=_visibility_preserved(*_args(locals())),
        integrity_preserved=_integrity_preserved(integrity_report),
        continuity_preserved=_continuity_preserved(continuity_report),
        execution_authorized=False,
        remediation_authorized=False,
        production_consumption_enabled=False,
        orchestration_enabled=False,
        planner_integration_enabled=False,
        deterministic_report_hash="pending",
    )
    return replace(report, deterministic_report_hash=hash_v4_closeout_report(report))


def audit_lifecycle_closeout(*args: object) -> V4CloseoutFinding:
    lifecycle_foundation = args[0]
    visible = bool(lifecycle_identity_key(lifecycle_foundation.patch_identity))
    return _build_boolean_finding(CLOSEOUT_FINDING_LIFECYCLE, "v4_0_phase_1", visible, "lifecycle_closeout_preserved", *args)


def audit_drift_closeout(*args: object) -> V4CloseoutFinding:
    drift_report = args[1]
    return _build_boolean_finding(
        CLOSEOUT_FINDING_DRIFT,
        "v4_0_phase_2",
        bool(drift_report.deterministic_report_hash),
        "drift_closeout_preserved",
        *args,
    )


def audit_bundle_governance_closeout(*args: object) -> V4CloseoutFinding:
    governance_report = args[2]
    return _build_boolean_finding(
        CLOSEOUT_FINDING_BUNDLE_GOVERNANCE,
        "v4_0_phase_3",
        bool(governance_report.deterministic_report_hash),
        "bundle_governance_closeout_preserved",
        *args,
    )


def audit_validation_closeout(*args: object) -> V4CloseoutFinding:
    validation_report = args[3]
    return _build_boolean_finding(
        CLOSEOUT_FINDING_VALIDATION,
        "v4_0_phase_4",
        bool(validation_report.deterministic_report_hash),
        "validation_closeout_preserved",
        *args,
    )


def audit_production_consumption_closeout(*args: object) -> V4CloseoutFinding:
    production_consumption_report = args[4]
    preserved = bool(production_consumption_report.deterministic_report_hash) and not production_consumption_report.production_consumption_enabled
    return _build_boolean_finding(
        CLOSEOUT_FINDING_PRODUCTION_CONSUMPTION,
        "v4_0_phase_5",
        preserved,
        "production_consumption_closeout_preserved",
        *args,
    )


def audit_recovery_closeout(*args: object) -> V4CloseoutFinding:
    recovery_report = args[5]
    preserved = (
        bool(recovery_report.deterministic_report_hash)
        and not recovery_report.recovery_execution_authorized
        and not recovery_report.rollback_execution_authorized
    )
    return _build_boolean_finding(CLOSEOUT_FINDING_RECOVERY, "v4_0_phase_6", preserved, "recovery_closeout_preserved", *args)


def audit_diagnostics_closeout(*args: object) -> V4CloseoutFinding:
    diagnostics_report = args[6]
    preserved = bool(diagnostics_report.deterministic_report_hash) and not diagnostics_report.recommendations_present
    return _build_boolean_finding(CLOSEOUT_FINDING_DIAGNOSTICS, "v4_0_phase_7", preserved, "diagnostics_preserved", *args)


def audit_integrity_closeout(*args: object) -> V4CloseoutFinding:
    integrity_report = args[7]
    return _build_boolean_finding(
        CLOSEOUT_FINDING_INTEGRITY,
        "v4_0_phase_8",
        _integrity_preserved(integrity_report),
        "integrity_preserved",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_continuity_closeout(*args: object) -> V4CloseoutFinding:
    continuity_report = args[8]
    return _build_boolean_finding(
        CLOSEOUT_FINDING_CONTINUITY,
        "v4_0_phase_9",
        _continuity_preserved(continuity_report),
        "continuity_preserved",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_provenance_closeout(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_PROVENANCE, "v4_0_phase_1_to_9", _provenance_safe(*args[1:]), "provenance_safe", *args)


def audit_lineage_closeout(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_LINEAGE, "v4_0_phase_1_to_9", _lineage_safe(*args[2:]), "lineage_safe", *args)


def audit_replay_closeout(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_REPLAY, "v4_0_phase_1_to_9", _replay_safe(*args[1:]), "replay_safe", *args)


def audit_rollback_closeout(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_ROLLBACK, "v4_0_phase_1_to_9", _rollback_safe(*args[1:]), "rollback_safe", *args)


def audit_serialization_stability(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_SERIALIZATION, "v4_0_phase_1_to_9", _serialization_stable(*args), "serialization_stable", *args)


def audit_hashing_stability(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_HASHING,
        "v4_0_phase_1_to_9",
        _hashing_stable(*args),
        "hashing_stable",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_visibility_preservation(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(CLOSEOUT_FINDING_VISIBILITY, "v4_0_phase_1_to_9", _visibility_preserved(*args), "visibility_preserved", *args)


def audit_non_execution(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_NON_EXECUTION,
        "v4_0_phase_1_to_9",
        _non_execution_preserved(*args),
        "execution_authorized=False",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_non_remediation(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_NON_REMEDIATION,
        "v4_0_phase_1_to_9",
        _non_remediation_preserved(*args),
        "remediation_authorized=False",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_non_authorization(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_NON_AUTHORIZATION,
        "v4_0_phase_1_to_9",
        _non_authorization_preserved(*args),
        "authorization_absent",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_production_consumption_disabled(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_PRODUCTION_DISABLED,
        "v4_0_phase_3_to_9",
        _production_consumption_disabled(*args),
        "production_consumption_enabled=False",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_orchestration_disabled(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_ORCHESTRATION_DISABLED,
        "v4_0_phase_1_to_9",
        _orchestration_disabled(*args),
        "orchestration_enabled=False",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_planner_integration_disabled(*args: object) -> V4CloseoutFinding:
    return _build_boolean_finding(
        CLOSEOUT_FINDING_PLANNER_DISABLED,
        "v4_0_phase_1_to_9",
        _planner_integration_disabled(*args),
        "planner_integration_enabled=False",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_CRITICAL,
    )


def audit_v4_1_readiness(*args: object) -> V4CloseoutFinding:
    ready = all(
        (
            _provenance_safe(*args[1:]),
            _lineage_safe(*args[2:]),
            _replay_safe(*args[1:]),
            _rollback_safe(*args[1:]),
            _serialization_stable(*args),
            _hashing_stable(*args),
            _visibility_preserved(*args),
            _integrity_preserved(args[7]),
            _continuity_preserved(args[8]),
            _non_execution_preserved(*args),
            _non_remediation_preserved(*args),
            _non_authorization_preserved(*args),
            _production_consumption_disabled(*args),
            _orchestration_disabled(*args),
            _planner_integration_disabled(*args),
        )
    )
    return _build_boolean_finding(
        CLOSEOUT_FINDING_V41_READINESS,
        "v4_0_phase_10",
        ready,
        "ready_for_v4_1_planning_only",
        *args,
        fail_severity=CLOSEOUT_SEVERITY_BLOCKING,
    )


def audit_prohibited_state_visibility(*args: object) -> V4CloseoutFinding:
    total = _prohibited_total(*args)
    return build_v4_closeout_finding(
        finding_type=CLOSEOUT_FINDING_PROHIBITED_VISIBILITY,
        severity=CLOSEOUT_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_9",
        lifecycle_foundation=args[0],
        drift_report=args[1],
        governance_report=args[2],
        validation_report=args[3],
        production_consumption_report=args[4],
        recovery_report=args[5],
        diagnostics_report=args[6],
        integrity_report=args[7],
        continuity_report=args[8],
        explanation=f"prohibited_state_visibility_preserved=True; prohibited_evidence_count={total}.",
    )


def audit_unknown_state_visibility(*args: object) -> V4CloseoutFinding:
    total = _unknown_total(*args)
    return build_v4_closeout_finding(
        finding_type=CLOSEOUT_FINDING_UNKNOWN_VISIBILITY,
        severity=CLOSEOUT_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_9",
        lifecycle_foundation=args[0],
        drift_report=args[1],
        governance_report=args[2],
        validation_report=args[3],
        production_consumption_report=args[4],
        recovery_report=args[5],
        diagnostics_report=args[6],
        integrity_report=args[7],
        continuity_report=args[8],
        explanation=f"unknown_state_visibility_preserved=True; unknown_evidence_count={total}.",
    )


def audit_warning_visibility(*args: object) -> V4CloseoutFinding:
    total = _warning_total(*args)
    return build_v4_closeout_finding(
        finding_type=CLOSEOUT_FINDING_WARNING_VISIBILITY,
        severity=CLOSEOUT_SEVERITY_WARNING,
        source_phase="v4_0_phase_1_to_9",
        lifecycle_foundation=args[0],
        drift_report=args[1],
        governance_report=args[2],
        validation_report=args[3],
        production_consumption_report=args[4],
        recovery_report=args[5],
        diagnostics_report=args[6],
        integrity_report=args[7],
        continuity_report=args[8],
        explanation=f"warning_visibility_preserved=True; warning_evidence_count={total}.",
    )


def build_v4_closeout_finding(
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
    continuity_report: OperationalContinuityCertificationReport,
    explanation: str,
) -> V4CloseoutFinding:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
        integrity_report,
        continuity_report,
    )
    lineage_reference = _lineage_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
        integrity_report,
        continuity_report,
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
            "continuity_reference": continuity_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "explanation": explanation,
        }
    )
    return V4CloseoutFinding(
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
        continuity_reference=continuity_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def determine_v4_closeout_status(findings: tuple[V4CloseoutFinding, ...]) -> str:
    severities = {finding.severity for finding in findings}
    if CLOSEOUT_SEVERITY_CRITICAL in severities or CLOSEOUT_SEVERITY_BLOCKING in severities:
        return CLOSEOUT_STATUS_BLOCKED
    if CLOSEOUT_SEVERITY_PROHIBITED in severities:
        return CLOSEOUT_STATUS_PROHIBITED
    if CLOSEOUT_SEVERITY_UNKNOWN in severities:
        return CLOSEOUT_STATUS_UNKNOWN
    if CLOSEOUT_SEVERITY_WARNING in severities:
        return CLOSEOUT_STATUS_CLOSED_OUT_WITH_WARNINGS
    return CLOSEOUT_STATUS_CLOSED_OUT


def determine_v4_1_readiness_status(findings: tuple[V4CloseoutFinding, ...]) -> str:
    severities = {finding.severity for finding in findings}
    if CLOSEOUT_SEVERITY_CRITICAL in severities:
        return V41_READINESS_NOT_READY
    if CLOSEOUT_SEVERITY_BLOCKING in severities:
        return V41_READINESS_BLOCKED
    if CLOSEOUT_SEVERITY_PROHIBITED in severities:
        return V41_READINESS_PROHIBITED
    if CLOSEOUT_SEVERITY_UNKNOWN in severities:
        return V41_READINESS_UNKNOWN
    if CLOSEOUT_SEVERITY_WARNING in severities:
        return V41_READINESS_READY_WITH_WARNINGS
    return V41_READINESS_READY


def order_v4_closeout_findings(findings: Iterable[V4CloseoutFinding]) -> tuple[V4CloseoutFinding, ...]:
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
    continuity_report: OperationalContinuityCertificationReport,
    *,
    fail_severity: str = CLOSEOUT_SEVERITY_BLOCKING,
) -> V4CloseoutFinding:
    return build_v4_closeout_finding(
        finding_type=finding_type,
        severity=CLOSEOUT_SEVERITY_INFO if preserved else fail_severity,
        source_phase=source_phase,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        integrity_report=integrity_report,
        continuity_report=continuity_report,
        explanation=f"{label}={preserved}.",
    )


def _args(local_values: dict[str, object]) -> tuple[object, ...]:
    return (
        local_values["lifecycle_foundation"],
        local_values["drift_report"],
        local_values["governance_report"],
        local_values["validation_report"],
        local_values["production_consumption_report"],
        local_values["recovery_report"],
        local_values["diagnostics_report"],
        local_values["integrity_report"],
        local_values["continuity_report"],
    )


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
    continuity_report: OperationalContinuityCertificationReport,
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
            f"continuity:{continuity_report.deterministic_report_hash}",
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
    continuity_report: OperationalContinuityCertificationReport,
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
            f"continuity:{continuity_report.deterministic_report_hash}",
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
    return "|".join(references) if references else f"{token}_v4_closeout_reference_not_visible"


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
    continuity_report: OperationalContinuityCertificationReport,
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
        serialize_operational_continuity_certification_report(continuity_report),
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
    continuity_report: OperationalContinuityCertificationReport,
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
            hash_operational_continuity_certification_report(continuity_report)
            == continuity_report.deterministic_report_hash,
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
    continuity_report: OperationalContinuityCertificationReport,
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
            validate_operational_continuity_visibility(continuity_report),
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


def _continuity_preserved(report: OperationalContinuityCertificationReport) -> bool:
    return all(
        (
            report.broken_count == 0,
            report.blocked_count == 0,
            report.critical_count == 0,
            report.replay_safe,
            report.rollback_safe,
            report.provenance_safe,
            report.lineage_safe,
            report.serialization_stable,
            report.hashing_stable,
            report.visibility_preserved,
            report.integrity_preserved,
            not report.execution_authorized,
            not report.remediation_authorized,
            not report.production_consumption_enabled,
        )
    )


def _prohibited_total(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    integrity_report: OperationalIntegrityReport,
    continuity_report: OperationalContinuityCertificationReport,
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
        + continuity_report.prohibited_count
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
    continuity_report: OperationalContinuityCertificationReport,
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
        + continuity_report.unknown_count
    )


def _warning_total(*reports: object) -> int:
    return sum(int(getattr(report, "warning_count", 0)) for report in reports[1:])


def _non_execution_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _EXECUTION_FIELDS) for report in reports)


def _non_remediation_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _REMEDIATION_FIELDS) for report in reports)


def _non_authorization_preserved(*reports: object) -> bool:
    return not any(_any_truthy(report, _AUTHORIZATION_FIELDS) for report in reports)


def _production_consumption_disabled(*reports: object) -> bool:
    return not any(_any_truthy(report, _PRODUCTION_CONSUMPTION_FIELDS) for report in reports)


def _orchestration_disabled(*reports: object) -> bool:
    return not any(_any_truthy(report, _ORCHESTRATION_FIELDS) for report in reports)


def _planner_integration_disabled(*reports: object) -> bool:
    return not any(_any_truthy(report, _PLANNER_FIELDS) for report in reports)


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
_ORCHESTRATION_FIELDS = ("orchestration_enabled", "orchestration_execution_enabled")
_PLANNER_FIELDS = ("planner_integration_enabled", "planner_behavior_changed", "planner_integration_leakage_detected")
