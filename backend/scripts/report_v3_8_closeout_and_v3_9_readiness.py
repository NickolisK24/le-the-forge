"""Generate the v3.8 closeout and v3.9 readiness report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
APP_ROOT = BACKEND_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402
from runtime_coordination.v3_8_closeout_readiness_audit import (  # noqa: E402
    EXPECTED_PHASE_COUNT,
    audit_v3_8_closeout_and_v3_9_readiness,
    export_v3_8_closeout_and_v3_9_readiness_result,
)
from runtime_coordination.v3_8_closeout_readiness_models import (  # noqa: E402
    validate_v3_8_closeout_hash_stability,
    validate_v3_8_closeout_serialization_stability,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_closeout_and_v3_9_readiness_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    result = audit_v3_8_closeout_and_v3_9_readiness()
    serialization = validate_v3_8_closeout_serialization_stability(result)
    hashing = validate_v3_8_closeout_hash_stability(result)
    totals = dict(result.validation_totals)
    report = {
        "schema_version": "v3_8.closeout_and_v3_9_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_closeout_and_v3.9_readiness",
        "repo_root": str(root),
        "architectural_purpose": (
            "closeout and readiness audit for deterministic orchestration-planning "
            "coordination intelligence"
        ),
        "closeout_state": result.closeout_state,
        "v3_9_readiness_state": result.v3_9_readiness_state,
        "closeout_id": result.closeout_id,
        "explanation": result.explanation,
        "expected_phase_count": EXPECTED_PHASE_COUNT,
        "audited_phase_count": totals["audited_phase_count"],
        "generated_report_count": totals["generated_report_count"],
        "migration_documentation_count": totals["migration_documentation_count"],
        "deterministic_evidence_count": totals["deterministic_evidence_count"],
        "replay_evidence_count": totals["replay_evidence_count"],
        "rollback_evidence_count": totals["rollback_evidence_count"],
        "provenance_continuity_count": totals["provenance_continuity_count"],
        "fail_visible_state_count": totals["fail_visible_state_count"],
        "unsupported_visibility_count": totals["unsupported_visibility_count"],
        "prohibited_visibility_count": totals["prohibited_visibility_count"],
        "unknown_visibility_count": totals["unknown_visibility_count"],
        "hidden_risk_count": totals["hidden_risk_count"],
        "recommendation_language_violation_count": totals[
            "recommendation_language_violation_count"
        ],
        "optimization_language_violation_count": totals["optimization_language_violation_count"],
        "ranking_language_violation_count": totals["ranking_language_violation_count"],
        "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
        "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
        "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        "blocker_count": totals["blocker_count"],
        "warning_count": totals["warning_count"],
        "non_execution_confirmation": result.non_execution_confirmation,
        "prohibited_behavior_confirmation": result.prohibited_behavior_confirmation,
        "coordination_execution_enabled": result.coordination_execution_enabled,
        "orchestration_execution_enabled": result.orchestration_execution_enabled,
        "routing_enabled": result.routing_enabled,
        "scheduling_enabled": result.scheduling_enabled,
        "dispatch_enabled": result.dispatch_enabled,
        "traversal_enabled": result.traversal_enabled,
        "optimization_enabled": result.optimization_enabled,
        "recommendation_enabled": result.recommendation_enabled,
        "ranking_enabled": result.ranking_enabled,
        "scoring_enabled": result.scoring_enabled,
        "selection_enabled": result.selection_enabled,
        "execution_authorization_enabled": result.execution_authorization_enabled,
        "runtime_mutation_enabled": result.runtime_mutation_enabled,
        "runtime_engine_enabled": result.runtime_engine_enabled,
        "state_machine_enabled": result.state_machine_enabled,
        "callable_coordination_flow_enabled": result.callable_coordination_flow_enabled,
        "hidden_transition_enabled": result.hidden_transition_enabled,
        "silent_fallback_enabled": result.silent_fallback_enabled,
        "production_behavior_enabled": result.production_behavior_enabled,
        "audited_phases": [phase.phase_id for phase in result.audited_phase_list],
        "generated_reports": list(result.generated_report_list),
        "migration_docs": list(result.migration_doc_list),
        "blockers": list(result.blocker_list),
        "warnings": list(result.warning_list),
        "provenance_continuity_summary": dict(result.provenance_continuity_summary),
        "replay_evidence_summary": dict(result.replay_evidence_summary),
        "rollback_evidence_summary": dict(result.rollback_evidence_summary),
        "deterministic_visibility_summary": dict(result.deterministic_visibility_summary),
        "validation_totals": totals,
        "deterministic_guarantees": {
            "closeout_serialization_stable": serialization["stable"],
            "closeout_hash_stable": hashing["stable"],
            "closeout_hash": result.deterministic_closeout_hash,
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "v3_9_planning_guidance": {
            "planning_target": "deterministic orchestration-planning coordination transition intelligence",
            "planning_themes": list(result.suggested_v3_9_planning_themes),
            "non_executable_until_later_decision": True,
        },
        "closeout_record": export_v3_8_closeout_and_v3_9_readiness_result(result),
        "explicit_limitations": [
            "v3.8 closeout is audit-only",
            "v3.8 closeout does not introduce runtime behavior",
            "v3.8 closeout does not enable execution",
            "v3.8 closeout does not enable routing, scheduling, dispatch, or traversal",
            "v3.8 closeout does not enable optimization or recommendations",
            "v3.8 closeout does not enable ranking, scoring, or selection",
            "v3.8 closeout does not enable authorization",
            "v3.8 closeout does not enable runtime mutation",
            "v3.8 closeout does not enable runtime engines or state machines",
            "v3.8 closeout does not enable callable coordination flows",
            "v3.8 closeout does not enable hidden transitions or silent fallback behavior",
        ],
        "summary": {
            "closeout_state": result.closeout_state,
            "v3_9_readiness_state": result.v3_9_readiness_state,
            "audited_phase_count": totals["audited_phase_count"],
            "expected_phase_count": EXPECTED_PHASE_COUNT,
            "generated_report_count": totals["generated_report_count"],
            "migration_documentation_count": totals["migration_documentation_count"],
            "deterministic_evidence_count": totals["deterministic_evidence_count"],
            "replay_evidence_count": totals["replay_evidence_count"],
            "rollback_evidence_count": totals["rollback_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "fail_visible_state_count": totals["fail_visible_state_count"],
            "unsupported_visibility_count": totals["unsupported_visibility_count"],
            "prohibited_visibility_count": totals["prohibited_visibility_count"],
            "unknown_visibility_count": totals["unknown_visibility_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
            "blocker_count": totals["blocker_count"],
            "warning_count": totals["warning_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "non_execution_confirmation": result.non_execution_confirmation,
            "prohibited_behavior_confirmation": result.prohibited_behavior_confirmation,
            "orchestration_boundaries_enforced": totals["execution_boundary_violation_count"] == 0,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.8 Closeout and v3.9 Readiness",
        "",
        "## What v3.8 Accomplished",
        "",
        "v3.8 established deterministic orchestration-planning coordination intelligence across foundation, boundary, compatibility, evaluation, session, scenario, aggregation, integrity, and continuity certification evidence.",
        "",
        "The closeout audit verifies phase coverage, generated report coverage, migration documentation coverage, deterministic hashes, replay evidence, rollback evidence, provenance continuity, fail-visible states, and strict non-execution boundaries.",
        "",
        "## What v3.8 Did Not Enable",
        "",
        "v3.8 did not enable execution, routing, scheduling, dispatch, traversal, optimization, recommendations, ranking, scoring, selection, authorization, runtime mutation, runtime engines, state machines, callable coordination flows, hidden transitions, silent fallback behavior, or production behavior.",
        "",
        "## Why Coordination Intelligence Remains Non-Executable",
        "",
        "The v3.8 chain stores deterministic planning and audit evidence. It does not create callable runtime pathways, mutable runtime state, routing decisions, scheduling decisions, dispatch decisions, traversal behavior, or execution authorization.",
        "",
        "## Deterministic Continuity",
        "",
        f"- Audited phase count: `{report['summary']['audited_phase_count']}`",
        f"- Expected phase count: `{report['summary']['expected_phase_count']}`",
        f"- Generated report count: `{report['summary']['generated_report_count']}`",
        f"- Migration documentation count: `{report['summary']['migration_documentation_count']}`",
        f"- Deterministic evidence count: `{report['summary']['deterministic_evidence_count']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        "",
        "## Replay Rollback And Provenance",
        "",
        f"- Replay evidence count: `{report['summary']['replay_evidence_count']}`",
        f"- Rollback evidence count: `{report['summary']['rollback_evidence_count']}`",
        f"- Provenance continuity count: `{report['summary']['provenance_continuity_count']}`",
        "",
        "## Fail-Visible States",
        "",
        f"- Fail-visible state count: `{report['summary']['fail_visible_state_count']}`",
        f"- Unsupported visibility count: `{report['summary']['unsupported_visibility_count']}`",
        f"- Prohibited visibility count: `{report['summary']['prohibited_visibility_count']}`",
        f"- Unknown visibility count: `{report['summary']['unknown_visibility_count']}`",
        f"- Hidden-risk count: `{report['summary']['hidden_risk_count']}`",
        "",
        "## Closeout Classification",
        "",
        f"- Final closeout state: `{report['summary']['closeout_state']}`",
        f"- v3.9 readiness state: `{report['summary']['v3_9_readiness_state']}`",
        f"- Blocker count: `{report['summary']['blocker_count']}`",
        f"- Warning count: `{report['summary']['warning_count']}`",
        f"- Execution-boundary violation count: `{report['summary']['execution_boundary_violation_count']}`",
        "",
        "## v3.9 Architectural Direction",
        "",
        "v3.9 should target deterministic orchestration-planning coordination transition intelligence.",
        "",
        "Suggested v3.9 planning themes:",
        "",
        "- Coordination transition reasoning.",
        "- Cross-coordination continuity deltas.",
        "- Transition readiness evidence.",
        "- Transition risk visibility.",
        "- Transition provenance chains.",
        "- Transition replay and rollback safety.",
        "- Transition integrity auditing.",
        "- Transition certification.",
        "",
        "v3.9 remains non-executable unless a later architectural decision explicitly changes that boundary.",
        "",
        "## Remaining Hard Prohibitions",
        "",
        "- Execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Authorization.",
        "- Runtime mutation.",
        "- Runtime engines.",
        "- State machines.",
        "- Callable coordination flows.",
        "- Hidden transitions.",
        "- Silent fallback behavior.",
        "- Production behavior.",
        "",
        "## Deterministic Report Evidence",
        "",
        f"- Closeout hash: `{report['deterministic_guarantees']['closeout_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "generated"
        / "v3_8_closeout_and_v3_9_readiness_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_CLOSEOUT_AND_V3_9_READINESS.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_closeout_and_v3_9_readiness_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
