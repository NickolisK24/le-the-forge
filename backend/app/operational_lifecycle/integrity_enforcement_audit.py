"""Deterministic operational lifecycle integrity enforcement audit.

The audit detects prohibited behavior leakage across v4.0 Phase 1-7 evidence.
It never fixes violations, remediates gaps, suppresses findings, authorizes
behavior, executes behavior, or mutates source reports.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .bundle_governance_models import TrustedBundleGovernanceReport
from .diagnostics_models import OPERATIONAL_DIAGNOSTIC_CATEGORIES, OperationalDiagnosticsReport
from .integrity_enforcement_hashing import hash_operational_integrity_report
from .integrity_enforcement_models import (
    INTEGRITY_FINDING_APPROVAL_LEAKAGE,
    INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE,
    INTEGRITY_FINDING_BOUNDARY,
    INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION,
    INTEGRITY_FINDING_EVIDENCE_CONTINUITY,
    INTEGRITY_FINDING_EXECUTION_LEAKAGE,
    INTEGRITY_FINDING_FALLBACK_LEAKAGE,
    INTEGRITY_FINDING_LINEAGE_CONTINUITY,
    INTEGRITY_FINDING_MUTATION_LEAKAGE,
    INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE,
    INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE,
    INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE,
    INTEGRITY_FINDING_PROHIBITED_STATE,
    INTEGRITY_FINDING_PROVENANCE_CONTINUITY,
    INTEGRITY_FINDING_RANKING_LEAKAGE,
    INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE,
    INTEGRITY_FINDING_REMEDIATION_LEAKAGE,
    INTEGRITY_FINDING_REPLAY_CONTINUITY,
    INTEGRITY_FINDING_ROLLBACK_CONTINUITY,
    INTEGRITY_FINDING_SCORING_LEAKAGE,
    INTEGRITY_FINDING_SELECTION_LEAKAGE,
    INTEGRITY_SEVERITY_BLOCKING,
    INTEGRITY_SEVERITY_CRITICAL,
    INTEGRITY_SEVERITY_INFO,
    INTEGRITY_SEVERITY_PROHIBITED,
    INTEGRITY_SEVERITY_UNKNOWN,
    INTEGRITY_SEVERITY_WARNING,
    INTEGRITY_STATUS_BLOCKED,
    INTEGRITY_STATUS_PRESERVED,
    INTEGRITY_STATUS_PROHIBITED,
    INTEGRITY_STATUS_UNKNOWN,
    INTEGRITY_STATUS_VIOLATION,
    INTEGRITY_STATUS_WARNING,
    OperationalIntegrityFinding,
    OperationalIntegrityReport,
)
from .integrity_enforcement_visibility import (
    blocked_integrity_count,
    critical_integrity_count,
    prohibited_integrity_count,
    unknown_integrity_count,
    violation_integrity_count,
    warning_integrity_count,
)
from .lifecycle_drift_models import LifecycleDriftReport
from .lifecycle_identity import lifecycle_identity_key
from .lifecycle_models import PatchLifecycleFoundation
from .lifecycle_serialization import stable_serialize
from .production_consumption_models import ProductionConsumptionGovernanceReport
from .recovery_certification_models import RecoveryCertificationReport
from .validation_automation_models import OperationalValidationReport


def audit_operational_lifecycle_integrity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityReport:
    leakage = build_integrity_leakage_summary(
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )
    findings = order_operational_integrity_findings(
        (
            audit_execution_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_orchestration_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_remediation_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_recommendation_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_ranking_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_scoring_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_selection_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_approval_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_authorization_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_mutation_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_production_consumption_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_planner_integration_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_fallback_leakage(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
                leakage,
            ),
            audit_diagnostic_suppression(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_evidence_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_provenance_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_lineage_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_replay_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_rollback_continuity(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_prohibited_state(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
            audit_integrity_enforcement_boundary(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
                production_consumption_report,
                recovery_report,
                diagnostics_report,
            ),
        )
    )
    placeholder = OperationalIntegrityReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        production_consumption_report_hash=production_consumption_report.deterministic_report_hash,
        recovery_report_hash=recovery_report.deterministic_report_hash,
        diagnostics_report_hash=diagnostics_report.deterministic_report_hash,
        integrity_status=determine_operational_integrity_status(findings, leakage),
        finding_count=len(findings),
        findings=findings,
        violation_count=0,
        warning_count=warning_integrity_count(findings),
        blocked_count=blocked_integrity_count(findings),
        prohibited_count=prohibited_integrity_count(findings),
        unknown_count=unknown_integrity_count(findings),
        critical_count=critical_integrity_count(findings),
        replay_safe=_replay_safe(drift_report, governance_report, validation_report, production_consumption_report, recovery_report, diagnostics_report),
        rollback_safe=_rollback_safe(drift_report, governance_report, validation_report, production_consumption_report, recovery_report, diagnostics_report),
        provenance_safe=_provenance_safe(drift_report, governance_report, validation_report, production_consumption_report, recovery_report, diagnostics_report),
        lineage_safe=_lineage_safe(governance_report, validation_report, production_consumption_report, recovery_report, diagnostics_report),
        execution_leakage_detected=leakage["execution"],
        orchestration_leakage_detected=leakage["orchestration"],
        remediation_leakage_detected=leakage["remediation"],
        recommendation_leakage_detected=leakage["recommendation"],
        ranking_leakage_detected=leakage["ranking"],
        scoring_leakage_detected=leakage["scoring"],
        selection_leakage_detected=leakage["selection"],
        approval_leakage_detected=leakage["approval"],
        authorization_leakage_detected=leakage["authorization"],
        mutation_leakage_detected=leakage["mutation"],
        production_consumption_leakage_detected=leakage["production_consumption"],
        planner_integration_leakage_detected=leakage["planner_integration"],
        integrity_enforcement_performed=True,
        deterministic_report_hash="pending",
    )
    placeholder = replace(placeholder, violation_count=violation_integrity_count(placeholder))
    return replace(placeholder, deterministic_report_hash=hash_operational_integrity_report(placeholder))


def build_integrity_leakage_summary(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> dict[str, bool]:
    reports = (
        lifecycle_foundation,
        drift_report,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )
    return {
        "execution": any(_any_truthy(report, _EXECUTION_FIELDS) for report in reports),
        "orchestration": any(_truthy(report, "orchestration_execution_enabled") for report in reports),
        "remediation": any(_any_truthy(report, _REMEDIATION_FIELDS) for report in reports),
        "recommendation": any(_any_truthy(report, _RECOMMENDATION_FIELDS) for report in reports),
        "ranking": any(_truthy(report, "ranking_enabled") for report in reports),
        "scoring": any(_truthy(report, "scoring_enabled") for report in reports),
        "selection": any(_truthy(report, "selection_enabled") for report in reports),
        "approval": any(_truthy(report, "approval_enabled") for report in reports),
        "authorization": any(_any_truthy(report, _AUTHORIZATION_FIELDS) for report in reports),
        "mutation": any(_any_truthy(report, _MUTATION_FIELDS) for report in reports),
        "production_consumption": any(_any_truthy(report, _PRODUCTION_CONSUMPTION_FIELDS) for report in reports),
        "planner_integration": any(_any_truthy(report, _PLANNER_FIELDS) for report in reports),
        "fallback": _hidden_fallback_count(lifecycle_foundation, diagnostics_report) > 0,
    }


def audit_execution_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_EXECUTION_LEAKAGE, "v4_0_phase_1_to_7", "execution", *args)


def audit_orchestration_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_ORCHESTRATION_LEAKAGE, "v4_0_phase_1_to_7", "orchestration", *args)


def audit_remediation_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_REMEDIATION_LEAKAGE, "v4_0_phase_1_to_7", "remediation", *args)


def audit_recommendation_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_RECOMMENDATION_LEAKAGE, "v4_0_phase_1_and_7", "recommendation", *args)


def audit_ranking_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_RANKING_LEAKAGE, "v4_0_phase_1_and_7", "ranking", *args)


def audit_scoring_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_SCORING_LEAKAGE, "v4_0_phase_1_and_7", "scoring", *args)


def audit_selection_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_SELECTION_LEAKAGE, "v4_0_phase_1_and_7", "selection", *args)


def audit_approval_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_APPROVAL_LEAKAGE, "v4_0_phase_1_to_7", "approval", *args)


def audit_authorization_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_AUTHORIZATION_LEAKAGE, "v4_0_phase_1_to_7", "authorization", *args)


def audit_mutation_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(INTEGRITY_FINDING_MUTATION_LEAKAGE, "v4_0_phase_1_to_7", "mutation", *args)


def audit_production_consumption_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(
        INTEGRITY_FINDING_PRODUCTION_CONSUMPTION_LEAKAGE,
        "v4_0_phase_3_to_7",
        "production_consumption",
        *args,
    )


def audit_planner_integration_leakage(*args: object) -> OperationalIntegrityFinding:
    return _build_leakage_finding(
        INTEGRITY_FINDING_PLANNER_INTEGRATION_LEAKAGE,
        "v4_0_phase_5",
        "planner_integration",
        *args,
    )


def audit_fallback_leakage(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    leakage: dict[str, bool],
) -> OperationalIntegrityFinding:
    detected = leakage["fallback"]
    count = _hidden_fallback_count(lifecycle_foundation, diagnostics_report)
    return build_operational_integrity_finding(
        finding_type=INTEGRITY_FINDING_FALLBACK_LEAKAGE,
        severity=INTEGRITY_SEVERITY_CRITICAL if detected else INTEGRITY_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_7",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=f"Fallback leakage audit observed hidden_fallback_signal_count={count}.",
    )


def audit_diagnostic_suppression(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityFinding:
    hidden_count = sum(1 for entry in diagnostics_report.entries if entry.hidden)
    missing_categories = tuple(
        category for category in OPERATIONAL_DIAGNOSTIC_CATEGORIES if diagnostics_report.category_counts.get(category, 0) == 0
    )
    suppressed = hidden_count > 0 or bool(missing_categories)
    return build_operational_integrity_finding(
        finding_type=INTEGRITY_FINDING_DIAGNOSTIC_SUPPRESSION,
        severity=INTEGRITY_SEVERITY_CRITICAL if suppressed else INTEGRITY_SEVERITY_INFO,
        source_phase="v4_0_phase_7",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=(
            "Diagnostic suppression audit observed "
            f"hidden_entry_count={hidden_count} and missing_category_count={len(missing_categories)}."
        ),
    )


def audit_evidence_continuity(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityFinding:
    references = (
        lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report.deterministic_report_hash,
        governance_report.deterministic_report_hash,
        validation_report.deterministic_report_hash,
        production_consumption_report.deterministic_report_hash,
        recovery_report.deterministic_report_hash,
        diagnostics_report.deterministic_report_hash,
    )
    visible = all(bool(reference) for reference in references)
    return build_operational_integrity_finding(
        finding_type=INTEGRITY_FINDING_EVIDENCE_CONTINUITY,
        severity=INTEGRITY_SEVERITY_INFO if visible else INTEGRITY_SEVERITY_BLOCKING,
        source_phase="v4_0_phase_1_to_7",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=f"Evidence continuity audit observed visible_reference_count={sum(1 for ref in references if ref)}.",
    )


def audit_provenance_continuity(*args: object) -> OperationalIntegrityFinding:
    return _build_safety_finding(INTEGRITY_FINDING_PROVENANCE_CONTINUITY, "v4_0_phase_1_to_7", "provenance", *args)


def audit_lineage_continuity(*args: object) -> OperationalIntegrityFinding:
    return _build_safety_finding(INTEGRITY_FINDING_LINEAGE_CONTINUITY, "v4_0_phase_1_to_7", "lineage", *args)


def audit_replay_continuity(*args: object) -> OperationalIntegrityFinding:
    return _build_safety_finding(INTEGRITY_FINDING_REPLAY_CONTINUITY, "v4_0_phase_1_to_7", "replay", *args)


def audit_rollback_continuity(*args: object) -> OperationalIntegrityFinding:
    return _build_safety_finding(INTEGRITY_FINDING_ROLLBACK_CONTINUITY, "v4_0_phase_1_to_7", "rollback", *args)


def audit_prohibited_state(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityFinding:
    prohibited_total = (
        drift_report.prohibited_drift_count
        + governance_report.prohibited_count
        + validation_report.prohibited_count
        + production_consumption_report.prohibited_gate_count
        + recovery_report.prohibited_count
        + diagnostics_report.prohibited_count
    )
    return build_operational_integrity_finding(
        finding_type=INTEGRITY_FINDING_PROHIBITED_STATE,
        severity=INTEGRITY_SEVERITY_PROHIBITED if prohibited_total else INTEGRITY_SEVERITY_INFO,
        source_phase="v4_0_phase_1_to_7",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=f"Prohibited state audit observed prohibited_evidence_count={prohibited_total}.",
    )


def audit_integrity_enforcement_boundary(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityFinding:
    return build_operational_integrity_finding(
        finding_type=INTEGRITY_FINDING_BOUNDARY,
        severity=INTEGRITY_SEVERITY_INFO,
        source_phase="v4_0_phase_8",
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation="Integrity enforcement performed a deterministic audit only; correction and remediation are disabled.",
    )


def build_operational_integrity_finding(
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
    explanation: str,
) -> OperationalIntegrityFinding:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
    )
    lineage_reference = _lineage_reference(
        lifecycle_foundation,
        governance_report,
        validation_report,
        production_consumption_report,
        recovery_report,
        diagnostics_report,
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
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "explanation": explanation,
        }
    )
    return OperationalIntegrityFinding(
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
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def determine_operational_integrity_status(
    findings: tuple[OperationalIntegrityFinding, ...],
    leakage: dict[str, bool],
) -> str:
    severities = {finding.severity for finding in findings}
    if any(leakage.values()) or INTEGRITY_SEVERITY_CRITICAL in severities:
        return INTEGRITY_STATUS_VIOLATION
    if INTEGRITY_SEVERITY_BLOCKING in severities:
        return INTEGRITY_STATUS_BLOCKED
    if INTEGRITY_SEVERITY_PROHIBITED in severities:
        return INTEGRITY_STATUS_PROHIBITED
    if INTEGRITY_SEVERITY_UNKNOWN in severities:
        return INTEGRITY_STATUS_UNKNOWN
    if INTEGRITY_SEVERITY_WARNING in severities:
        return INTEGRITY_STATUS_WARNING
    return INTEGRITY_STATUS_PRESERVED


def order_operational_integrity_findings(
    findings: Iterable[OperationalIntegrityFinding],
) -> tuple[OperationalIntegrityFinding, ...]:
    return tuple(sorted(tuple(findings), key=lambda item: item.deterministic_key))


def _build_leakage_finding(
    finding_type: str,
    source_phase: str,
    leakage_key: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
    leakage: dict[str, bool],
) -> OperationalIntegrityFinding:
    detected = leakage[leakage_key]
    return build_operational_integrity_finding(
        finding_type=finding_type,
        severity=INTEGRITY_SEVERITY_CRITICAL if detected else INTEGRITY_SEVERITY_INFO,
        source_phase=source_phase,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=f"{leakage_key}_leakage_detected={detected}.",
    )


def _build_safety_finding(
    finding_type: str,
    source_phase: str,
    safety_key: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
) -> OperationalIntegrityFinding:
    safety_map = {
        "provenance": _provenance_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
        ),
        "lineage": _lineage_safe(
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
        ),
        "replay": _replay_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
        ),
        "rollback": _rollback_safe(
            drift_report,
            governance_report,
            validation_report,
            production_consumption_report,
            recovery_report,
            diagnostics_report,
        ),
    }
    safe = safety_map[safety_key]
    return build_operational_integrity_finding(
        finding_type=finding_type,
        severity=INTEGRITY_SEVERITY_INFO if safe else INTEGRITY_SEVERITY_BLOCKING,
        source_phase=source_phase,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        production_consumption_report=production_consumption_report,
        recovery_report=recovery_report,
        diagnostics_report=diagnostics_report,
        explanation=f"{safety_key}_continuity_safe={safe}.",
    )


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
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
        )
    )


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    production_consumption_report: ProductionConsumptionGovernanceReport,
    recovery_report: RecoveryCertificationReport,
    diagnostics_report: OperationalDiagnosticsReport,
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
    return "|".join(references) if references else f"{token}_integrity_reference_not_visible"


def _provenance_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "provenance_safe", True)) for report in reports)


def _lineage_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "lineage_safe", True)) for report in reports)


def _replay_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "replay_safe", True)) for report in reports)


def _rollback_safe(*reports: object) -> bool:
    return all(bool(getattr(report, "rollback_safe", True)) for report in reports)


def _truthy(source: object, field_name: str) -> bool:
    return bool(getattr(source, field_name, False))


def _any_truthy(source: object, field_names: tuple[str, ...]) -> bool:
    return any(_truthy(source, field_name) for field_name in field_names)


def _hidden_fallback_count(
    lifecycle_foundation: PatchLifecycleFoundation,
    diagnostics_report: OperationalDiagnosticsReport,
) -> int:
    lifecycle_hidden = sum(1 for record in lifecycle_foundation.visibility_records if record.hidden)
    provenance_hidden = sum(1 for record in lifecycle_foundation.provenance_records if record.hidden)
    lineage_hidden = sum(1 for record in lifecycle_foundation.lineage_records if record.hidden_lineage_gap_correction_enabled)
    diagnostics_hidden = sum(1 for entry in diagnostics_report.entries if entry.hidden)
    return lifecycle_hidden + provenance_hidden + lineage_hidden + diagnostics_hidden


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
    "recovery_execution_enabled",
    "rollback_execution_enabled",
    "execution_authorized",
)
_REMEDIATION_FIELDS = (
    "remediation_enabled",
    "correction_enabled",
    "repair_enabled",
    "automatic_resolution_enabled",
    "corrective_behavior_enabled",
)
_RECOMMENDATION_FIELDS = ("recommendation_enabled", "recommendations_present")
_AUTHORIZATION_FIELDS = (
    "authorization_enabled",
    "operational_execution_authorized",
    "production_consumption_authorized",
    "recovery_execution_authorized",
    "rollback_execution_authorized",
    "execution_authorized",
)
_MUTATION_FIELDS = (
    "runtime_mutation_enabled",
    "hidden_lifecycle_state_mutation_enabled",
    "implicit_operational_state_transition_enabled",
    "automatic_patch_transition_logic_enabled",
)
_PRODUCTION_CONSUMPTION_FIELDS = (
    "production_consumption_authorized",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
)
_PLANNER_FIELDS = ("planner_integration_enabled", "planner_behavior_changed")
