"""Fail-visible integrity findings for v3.7 graph planning evidence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .v3_7_graph_integrity_models import (
    V37_INTEGRITY_FINDING_BLOCKED,
    V37_INTEGRITY_FINDING_CLASSIFICATIONS,
    V37_INTEGRITY_FINDING_CONTINUITY_VIOLATION,
    V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
    V37_INTEGRITY_FINDING_EXPLAINABILITY_VIOLATION,
    V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
    V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
    V37_INTEGRITY_FINDING_INVALID,
    V37_INTEGRITY_FINDING_PROVENANCE_VIOLATION,
    V37_INTEGRITY_FINDING_REPLAY_VIOLATION,
    V37_INTEGRITY_FINDING_ROLLBACK_VIOLATION,
    V37_INTEGRITY_FINDING_VALID,
    V37_INTEGRITY_FINDING_WARNING,
    V37GraphIntegrityFinding,
    export_v3_7_graph_integrity_finding,
)


def build_v3_7_graph_integrity_findings(
    integrity_totals: dict[str, int | bool],
    evidence_source_ids: tuple[str, ...],
) -> tuple[V37GraphIntegrityFinding, ...]:
    specs = (
        (
            V37_INTEGRITY_FINDING_VALID,
            "integrity",
            "valid",
            "info",
            "integrity policy evaluation completed as deterministic planning validation",
            False,
        ),
        (
            V37_INTEGRITY_FINDING_INVALID,
            "integrity",
            "invalid",
            "visibility",
            "invalid integrity states remain fail-visible",
            bool(integrity_totals["invalid_integrity_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_BLOCKED,
            "integrity",
            "blocked",
            "visibility",
            "blocked planning evidence remains fail-visible",
            bool(integrity_totals["blocked_integrity_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_WARNING,
            "integrity",
            "warning",
            "warning",
            "warning planning evidence remains fail-visible",
            bool(integrity_totals["warning_integrity_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_CONTINUITY_VIOLATION,
            "continuity",
            "continuity",
            "blocked",
            "continuity violations are blocked when active",
            bool(integrity_totals["continuity_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_PROVENANCE_VIOLATION,
            "provenance",
            "provenance",
            "blocked",
            "provenance violations are blocked when active",
            bool(integrity_totals["provenance_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_EXPLAINABILITY_VIOLATION,
            "explainability",
            "explainability",
            "blocked",
            "explainability violations are blocked when active",
            bool(integrity_totals["explainability_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_REPLAY_VIOLATION,
            "replay",
            "replay",
            "blocked",
            "replay violations are blocked when active",
            bool(integrity_totals["replay_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_ROLLBACK_VIOLATION,
            "rollback",
            "rollback",
            "blocked",
            "rollback violations are blocked when active",
            bool(integrity_totals["rollback_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_EXECUTION_BOUNDARY_VIOLATION,
            "execution_boundary",
            "execution_boundary",
            "blocked",
            "execution-boundary violations are blocked when active",
            bool(integrity_totals["execution_boundary_violation_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_HIDDEN_PROHIBITED_STATE,
            "finding_visibility",
            "prohibited",
            "blocked",
            "hidden prohibited states are blocked when active",
            bool(integrity_totals["hidden_prohibited_state_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_HIDDEN_UNSUPPORTED_STATE,
            "finding_visibility",
            "unsupported",
            "blocked",
            "hidden unsupported states are blocked when active",
            bool(integrity_totals["hidden_unsupported_state_count"]),
        ),
        (
            V37_INTEGRITY_FINDING_HIDDEN_UNKNOWN_STATE,
            "finding_visibility",
            "unknown",
            "blocked",
            "hidden unknown states are blocked when active",
            bool(integrity_totals["hidden_unknown_state_count"]),
        ),
    )
    findings = []
    for classification, subject_type, subject_id, severity, summary, active in specs:
        blocks_validation = active and severity in {"blocked", "error"}
        findings.append(
            V37GraphIntegrityFinding(
                finding_id=f"v3_7_graph_integrity_{classification}",
                finding_classification=classification,
                subject_type=subject_type,
                subject_id=f"{subject_id}:{int(active)}",
                severity=severity,
                summary=summary,
                evidence_references=evidence_source_ids,
                fail_visible=True,
                hidden=False,
                active_violation=active,
                blocks_validation=blocks_validation,
                execution_authorization=False,
                routing_authorization=False,
                scheduling_authorization=False,
                dispatch_authorization=False,
                traversal_authorization=False,
            )
        )
    return tuple(sorted(findings, key=lambda item: item.finding_id))


def count_v3_7_graph_integrity_findings_by_classification(
    findings: tuple[V37GraphIntegrityFinding, ...],
) -> dict[str, int]:
    counts = Counter(finding.finding_classification for finding in findings)
    return {
        classification: counts.get(classification, 0)
        for classification in V37_INTEGRITY_FINDING_CLASSIFICATIONS
    }


def export_v3_7_graph_integrity_finding_classifications() -> list[str]:
    return list(V37_INTEGRITY_FINDING_CLASSIFICATIONS)


def export_v3_7_graph_integrity_finding_records(
    findings: tuple[V37GraphIntegrityFinding, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_integrity_finding(finding)
        for finding in sorted(findings, key=lambda item: item.finding_id)
    ]
