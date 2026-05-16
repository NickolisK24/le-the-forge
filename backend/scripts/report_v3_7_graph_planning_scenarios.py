"""Generate the v3.7 graph planning scenarios report."""

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
from app.runtime_orchestration.v3_7_graph_scenario_audit import (  # noqa: E402
    V37_GRAPH_SCENARIO_AUDIT_STABLE,
    audit_v3_7_graph_scenario,
    export_v3_7_graph_scenario_audit_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_comparison import (  # noqa: E402
    export_v3_7_graph_scenario_comparison_records,
    validate_v3_7_graph_scenario_comparison_stability,
)
from app.runtime_orchestration.v3_7_graph_scenario_explainability import (  # noqa: E402
    V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE,
    explain_v3_7_graph_scenario,
    export_v3_7_graph_scenario_explainability_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_models import (  # noqa: E402
    V37_GRAPH_SCENARIO_STATUSES,
    V37_SCENARIO_STATUS_BLOCKED,
    V37_SCENARIO_STATUS_PROHIBITED,
    V37_SCENARIO_STATUS_UNKNOWN,
    V37_SCENARIO_STATUS_UNSUPPORTED,
    export_v3_7_graph_planning_scenario,
    export_v3_7_graph_scenario_counts,
    hash_v3_7_graph_planning_scenario,
    validate_v3_7_graph_scenario_hash_stability,
    validate_v3_7_graph_scenario_serialization_stability,
)
from app.runtime_orchestration.v3_7_graph_scenario_provenance import (  # noqa: E402
    V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED,
    audit_v3_7_graph_scenario_provenance,
    export_v3_7_graph_scenario_provenance_result,
)
from app.runtime_orchestration.v3_7_graph_scenario_replay import (  # noqa: E402
    export_v3_7_graph_scenario_replay_evidence_records,
    validate_v3_7_graph_scenario_replay_evidence,
)
from app.runtime_orchestration.v3_7_graph_scenario_validation import (  # noqa: E402
    V37_GRAPH_SCENARIO_VALIDATION_STABLE,
    export_v3_7_graph_scenario_validation_result,
    validate_v3_7_graph_scenarios,
)
from app.runtime_orchestration.v3_7_graph_scenario_variations import (  # noqa: E402
    build_v3_7_graph_planning_scenario,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_graph_planning_scenarios_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    scenario = build_v3_7_graph_planning_scenario()
    validation = validate_v3_7_graph_scenarios((scenario,))
    audit = audit_v3_7_graph_scenario(scenario)
    provenance = audit_v3_7_graph_scenario_provenance(scenario)
    explainability = explain_v3_7_graph_scenario(scenario)
    replay = validate_v3_7_graph_scenario_replay_evidence(scenario)
    comparison = validate_v3_7_graph_scenario_comparison_stability(scenario.comparison_evidence)
    serialization = validate_v3_7_graph_scenario_serialization_stability(scenario)
    hashing = validate_v3_7_graph_scenario_hash_stability(scenario)
    report = {
        "schema_version": "v3_7.graph_planning_scenarios_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_graph_planning_scenarios",
        "repo_root": str(root),
        "architectural_purpose": "deterministic graph planning scenario modeling",
        "planning_scenario_intelligence": True,
        "runtime_orchestration_branching": False,
        "scenarios_are_non_executable": True,
        "scenarios_are_hypothetical_planning_evidence_only": True,
        "hypothetical_variations_are_not_runtime_branches": True,
        "scenario_replay_evidence_is_not_runtime_replay": True,
        "comparisons_do_not_imply_orchestration_selection": True,
        "scenario_status_does_not_authorize_execution": True,
        "graph_planning_scenarios_do_not_enable_routing_scheduling_dispatch_traversal": True,
        "graph_execution_enabled": False,
        "scenario_execution_enabled": False,
        "runtime_orchestration_enabled": False,
        "routing_enabled": False,
        "scheduling_enabled": False,
        "dispatch_enabled": False,
        "graph_traversal_execution_enabled": False,
        "optimization_engine_enabled": False,
        "recommendation_enabled": False,
        "autonomous_orchestration_enabled": False,
        "runtime_mutation_enabled": False,
        "persistent_runtime_writes_enabled": False,
        "execution_capable_scenarios_enabled": False,
        "runtime_branching_behavior_enabled": False,
        "orchestration_state_machine_enabled": False,
        "runtime_orchestration_history_enabled": False,
        "scenario_counts": export_v3_7_graph_scenario_counts(scenario),
        "scenario_status_counts": _status_counts((scenario.status,), V37_GRAPH_SCENARIO_STATUSES),
        "variation_counts": {
            "variation_count": len(scenario.variations),
            "structural_hypothetical_variation_count": sum(
                1 for variation in scenario.variations if variation.structural_hypothetical_evidence_only
            ),
            "executable_orchestration_branch_count": sum(
                1 for variation in scenario.variations if variation.executable_orchestration_branch
            ),
            "prohibited_variation_count": sum(
                1
                for variation in scenario.variations
                if "prohibited"
                in {
                    variation.governance_classification,
                    variation.compatibility_classification,
                    variation.evaluation_classification,
                }
            ),
            "unsupported_variation_count": sum(
                1
                for variation in scenario.variations
                if "unsupported"
                in {
                    variation.governance_classification,
                    variation.compatibility_classification,
                    variation.evaluation_classification,
                }
            ),
            "unknown_variation_count": sum(
                1
                for variation in scenario.variations
                if "unknown"
                in {
                    variation.governance_classification,
                    variation.compatibility_classification,
                    variation.evaluation_classification,
                }
            ),
        },
        "comparison_counts": comparison,
        "replay_evidence_counts": {
            "replay_evidence_count": replay["replay_evidence_count"],
            "rollback_reference_count": replay["rollback_reference_count"],
            "non_executable_replay_evidence": replay["non_executable_replay_evidence"],
            "runtime_replay_state": replay["runtime_replay_state"],
            "execution_authorization": replay["execution_authorization"],
        },
        "rollback_continuity_counts": {
            "rollback_reference_count": replay["rollback_reference_count"],
            "rollback_continuity_preserved": replay["rollback_continuity_preserved"],
        },
        "blocked_unsupported_prohibited_unknown_visibility_counts": {
            "blocked_visible_count": _audit_status_count(scenario, V37_SCENARIO_STATUS_BLOCKED),
            "unsupported_visible_count": _audit_status_count(scenario, V37_SCENARIO_STATUS_UNSUPPORTED),
            "prohibited_visible_count": _audit_status_count(scenario, V37_SCENARIO_STATUS_PROHIBITED),
            "unknown_visible_count": _audit_status_count(scenario, V37_SCENARIO_STATUS_UNKNOWN),
        },
        "provenance_continuity_totals": {
            "provenance_status": provenance.provenance_status,
            "provenance_record_count": provenance.provenance_record_count,
            "scenario_creation_provenance_preserved": provenance.scenario_creation_provenance_preserved,
            "planning_session_provenance_preserved": provenance.planning_session_provenance_preserved,
            "graph_snapshot_provenance_preserved": provenance.graph_snapshot_provenance_preserved,
            "evaluation_provenance_preserved": provenance.evaluation_provenance_preserved,
            "replay_provenance_preserved": provenance.replay_provenance_preserved,
            "rollback_provenance_preserved": provenance.rollback_provenance_preserved,
            "explainability_provenance_preserved": provenance.explainability_provenance_preserved,
            "continuity_provenance_preserved": provenance.continuity_provenance_preserved,
            "comparison_provenance_preserved": provenance.comparison_provenance_preserved,
        },
        "explainability_continuity_totals": {
            "explainability_status": explainability.explainability_status,
            "explanation_count": explainability.explanation_count,
            "scenario_existence_explanation_count": explainability.scenario_existence_explanation_count,
            "variation_explanation_count": explainability.variation_explanation_count,
            "comparison_explanation_count": explainability.comparison_explanation_count,
            "replay_explanation_count": explainability.replay_explanation_count,
            "visible_finding_explanation_count": explainability.visible_finding_explanation_count,
            "blocked_explanation_count": explainability.blocked_explanation_count,
            "unsupported_explanation_count": explainability.unsupported_explanation_count,
            "prohibited_explanation_count": explainability.prohibited_explanation_count,
            "unknown_explanation_count": explainability.unknown_explanation_count,
            "changed_between_scenarios_explanation_count": (
                explainability.changed_between_scenarios_explanation_count
            ),
        },
        "validation_totals": {
            "validation_status": validation.validation_status,
            "valid": validation.valid,
            "finding_count": validation.finding_count,
            "error_count": validation.error_count,
            "visibility_finding_count": validation.visibility_finding_count,
            "duplicate_scenario_identity_count": validation.duplicate_scenario_identity_count,
            "invalid_variation_reference_count": validation.invalid_variation_reference_count,
            "invalid_replay_evidence_reference_count": validation.invalid_replay_evidence_reference_count,
            "invalid_comparison_reference_count": validation.invalid_comparison_reference_count,
            "hidden_prohibited_state_count": validation.hidden_prohibited_state_count,
            "hidden_unsupported_state_count": validation.hidden_unsupported_state_count,
            "hidden_unknown_state_count": validation.hidden_unknown_state_count,
            "non_execution_guarantee_preserved": validation.non_execution_guarantee_preserved,
        },
        "deterministic_guarantees": {
            "serialization_stable": serialization["stable"],
            "hash_stable": hashing["stable"],
            "scenario_hash": hash_v3_7_graph_planning_scenario(scenario),
            "validation_hash": validation.deterministic_validation_hash,
            "audit_hash": audit.deterministic_audit_hash,
            "provenance_hash": provenance.deterministic_provenance_hash,
            "explainability_hash": explainability.deterministic_explainability_hash,
        },
        "coverage": {
            "validation_coverage": validation.validation_status == V37_GRAPH_SCENARIO_VALIDATION_STABLE,
            "audit_coverage": audit.audit_status == V37_GRAPH_SCENARIO_AUDIT_STABLE,
            "provenance_coverage": provenance.provenance_status == V37_GRAPH_SCENARIO_PROVENANCE_PRESERVED,
            "explainability_coverage": explainability.explainability_status == V37_GRAPH_SCENARIO_EXPLAINABILITY_STABLE,
            "comparison_coverage": comparison["deterministic_comparison_stable"],
            "replay_continuity_coverage": replay["replay_continuity_preserved"],
            "rollback_continuity_coverage": replay["rollback_continuity_preserved"],
            "non_execution_coverage": validation.non_execution_guarantee_preserved,
        },
        "planning_scenario": export_v3_7_graph_planning_scenario(scenario),
        "comparison_records": export_v3_7_graph_scenario_comparison_records(scenario.comparison_evidence),
        "replay_evidence_records": export_v3_7_graph_scenario_replay_evidence_records(scenario.replay_evidence),
        "validation_result": export_v3_7_graph_scenario_validation_result(validation),
        "audit_result": export_v3_7_graph_scenario_audit_result(audit),
        "provenance_result": export_v3_7_graph_scenario_provenance_result(provenance),
        "explainability_result": export_v3_7_graph_scenario_explainability_result(explainability),
        "explicit_limitations": [
            "scenarios are non-executable",
            "scenarios are hypothetical planning evidence only",
            "hypothetical variations are not runtime branches",
            "scenario replay evidence is not runtime replay",
            "comparisons do not imply orchestration selection",
            "scenario status does not authorize execution",
            "graph planning scenarios do not enable routing, scheduling, dispatch, or traversal",
        ],
        "summary": {
            "scenario_status": validation.validation_status,
            "planning_scenario_intelligence": True,
            "runtime_orchestration_branching": False,
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "provenance_continuity_verified": validation.provenance_continuity_preserved,
            "explainability_continuity_verified": validation.explainability_continuity_preserved,
            "governance_continuity_verified": validation.governance_continuity_preserved,
            "compatibility_continuity_verified": validation.compatibility_continuity_preserved,
            "evaluation_continuity_verified": validation.evaluation_continuity_preserved,
            "replay_continuity_verified": validation.replay_continuity_preserved,
            "rollback_continuity_verified": validation.rollback_continuity_preserved,
            "non_execution_guarantee_verified": validation.non_execution_guarantee_preserved,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Graph Planning Scenarios",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 Phase 6 adds deterministic graph planning scenario modeling.",
        "",
        "Scenarios are NON-executable.",
        "",
        "Scenarios are hypothetical planning evidence only.",
        "",
        "Hypothetical variations are NOT runtime branches.",
        "",
        "Scenario replay evidence is NOT runtime replay.",
        "",
        "Comparisons do NOT imply orchestration selection.",
        "",
        "Scenario status does NOT authorize execution.",
        "",
        "Graph planning scenarios do NOT enable routing, scheduling, dispatch, or traversal.",
        "",
        "Planning scenario intelligence records controlled deterministic planning hypotheses. Runtime orchestration branching would control runtime behavior. This phase implements planning scenario intelligence only, not runtime orchestration branching.",
        "",
        "## Deterministic Scope",
        "",
        f"- Validation status: `{report['validation_totals']['validation_status']}`",
        f"- Scenario hash: `{report['deterministic_guarantees']['scenario_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        f"- Scenarios: `{report['scenario_counts']['scenario_count']}`",
        f"- Variations: `{report['variation_counts']['variation_count']}`",
        f"- Comparisons: `{report['comparison_counts']['comparison_count']}`",
        f"- Replay evidence records: `{report['replay_evidence_counts']['replay_evidence_count']}`",
        f"- Rollback continuity references: `{report['rollback_continuity_counts']['rollback_reference_count']}`",
        f"- Blocked visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['blocked_visible_count']}`",
        f"- Unsupported visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unsupported_visible_count']}`",
        f"- Prohibited visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['prohibited_visible_count']}`",
        f"- Unknown visible states: `{report['blocked_unsupported_prohibited_unknown_visibility_counts']['unknown_visible_count']}`",
        "",
        "## Verified Guarantees",
        "",
        "- deterministic scenario identity stability",
        "- deterministic variation stability",
        "- deterministic comparison stability",
        "- deterministic replay evidence stability",
        "- deterministic rollback continuity",
        "- deterministic audit stability",
        "- provenance continuity preservation",
        "- explainability continuity preservation",
        "- governance continuity preservation",
        "- compatibility continuity preservation",
        "- evaluation continuity preservation",
        "- fail-visible blocked states",
        "- fail-visible unsupported states",
        "- fail-visible prohibited states",
        "- fail-visible unknown states",
        "- deterministic serialization compatibility",
        "- deterministic hashing compatibility",
        "- scenarios are non-executable",
        "",
        "## Explicit Non-Execution Boundary",
        "",
        "This implementation does not add graph execution.",
        "",
        "This implementation does not add scenario execution.",
        "",
        "This implementation does not add runtime orchestration.",
        "",
        "This implementation does not add routing, scheduling, dispatch, graph traversal execution, optimization engines, recommendation systems, autonomous orchestration, runtime mutation, persistent runtime writes, execution-capable scenarios, runtime branching behavior, orchestration state machines, or runtime orchestration history.",
        "",
        "Planning scenario intelligence remains deterministic hypothetical planning evidence, not runtime orchestration branching.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _status_counts(statuses: tuple[str, ...], expected_statuses: tuple[str, ...]) -> dict[str, int]:
    counts = {status: 0 for status in expected_statuses}
    for status in statuses:
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _audit_status_count(scenario, status: str) -> int:
    return sum(
        1
        for entry in scenario.audit_trail
        if entry.scenario_status == status and entry.fail_visible and not entry.hidden
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    report = build_v3_7_graph_planning_scenarios_report(args.repo_root)
    generated_path = args.repo_root / "docs/generated/v3_7_graph_planning_scenarios_report.json"
    markdown_path = args.repo_root / "docs/migration/V3_7_GRAPH_PLANNING_SCENARIOS.md"
    generated_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    generated_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_path)


if __name__ == "__main__":
    main()
