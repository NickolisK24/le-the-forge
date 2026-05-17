"""Continuity certification for v4.1 closeout readiness."""

from __future__ import annotations

from .v4_1_closeout_readiness_models import V41CloseoutReadiness, default_v4_1_closeout_readiness
from .v4_1_closeout_readiness_visibility import validate_v4_1_closeout_visibility


def validate_v4_1_phase_continuity(payload: V41CloseoutReadiness) -> dict[str, object]:
    phase_results = {
        phase.phase_id: (
            phase.phase_coverage_present
            and phase.report_coverage_present
            and phase.integrity_coverage_present
            and phase.continuity_coverage_present
            and phase.provenance_coverage_present
            and phase.lineage_coverage_present
            and phase.replay_coverage_present
            and phase.rollback_coverage_present
        )
        for phase in payload.phase_coverage
    }
    return {
        "valid": all(phase_results.values()),
        "phase_results": phase_results,
        "phase_count": len(phase_results),
    }


def validate_v4_1_report_continuity(payload: V41CloseoutReadiness) -> dict[str, object]:
    report_results = {
        report.report_name: (
            report.present
            and report.json_valid
            and report.deterministic_hash_present
            and report.integrity_coverage_present
            and report.continuity_coverage_present
            and report.warning_visibility_present
            and report.generated_at_visible
        )
        for report in payload.report_coverage
    }
    return {
        "valid": all(report_results.values()),
        "report_results": report_results,
        "report_count": len(report_results),
    }


def certify_v4_1_closeout_continuity(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    visibility = validate_v4_1_closeout_visibility(source)
    phases = validate_v4_1_phase_continuity(source)
    reports = validate_v4_1_report_continuity(source)
    readiness = source.readiness
    return {
        "valid": (
            visibility["valid"]
            and phases["valid"]
            and reports["valid"]
            and readiness.integrity_verified
            and readiness.continuity_verified
            and readiness.governance_verified
            and readiness.replay_safe
            and readiness.rollback_safe
            and readiness.provenance_safe
            and readiness.lineage_safe
            and readiness.deterministic_readiness_visible
            and not readiness.remediation_enabled
            and not readiness.automatic_correction_enabled
            and not readiness.approval_enabled
            and not readiness.authorization_enabled
            and not readiness.execution_enabled
            and not readiness.runtime_mutation_enabled
        ),
        "phase_coverage_valid": phases["valid"],
        "report_coverage_valid": reports["valid"],
        "integrity_coverage_valid": readiness.integrity_verified,
        "continuity_coverage_valid": readiness.continuity_verified,
        "governance_verification_valid": readiness.governance_verified,
        "replay_verification_valid": readiness.replay_safe,
        "rollback_verification_valid": readiness.rollback_safe,
        "provenance_verification_valid": readiness.provenance_safe,
        "lineage_verification_valid": readiness.lineage_safe,
        "readiness_visibility_valid": readiness.deterministic_readiness_visible,
        "warning_aggregation_valid": visibility["warning_aggregation_valid"],
        "unsupported_prohibited_blocked_aggregation_valid": (
            visibility["unsupported_state_aggregation_visible"]
            and visibility["prohibited_state_aggregation_visible"]
            and visibility["blocked_state_aggregation_visible"]
        ),
        "phase_continuity": phases,
        "report_continuity": reports,
        "visibility": visibility,
    }
