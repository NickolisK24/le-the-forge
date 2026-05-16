"""Generate the v3.7 graph planning intelligence aggregation report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.classification_hashing import deterministic_hash  # noqa: E402
from app.runtime_orchestration.v3_7_graph_intelligence_aggregation import (  # noqa: E402
    build_v3_7_graph_planning_intelligence_aggregation,
)
from app.runtime_orchestration.v3_7_graph_intelligence_audit import (  # noqa: E402
    V37_GRAPH_INTELLIGENCE_AUDIT_STABLE,
    audit_v3_7_graph_intelligence,
    export_v3_7_graph_intelligence_audit_result,
)
from app.runtime_orchestration.v3_7_graph_intelligence_explainability import (  # noqa: E402
    V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_intelligence,
    export_v3_7_graph_intelligence_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_intelligence_findings import (  # noqa: E402
    count_v3_7_graph_intelligence_findings_by_classification,
    export_v3_7_graph_intelligence_finding_records,
)
from app.runtime_orchestration.v3_7_graph_intelligence_models import (  # noqa: E402
    export_v3_7_graph_intelligence_counts,
    export_v3_7_graph_intelligence_totals,
    export_v3_7_graph_planning_intelligence_aggregation,
    hash_v3_7_graph_planning_intelligence_aggregation,
    validate_v3_7_graph_intelligence_hash_stability,
    validate_v3_7_graph_intelligence_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_intelligence_provenance import (  # noqa: E402
    V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
    audit_v3_7_graph_intelligence_provenance,
    export_v3_7_graph_intelligence_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_intelligence_replay import (  # noqa: E402
    export_v3_7_graph_intelligence_replay_evidence_records,
    validate_v3_7_graph_intelligence_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_intelligence_validation import (  # noqa: E402
    V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE,
    export_v3_7_graph_intelligence_validation_result,
    validate_v3_7_graph_intelligence,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_planning_intelligence_aggregation_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    aggregation = build_v3_7_graph_planning_intelligence_aggregation()
    validation = validate_v3_7_graph_intelligence((aggregation,))
    audit = audit_v3_7_graph_intelligence(aggregation)
    provenance = audit_v3_7_graph_intelligence_provenance(aggregation)
    explainability = explain_v3_7_graph_intelligence(aggregation)
    replay = validate_v3_7_graph_intelligence_replay_evidence(aggregation)
    serialization = validate_v3_7_graph_intelligence_serialization_stability(aggregation)
    hashing = validate_v3_7_graph_intelligence_hash_stability(aggregation)
    totals = export_v3_7_graph_intelligence_totals(aggregation.totals)
    report = {
        "schema_version": "v3_7.graph_planning_intelligence_aggregation_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_planning_intelligence_aggregation",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph planning intelligence aggregation",
        "planning_intelligence_aggregation": True,
        "runtime_orchestration_decision_making": False,
        "aggregation_is_non_executable": True,
        "aggregation_is_planning_evidence_summarization_only": True,
        "aggregated_insights_are_not_recommendations": True,
        "aggregated_insights_do_not_authorize_execution": True,
        "aggregation_does_not_select_graph_paths": True,
        "aggregation_does_not_select_scenarios_for_execution": True,
        "aggregation_does_not_enable_routing_scheduling_dispatch_traversal_runtime_orchestration": True,
        "graph_execution_enabled": False,
        "aggregation_driven_execution_enabled": False,
        "orchestration_selection_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "graph_traversal_execution_enabled": False,
        "optimization_engine_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "persistent_runtime_writes_enabled": False,
        "runtime_decision_making_enabled": False,
        "path_ranking_for_execution_enabled": False,
        "scenario_selection_for_execution_enabled": False,
        "executable_planning_insights_enabled": False,
        "orchestration_state_machine_enabled": False,
        "aggregation_counts": export_v3_7_graph_intelligence_counts(aggregation),
        "evidence_source_counts": {
            "evidence_source_count": len(aggregation.evidence_sources),
            "graph_source_count": _source_type_count(aggregation, "graph_foundations"),
            "governance_source_count": _source_type_count(aggregation, "governance"),
            "compatibility_source_count": _source_type_count(aggregation, "compatibility"),
            "evaluation_source_count": _source_type_count(aggregation, "evaluation"),
            "session_source_count": _source_type_count(aggregation, "session"),
            "scenario_source_count": _source_type_count(aggregation, "scenario"),
        },
        "finding_classification_counts": count_v3_7_graph_intelligence_findings_by_classification(aggregation.findings),
        "governance_finding_totals": {"governance_finding_total": totals["governance_finding_total"]},
        "compatibility_finding_totals": {"compatibility_finding_total": totals["compatibility_finding_total"]},
        "evaluation_finding_totals": {"evaluation_finding_total": totals["evaluation_finding_total"]},
        "session_finding_totals": {"session_finding_total": totals["session_finding_total"]},
        "scenario_finding_totals": {"scenario_finding_total": totals["scenario_finding_total"]},
        "blocked_unsupported_prohibited_unknown_visibility_counts": {
            "blocked_visibility_total": totals["blocked_visibility_total"],
            "unsupported_visibility_total": totals["unsupported_visibility_total"],
            "prohibited_visibility_total": totals["prohibited_visibility_total"],
            "unknown_visibility_total": totals["unknown_visibility_total"],
            "experimental_visibility_total": totals["experimental_visibility_total"],
            "continuity_warning_total": totals["continuity_warning_total"],
        },
        "replay_evidence_counts": {
            "replay_evidence_count": replay["replay_evidence_count"],
            "non_executable_replay_evidence": replay["non_executable_replay_evidence"],
            "runtime_replay": replay["runtime_replay"],
            "execution_authorization": replay["execution_authorization"],
        },
        "rollback_continuity_counts": {
            "rollback_reference_count": replay["rollback_reference_count"],
            "rollback_continuity_preserved": replay["rollback_continuity_preserved"],
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "aggregation_creation_provenance_preserved": provenance.aggregation_creation_provenance_preserved,
            "graph_provenance_preserved": provenance.graph_provenance_preserved,
            "governance_provenance_preserved": provenance.governance_provenance_preserved,
            "compatibility_provenance_preserved": provenance.compatibility_provenance_preserved,
            "evaluation_provenance_preserved": provenance.evaluation_provenance_preserved,
            "session_provenance_preserved": provenance.session_provenance_preserved,
            "scenario_provenance_preserved": provenance.scenario_provenance_preserved,
            "replay_provenance_preserved": provenance.replay_provenance_preserved,
            "rollback_provenance_preserved": provenance.rollback_provenance_preserved,
            "explainability_provenance_preserved": provenance.explainability_provenance_preserved,
            "continuity_provenance_preserved": provenance.continuity_provenance_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "aggregation_explanation_count": explainability.aggregation_explanation_count,
            "evidence_source_explanation_count": explainability.evidence_source_explanation_count,
            "finding_explanation_count": explainability.finding_explanation_count,
            "insight_explanation_count": explainability.insight_explanation_count,
            "replay_explanation_count": explainability.replay_explanation_count,
            "risk_visibility_explanation_count": explainability.risk_visibility_explanation_count,
            "does_not_authorize_explanation_count": explainability.does_not_authorize_explanation_count,
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_aggregation_identity_count": validation.duplicate_aggregation_identity_count,
            "hidden_prohibited_finding_count": validation.hidden_prohibited_finding_count,
            "hidden_unsupported_finding_count": validation.hidden_unsupported_finding_count,
            "hidden_unknown_finding_count": validation.hidden_unknown_finding_count,
            "non_execution_guarantee_preserved": validation.non_execution_guarantee_preserved,
            "no_execution_recommendation_preserved": validation.no_execution_recommendation_preserved,
            "no_runtime_path_selection_preserved": validation.no_runtime_path_selection_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "aggregation_hash": hash_v3_7_graph_planning_intelligence_aggregation(aggregation),
            "validation_hash": validation.deterministic_validation_hash,
            "audit_hash": audit.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_INTELLIGENCE_VALIDATION_STABLE,
            "audit_coverage": audit.audit_status == V37_GRAPH_INTELLIGENCE_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED,
            "explainability_coverage": explainability.explainability_status == V37_GRAPH_INTELLIGENCE_EXPLAINABILITY_STABLE,
            "replay_continuity_coverage": replay["replay_continuity_preserved"],
            "rollback_continuity_coverage": replay["rollback_continuity_preserved"],
            "non_execution_coverage": validation.non_execution_guarantee_preserved,
            "no_execution_recommendation_coverage": validation.no_execution_recommendation_preserved,
            "no_runtime_path_selection_coverage": validation.no_runtime_path_selection_preserved,
        },
        "planning_intelligence_aggregation_record": export_v3_7_graph_planning_intelligence_aggregation(aggregation),
        "finding_records": export_v3_7_graph_intelligence_finding_records(aggregation.findings),
        "replay_evidence_records": export_v3_7_graph_intelligence_replay_evidence_records(aggregation.replay_evidence),
        "validation_result": export_v3_7_graph_intelligence_validation_result(validation),
        "audit_result": export_v3_7_graph_intelligence_audit_result(audit),
        "provenance_result": export_v3_7_graph_intelligence_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_intelligence_explainability_result(explainability),
        "explicit_limitations": [
            "aggregation is non-executable",
            "aggregation is planning evidence summarization only",
            "aggregated insights are not recommendations",
            "aggregated insights do not authorize execution",
            "aggregation does not select graph paths",
            "aggregation does not select scenarios for execution",
            "aggregation does not enable routing, scheduling, dispatch, traversal, or runtime orchestration",
        ],
        "summary": {
            "aggregation_status": validation.validation_status,
            "planning_intelligence_aggregation": True,
            "runtime_orchestration_decision_making": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "non_execution_guarantee_verified": validation.non_execution_guarantee_preserved,
            "no_execution_recommendation_verified": validation.no_execution_recommendation_preserved,
            "no_runtime_path_selection_verified": validation.no_runtime_path_selection_preserved,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Planning Intelligence Aggregation",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 7 adds deterministic graph planning intelligence aggregation.",
        "",
        "Aggregation is NON-executable.",
        "",
        "Aggregation is planning evidence summarization only.",
        "",
        "Aggregated insights are NOT recommendations.",
        "",
        "Aggregated insights do NOT authorize execution.",
        "",
        "Aggregation does NOT select graph paths.",
        "",
        "Aggregation does NOT select scenarios for execution.",
        "",
        "Aggregation does NOT enable routing, scheduling, dispatch, traversal, or runtime orchestration.",
        "",
        "Planning intelligence aggregation summarizes deterministic graph evidence. Runtime orchestration decision-making would decide runtime behavior. This phase implements planning intelligence aggregation only, not runtime orchestration decision-making.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Aggregation hash: `{report['deterministic_guarantees']['aggregation_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Evidence sources: `{report['evidence_source_counts']['evidence_source_count']}`",
        f"- Aggregated findings: `{report['aggregation_counts']['finding_count']}`",
        f"- Planning insights: `{report['aggregation_counts']['insight_count']}`",
        f"- Replay evidence records: `{report['replay_evidence_counts']['replay_evidence_count']}`",
        f"- Rollback continuity references: `{report['rollback_continuity_counts']['rollback_reference_count']}`",
        f"- Blocked visibility total: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['blocked_visibility_total']}`",
        f"- Unsupported visibility total: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unsupported_visibility_total']}`",
        f"- Prohibited visibility total: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['prohibited_visibility_total']}`",
        f"- Unknown visibility total: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unknown_visibility_total']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic aggregation identity stability",
        "- deterministic evidence-source stability",
        "- deterministic aggregated finding stability",
        "- deterministic replay evidence stability",
        "- deterministic rollback continuity",
        "- deterministic audit stability",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- governance aggregation continuity",
        "- compatibility aggregation continuity",
        "- evaluation aggregation continuity",
        "- session aggregation continuity",
        "- scenario aggregation continuity",
        "- fail-visible blocked findings",
        "- fail-visible unsupported findings",
        "- fail-visible prohibited findings",
        "- fail-visible unknown findings",
        "- deterministic serialization compatibility",
        "- deterministic hashing compatibility",
        "- aggregation is non-executable",
        "- aggregation does not recommend execution",
        "- aggregation does not select runtime paths",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add aggregation-driven execution.",
        "",
        "This implementation does not add orchestration selection.",
        "",
        "This implementation does not add routing, scheduling, dispatch, graph traversal execution, optimization engines, recommendation systems, autonomous orchestration, runtime mutation, persistent runtime writes, runtime decision-making, path ranking for execution, scenario selection for execution, executable planning insights, or orchestration state machines.",
        "",
        "Planning intelligence aggregation remains deterministic planning evidence summarization, not runtime orchestration decision-making.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _source_type_count(aggregation, source_type: str) -> int:
    return sum(1 for source in aggregation.evidence_sources if source.source_type == source_type)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_planning_intelligence_aggregation_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_planning_intelligence_aggregation_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_PLANNING_INTELLIGENCE_AGGREGATION.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
