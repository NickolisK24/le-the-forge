"""Diagnostics and summaries for v4.1 closeout readiness."""

from __future__ import annotations

from .v4_1_closeout_readiness_continuity import certify_v4_1_closeout_continuity
from .v4_1_closeout_readiness_integrity import (
    enabled_v4_1_closeout_capability_flags,
    validate_v4_1_closeout_integrity,
    validate_v4_1_closeout_non_execution,
)
from .v4_1_closeout_readiness_models import V41CloseoutReadiness, default_v4_1_closeout_readiness
from .v4_1_closeout_readiness_visibility import validate_v4_1_closeout_visibility


def build_v4_1_closeout_diagnostics(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    visibility = validate_v4_1_closeout_visibility(source)
    continuity = certify_v4_1_closeout_continuity(source)
    non_execution = validate_v4_1_closeout_non_execution(source)
    enabled_flags = enabled_v4_1_closeout_capability_flags(source)
    return {
        "closeout_id": source.identity.closeout_id,
        "diagnostics_mode": "descriptive_closeout_only",
        "phase_count": visibility["phase_count"],
        "report_count": visibility["report_count"],
        "warning_count": source.readiness.warning_count,
        "blocker_count": source.readiness.blocker_count,
        "missing_phase_ids": visibility["missing_phase_ids"],
        "missing_report_names": visibility["missing_report_names"],
        "fail_visible_warning_count": visibility["fail_visible_warning_count"],
        "visibility_valid": visibility["valid"],
        "continuity_valid": continuity["valid"],
        "non_execution_valid": non_execution["valid"],
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
    }


def build_v4_1_final_governance_summary(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    visibility = validate_v4_1_closeout_visibility(source)
    continuity = certify_v4_1_closeout_continuity(source)
    non_execution = validate_v4_1_closeout_non_execution(source)
    return {
        "schema": "v4_1_final_governance_summary",
        "closeout_status": source.readiness.closeout_status,
        "v4_2_readiness_status": source.readiness.v4_2_readiness_status,
        "phase_coverage_certified": visibility["phase_coverage_complete"],
        "report_coverage_certified": visibility["report_coverage_complete"],
        "integrity_verified": continuity["integrity_coverage_valid"],
        "continuity_verified": continuity["continuity_coverage_valid"],
        "governance_verified": continuity["governance_verification_valid"],
        "replay_safe": continuity["replay_verification_valid"],
        "rollback_safe": continuity["rollback_verification_valid"],
        "provenance_safe": continuity["provenance_verification_valid"],
        "lineage_safe": continuity["lineage_verification_valid"],
        "warning_count": source.readiness.warning_count,
        "blocker_count": source.readiness.blocker_count,
        "non_execution_valid": non_execution["valid"],
        "readiness_mode": "planning_ready_with_warnings_descriptive_only",
    }


def build_v4_2_planning_readiness_certification(payload: V41CloseoutReadiness | None = None) -> dict[str, object]:
    source = payload or default_v4_1_closeout_readiness()
    integrity = validate_v4_1_closeout_integrity(source)
    return {
        "schema": "v4_2_planning_readiness_certification",
        "readiness_id": source.readiness.readiness_id,
        "v4_2_readiness_status": source.readiness.v4_2_readiness_status,
        "planning_only": source.readiness.planning_only,
        "descriptive_only": source.readiness.descriptive_only,
        "non_executable": source.readiness.non_executable,
        "warning_count": source.readiness.warning_count,
        "blocker_count": source.readiness.blocker_count,
        "integrity_valid": integrity["valid"],
        "readiness_certification_does_not_authorize_operations": True,
        "approval_enabled": False,
        "authorization_enabled": False,
        "execution_enabled": False,
    }
