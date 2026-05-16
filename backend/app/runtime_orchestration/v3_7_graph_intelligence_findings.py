"""Deterministic aggregated findings for v3.7 planning intelligence."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .v3_7_graph_intelligence_models import (
    V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE,
    V37_INTELLIGENCE_FINDING_CLASSIFICATIONS,
    V37_INTELLIGENCE_FINDING_COMPATIBILITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_CONTINUITY_WARNING_VISIBLE,
    V37_INTELLIGENCE_FINDING_EVALUATION_VISIBLE,
    V37_INTELLIGENCE_FINDING_EXPERIMENTAL_VISIBLE,
    V37_INTELLIGENCE_FINDING_EXPLAINABILITY_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_GOVERNANCE_VISIBLE,
    V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE,
    V37_INTELLIGENCE_FINDING_PROVENANCE_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_REPLAY_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_ROLLBACK_CONTINUITY_VISIBLE,
    V37_INTELLIGENCE_FINDING_SCENARIO_VISIBLE,
    V37_INTELLIGENCE_FINDING_SESSION_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE,
    V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE,
    V37GraphIntelligenceFinding,
    export_v3_7_graph_intelligence_finding,
)


def build_v3_7_graph_intelligence_findings(
    source_totals: dict[str, int],
    evidence_source_ids: tuple[str, ...],
) -> tuple[V37GraphIntelligenceFinding, ...]:
    specs = (
        (V37_INTELLIGENCE_FINDING_GOVERNANCE_VISIBLE, "governance", source_totals["governance_finding_total"], "governance findings remain visible"),
        (V37_INTELLIGENCE_FINDING_COMPATIBILITY_VISIBLE, "compatibility", source_totals["compatibility_finding_total"], "compatibility findings remain visible"),
        (V37_INTELLIGENCE_FINDING_EVALUATION_VISIBLE, "evaluation", source_totals["evaluation_finding_total"], "evaluation findings remain visible"),
        (V37_INTELLIGENCE_FINDING_SESSION_VISIBLE, "session", source_totals["session_finding_total"], "session findings remain visible"),
        (V37_INTELLIGENCE_FINDING_SCENARIO_VISIBLE, "scenario", source_totals["scenario_finding_total"], "scenario findings remain visible"),
        (V37_INTELLIGENCE_FINDING_BLOCKED_VISIBLE, "aggregate_visibility", source_totals["blocked_visibility_total"], "blocked planning states remain visible"),
        (V37_INTELLIGENCE_FINDING_UNSUPPORTED_VISIBLE, "aggregate_visibility", source_totals["unsupported_visibility_total"], "unsupported planning states remain visible"),
        (V37_INTELLIGENCE_FINDING_PROHIBITED_VISIBLE, "aggregate_visibility", source_totals["prohibited_visibility_total"], "prohibited planning states remain visible"),
        (V37_INTELLIGENCE_FINDING_UNKNOWN_VISIBLE, "aggregate_visibility", source_totals["unknown_visibility_total"], "unknown planning states remain visible"),
        (V37_INTELLIGENCE_FINDING_EXPERIMENTAL_VISIBLE, "aggregate_visibility", source_totals["experimental_visibility_total"], "experimental planning states remain visible"),
        (V37_INTELLIGENCE_FINDING_CONTINUITY_WARNING_VISIBLE, "aggregate_visibility", source_totals["continuity_warning_total"], "continuity warnings remain visible"),
        (V37_INTELLIGENCE_FINDING_PROVENANCE_CONTINUITY_VISIBLE, "provenance", source_totals["provenance_evidence_total"], "provenance continuity evidence remains visible"),
        (V37_INTELLIGENCE_FINDING_EXPLAINABILITY_CONTINUITY_VISIBLE, "explainability", source_totals["explainability_evidence_total"], "explainability continuity evidence remains visible"),
        (V37_INTELLIGENCE_FINDING_REPLAY_CONTINUITY_VISIBLE, "replay", source_totals["replay_evidence_total"], "replay continuity evidence remains visible"),
        (V37_INTELLIGENCE_FINDING_ROLLBACK_CONTINUITY_VISIBLE, "rollback", source_totals["rollback_evidence_total"], "rollback continuity evidence remains visible"),
    )
    return tuple(
        V37GraphIntelligenceFinding(
            finding_id=f"v3_7_graph_intelligence_{classification}",
            finding_classification=classification,
            source_type=source_type,
            subject_id=f"{classification}:{count}",
            visibility_status="fail_visible",
            summary=f"{summary}; total={count}",
            evidence_references=evidence_source_ids,
            fail_visible=True,
            hidden=False,
            execution_recommendation=False,
            runtime_path_selection=False,
        )
        for classification, source_type, count, summary in specs
    )


def count_v3_7_graph_intelligence_findings_by_classification(
    findings: tuple[V37GraphIntelligenceFinding, ...],
) -> dict[str, int]:
    counts = Counter(finding.finding_classification for finding in findings)
    return {
        classification: counts.get(classification, 0)
        for classification in V37_INTELLIGENCE_FINDING_CLASSIFICATIONS
    }


def export_v3_7_graph_intelligence_finding_classifications() -> list[str]:
    return list(V37_INTELLIGENCE_FINDING_CLASSIFICATIONS)


def export_v3_7_graph_intelligence_finding_records(
    findings: tuple[V37GraphIntelligenceFinding, ...],
) -> list[dict[str, Any]]:
    return [
        export_v3_7_graph_intelligence_finding(finding)
        for finding in sorted(findings, key=lambda item: item.finding_id)
    ]
