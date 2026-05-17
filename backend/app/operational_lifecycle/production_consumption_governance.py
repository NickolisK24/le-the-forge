"""Deterministic controlled production consumption governance.

The governance layer evaluates evidence gates and blockers. It never
authorizes production consumption, enables production consumption, integrates
with planners, repairs blockers, or mutates source evidence.
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
from .production_consumption_hashing import hash_production_consumption_governance_report
from .production_consumption_models import (
    PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE,
    PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE,
    PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_INTEGRITY_WARNING,
    PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE,
    PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION,
    PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS,
    PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE,
    PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY,
    PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
    PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED,
    PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN,
    PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED,
    PRODUCTION_CONSUMPTION_GATE_STATE_VISIBLE,
    PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE,
    PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE,
    PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
    PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL,
    PRODUCTION_CONSUMPTION_SEVERITY_INFO,
    PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED,
    PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN,
    PRODUCTION_CONSUMPTION_SEVERITY_WARNING,
    ProductionConsumptionGate,
    ProductionConsumptionGovernanceReport,
)
from .production_consumption_visibility import (
    blocked_gate_count,
    critical_gate_count,
    prohibited_gate_count,
    satisfied_gate_count,
    unknown_gate_count,
    unsupported_gate_count,
    warning_gate_count,
)
from .validation_automation_models import OperationalValidationReport


def evaluate_controlled_production_consumption_governance(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGovernanceReport:
    gates = order_production_consumption_gates(
        (
            evaluate_lifecycle_evidence_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_drift_evidence_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_bundle_governance_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_operational_validation_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_provenance_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_lineage_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_replay_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_rollback_continuity_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_unsupported_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_prohibited_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_blocked_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_unknown_state_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_integrity_warning_gate(lifecycle_foundation, drift_report, governance_report, validation_report),
            evaluate_production_consumption_prohibition_gate(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
            ),
            evaluate_production_consumption_readiness_gate(
                lifecycle_foundation,
                drift_report,
                governance_report,
                validation_report,
            ),
        )
    )
    placeholder = ProductionConsumptionGovernanceReport(
        lifecycle_identity=lifecycle_identity_key(lifecycle_foundation.patch_identity),
        drift_report_hash=drift_report.deterministic_report_hash,
        governance_report_hash=governance_report.deterministic_report_hash,
        validation_report_hash=validation_report.deterministic_report_hash,
        gate_count=len(gates),
        gates=gates,
        satisfied_gate_count=satisfied_gate_count(gates),
        blocked_gate_count=blocked_gate_count(gates),
        unsupported_gate_count=unsupported_gate_count(gates),
        prohibited_gate_count=prohibited_gate_count(gates),
        unknown_gate_count=unknown_gate_count(gates),
        warning_count=warning_gate_count(gates),
        critical_count=critical_gate_count(gates),
        replay_safe=drift_report.replay_safe and governance_report.replay_safe and validation_report.replay_safe,
        rollback_safe=drift_report.rollback_safe and governance_report.rollback_safe and validation_report.rollback_safe,
        provenance_safe=drift_report.provenance_safe and governance_report.provenance_safe and validation_report.provenance_safe,
        lineage_safe=governance_report.lineage_safe and validation_report.lineage_safe,
        production_consumption_authorized=False,
        production_consumption_enabled=False,
        deterministic_report_hash="pending",
    )
    return replace(
        placeholder,
        deterministic_report_hash=hash_production_consumption_governance_report(placeholder),
    )


def evaluate_lifecycle_evidence_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    state_count = len(lifecycle_foundation.lifecycle_states)
    has_identity = bool(lifecycle_identity_key(lifecycle_foundation.patch_identity))
    gate_state = PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED if has_identity and state_count else PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN
    severity = PRODUCTION_CONSUMPTION_SEVERITY_WARNING if _lifecycle_fail_visible_state_count(lifecycle_foundation) else PRODUCTION_CONSUMPTION_SEVERITY_INFO
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_LIFECYCLE_EVIDENCE,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Lifecycle evidence gate is visible with "
            f"state_count={state_count}; satisfied means evidence is present and internally consistent only."
        ),
    )


def evaluate_drift_evidence_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    gate_state = PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED if drift_report.deterministic_report_hash else PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN
    severity = PRODUCTION_CONSUMPTION_SEVERITY_WARNING if drift_report.finding_count else PRODUCTION_CONSUMPTION_SEVERITY_INFO
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_DRIFT_EVIDENCE,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Drift evidence gate is visible with "
            f"finding_count={drift_report.finding_count}; drift visibility does not remediate drift."
        ),
    )


def evaluate_bundle_governance_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    gate_state = (
        PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
        if governance_report.deterministic_report_hash and not governance_report.production_consumption_authorized
        else PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED
    )
    severity = PRODUCTION_CONSUMPTION_SEVERITY_WARNING if governance_report.warning_count else PRODUCTION_CONSUMPTION_SEVERITY_INFO
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_BUNDLE_GOVERNANCE,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Bundle governance gate is visible and remains non-authorizing with "
            f"production_consumption_authorized={governance_report.production_consumption_authorized}."
        ),
    )


def evaluate_operational_validation_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    gate_state = (
        PRODUCTION_CONSUMPTION_GATE_STATE_NOT_SATISFIED
        if validation_report.validation_state != "ready"
        else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    )
    severity = (
        PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING
        if validation_report.validation_state != "ready"
        else PRODUCTION_CONSUMPTION_SEVERITY_INFO
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_OPERATIONAL_VALIDATION,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Operational validation gate is visible with "
            f"validation_state={validation_report.validation_state}; no validation result authorizes production consumption."
        ),
    )


def evaluate_provenance_continuity_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    safe = drift_report.provenance_safe and governance_report.provenance_safe and validation_report.provenance_safe
    gate_state = PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED if safe else PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED
    severity = (
        PRODUCTION_CONSUMPTION_SEVERITY_WARNING
        if safe and validation_report.warning_count
        else PRODUCTION_CONSUMPTION_SEVERITY_INFO
        if safe
        else PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_PROVENANCE_CONTINUITY,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Provenance continuity gate is visible with provenance_safe={safe}.",
    )


def evaluate_lineage_continuity_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    gate_state = PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED if validation_report.blocked_count else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED
    severity = PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING if validation_report.blocked_count else PRODUCTION_CONSUMPTION_SEVERITY_INFO
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_LINEAGE_CONTINUITY,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Lineage continuity gate is visible with "
            f"validation_blocked_count={validation_report.blocked_count}; blockers are not resolved."
        ),
    )


def evaluate_replay_continuity_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    safe = drift_report.replay_safe and governance_report.replay_safe and validation_report.replay_safe
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_REPLAY_CONTINUITY,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED if safe else PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_WARNING if safe else PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Replay continuity gate is visible with replay_safe={safe}; replay execution is not enabled.",
    )


def evaluate_rollback_continuity_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    safe = drift_report.rollback_safe and governance_report.rollback_safe and validation_report.rollback_safe
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_ROLLBACK_CONTINUITY,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED if safe else PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_WARNING if safe else PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Rollback continuity gate is visible with rollback_safe={safe}; rollback execution is not enabled.",
    )


def evaluate_unsupported_state_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNSUPPORTED)
        + drift_report.unsupported_drift_count
        + governance_report.unsupported_count
        + validation_report.unsupported_count
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_UNSUPPORTED_STATE,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_UNSUPPORTED if total else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_WARNING if total else PRODUCTION_CONSUMPTION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Unsupported gate states remain visible with unsupported_evidence_count={total}.",
    )


def evaluate_prohibited_state_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_PROHIBITED)
        + drift_report.prohibited_drift_count
        + governance_report.prohibited_count
        + validation_report.prohibited_count
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_PROHIBITED_STATE,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED if total else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED if total else PRODUCTION_CONSUMPTION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Prohibited gate states remain visible with prohibited_evidence_count={total}.",
    )


def evaluate_blocked_state_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_BLOCKED)
        + drift_report.blocking_drift_count
        + governance_report.blocked_count
        + validation_report.blocked_count
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_BLOCKED_STATE,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED if total else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING if total else PRODUCTION_CONSUMPTION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Blocked gate states remain visible with blocked_evidence_count={total}.",
    )


def evaluate_unknown_state_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_UNKNOWN)
        + drift_report.unknown_drift_count
        + governance_report.unknown_count
        + validation_report.unknown_count
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_UNKNOWN_STATE,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_UNKNOWN if total else PRODUCTION_CONSUMPTION_GATE_STATE_SATISFIED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_UNKNOWN if total else PRODUCTION_CONSUMPTION_SEVERITY_INFO,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=f"Unknown gate states remain visible with unknown_evidence_count={total}.",
    )


def evaluate_integrity_warning_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    warning_total = (
        _state_count(lifecycle_foundation, LIFECYCLE_STATE_DEPRECATED)
        + _state_count(lifecycle_foundation, LIFECYCLE_STATE_EXPERIMENTAL)
        + governance_report.warning_count
        + validation_report.warning_count
    )
    severity = PRODUCTION_CONSUMPTION_SEVERITY_CRITICAL if validation_report.critical_count else PRODUCTION_CONSUMPTION_SEVERITY_WARNING
    gate_state = PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED if validation_report.critical_count else PRODUCTION_CONSUMPTION_GATE_STATE_VISIBLE
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_INTEGRITY_WARNING,
        gate_state=gate_state,
        severity=severity,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Integrity warning gate remains visible with "
            f"warning_evidence_count={warning_total} and critical_count={validation_report.critical_count}."
        ),
    )


def evaluate_production_consumption_prohibition_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_PROHIBITION,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_PROHIBITED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_PROHIBITED,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Production consumption is explicitly prohibited; production_consumption_authorized "
            "and production_consumption_enabled remain false."
        ),
    )


def evaluate_production_consumption_readiness_gate(
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> ProductionConsumptionGate:
    readiness_blocker_count = (
        drift_report.blocking_drift_count
        + governance_report.blocked_count
        + governance_report.prohibited_count
        + validation_report.blocked_count
        + validation_report.prohibited_count
        + validation_report.critical_count
    )
    return build_production_consumption_gate(
        gate_type=PRODUCTION_CONSUMPTION_GATE_PRODUCTION_CONSUMPTION_READINESS,
        gate_state=PRODUCTION_CONSUMPTION_GATE_STATE_BLOCKED,
        severity=PRODUCTION_CONSUMPTION_SEVERITY_BLOCKING,
        lifecycle_foundation=lifecycle_foundation,
        drift_report=drift_report,
        governance_report=governance_report,
        validation_report=validation_report,
        explanation=(
            "Production consumption readiness remains descriptive and blocked with "
            f"readiness_blocker_count={readiness_blocker_count}; planner behavior is unchanged."
        ),
    )


def build_production_consumption_gate(
    *,
    gate_type: str,
    gate_state: str,
    severity: str,
    lifecycle_foundation: PatchLifecycleFoundation,
    drift_report: LifecycleDriftReport,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
    explanation: str,
) -> ProductionConsumptionGate:
    lifecycle_reference = lifecycle_identity_key(lifecycle_foundation.patch_identity)
    provenance_reference = _provenance_reference(lifecycle_foundation, governance_report, validation_report)
    lineage_reference = _lineage_reference(lifecycle_foundation, governance_report, validation_report)
    replay_reference = _continuity_reference(lifecycle_foundation, "replay")
    rollback_reference = _continuity_reference(lifecycle_foundation, "rollback")
    deterministic_key = stable_serialize(
        {
            "gate_type": gate_type,
            "gate_state": gate_state,
            "severity": severity,
            "lifecycle_reference": lifecycle_reference,
            "drift_reference": drift_report.deterministic_report_hash,
            "governance_reference": governance_report.deterministic_report_hash,
            "validation_reference": validation_report.deterministic_report_hash,
            "provenance_reference": provenance_reference,
            "lineage_reference": lineage_reference,
            "replay_reference": replay_reference,
            "rollback_reference": rollback_reference,
            "explanation": explanation,
        }
    )
    return ProductionConsumptionGate(
        gate_type=gate_type,
        gate_state=gate_state,
        severity=severity,
        lifecycle_reference=lifecycle_reference,
        drift_reference=drift_report.deterministic_report_hash,
        governance_reference=governance_report.deterministic_report_hash,
        validation_reference=validation_report.deterministic_report_hash,
        provenance_reference=provenance_reference,
        lineage_reference=lineage_reference,
        replay_reference=replay_reference,
        rollback_reference=rollback_reference,
        explanation=explanation,
        deterministic_key=deterministic_key,
    )


def order_production_consumption_gates(
    gates: Iterable[ProductionConsumptionGate],
) -> tuple[ProductionConsumptionGate, ...]:
    return tuple(sorted(tuple(gates), key=lambda item: item.deterministic_key))


def _provenance_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> str:
    references = tuple(sorted(record.provenance_reference_id for record in lifecycle_foundation.provenance_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
        )
    )


def _lineage_reference(
    lifecycle_foundation: PatchLifecycleFoundation,
    governance_report: TrustedBundleGovernanceReport,
    validation_report: OperationalValidationReport,
) -> str:
    references = tuple(sorted(record.lineage_reference_id for record in lifecycle_foundation.lineage_records))
    return "|".join(
        (
            *references,
            f"governance:{governance_report.deterministic_report_hash}",
            f"validation:{validation_report.deterministic_report_hash}",
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
    return "|".join(references) if references else f"{token}_continuity_reference_not_visible"


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
