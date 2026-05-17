"""Generate the v3.8 coordination continuity certification report."""

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

from runtime_coordination.coordination_certification_models import (  # noqa: E402
    CERTIFICATION_STATE_BLOCKED,
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_EXPERIMENTAL,
    CERTIFICATION_STATE_NON_EXECUTABLE,
    CERTIFICATION_STATE_PLANNING_ONLY,
    CERTIFICATION_STATE_PROHIBITED,
    CERTIFICATION_STATE_UNCERTIFIED,
    CERTIFICATION_STATE_UNKNOWN,
    CERTIFICATION_STATE_UNSUPPORTED,
    hash_v3_8_certification_audit,
    validate_v3_8_certification_hash_stability,
    validate_v3_8_certification_serialization_stability,
)
from runtime_coordination.coordination_continuity_certification import (  # noqa: E402
    certify_v3_8_coordination_continuity,
    export_v3_8_coordination_continuity_certification_audit,
)
from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_continuity_certification_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = certify_v3_8_coordination_continuity()
    serialization = validate_v3_8_certification_serialization_stability(audit)
    hashing = validate_v3_8_certification_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_continuity_certification_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_continuity_certification",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic certification-only continuity evidence across foundation, boundary, "
            "compatibility, evaluation, session, scenario, aggregation, and integrity evidence"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "source_compatibility_audit_id": audit.source_compatibility_audit_id,
        "source_evaluation_audit_id": audit.source_evaluation_audit_id,
        "source_session_audit_id": audit.source_session_audit_id,
        "source_scenario_audit_id": audit.source_scenario_audit_id,
        "source_aggregation_audit_id": audit.source_aggregation_audit_id,
        "source_integrity_audit_id": audit.source_integrity_audit_id,
        "immutable_certification_evidence_records": audit.immutable_certification_evidence_records,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "runtime_certification_engine_enabled": audit.runtime_certification_engine_enabled,
        "runtime_enforcement_engine_enabled": audit.runtime_enforcement_engine_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "ranking_enabled": audit.ranking_enabled,
        "scoring_enabled": audit.scoring_enabled,
        "selection_enabled": audit.selection_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "certification_runtime_state_machine_enabled": audit.certification_runtime_state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "certification_totals": {
            "certification_result_count": totals["certification_result_count"],
            "certified_count": totals["certified_count"],
            "uncertified_count": totals["uncertified_count"],
            "blocked_count": totals["blocked_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "foundation_context_count": totals["foundation_context_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "evaluation_context_count": totals["evaluation_context_count"],
            "session_context_count": totals["session_context_count"],
            "scenario_context_count": totals["scenario_context_count"],
            "aggregation_context_count": totals["aggregation_context_count"],
            "integrity_context_count": totals["integrity_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "continuity_certification_failure_count": totals[
                "continuity_certification_failure_count"
            ],
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
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "certified_visible": totals["certified_visible_count"] == totals["certified_count"],
            "uncertified_fail_visible": totals["fail_visible_uncertified_count"]
            == totals["uncertified_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "continuity_certification_failure_count": totals[
                "continuity_certification_failure_count"
            ],
            "hidden_risk_count": totals["hidden_risk_count"],
        },
        "context_guarantees": {
            "foundation_context_count": totals["foundation_context_count"],
            "foundation_context_certified_count": totals["foundation_context_certified_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "boundary_context_certified_count": totals["boundary_context_certified_count"],
            "compatibility_context_count": totals["compatibility_context_count"],
            "compatibility_context_certified_count": totals[
                "compatibility_context_certified_count"
            ],
            "evaluation_context_count": totals["evaluation_context_count"],
            "evaluation_context_certified_count": totals["evaluation_context_certified_count"],
            "session_context_count": totals["session_context_count"],
            "session_context_certified_count": totals["session_context_certified_count"],
            "scenario_context_count": totals["scenario_context_count"],
            "scenario_context_certified_count": totals["scenario_context_certified_count"],
            "aggregation_context_count": totals["aggregation_context_count"],
            "aggregation_context_certified_count": totals["aggregation_context_certified_count"],
            "integrity_context_count": totals["integrity_context_count"],
            "integrity_context_certified_count": totals["integrity_context_certified_count"],
            "all_results_certify_context": (
                totals["foundation_context_count"]
                == totals["boundary_context_count"]
                == totals["compatibility_context_count"]
                == totals["evaluation_context_count"]
                == totals["session_context_count"]
                == totals["scenario_context_count"]
                == totals["aggregation_context_count"]
                == totals["integrity_context_count"]
                == totals["certification_result_count"]
            ),
        },
        "continuity_guarantees": {
            "explainability_continuity_count": totals["explainability_continuity_count"],
            "non_execution_continuity_count": totals["non_execution_continuity_count"],
            "fail_visible_state_continuity_count": totals["fail_visible_state_continuity_count"],
            "continuity_certification_failure_count": totals[
                "continuity_certification_failure_count"
            ],
            "certification_failure_code_count": totals["certification_failure_code_count"],
        },
        "deterministic_guarantees": {
            "certification_serialization_stable": serialization["stable"],
            "certification_hash_stable": hashing["stable"],
            "certification_hash": hash_v3_8_certification_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["certification_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["certification_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["certification_result_count"],
        },
        "certification_record_guarantees": {
            "immutable_certification_evidence_record_count": totals[
                "immutable_certification_evidence_record_count"
            ],
            "all_certifications_are_immutable_evidence_records": totals[
                "immutable_certification_evidence_record_count"
            ]
            == totals["certification_result_count"],
            "runtime_certification_state_machine_count": totals[
                "runtime_certification_state_machine_count"
            ],
            "certifications_are_not_runtime_state_machines": totals[
                "runtime_certification_state_machine_count"
            ]
            == 0,
        },
        "contamination_guarantees": {
            "recommendation_language_violation_count": totals[
                "recommendation_language_violation_count"
            ],
            "optimization_language_violation_count": totals[
                "optimization_language_violation_count"
            ],
            "ranking_language_violation_count": totals["ranking_language_violation_count"],
            "scoring_behavior_violation_count": totals["scoring_behavior_violation_count"],
            "selection_behavior_violation_count": totals["selection_behavior_violation_count"],
            "recommendation_behavior_violation_count": totals[
                "recommendation_behavior_violation_count"
            ],
            "optimization_behavior_violation_count": totals[
                "optimization_behavior_violation_count"
            ],
            "ranking_behavior_violation_count": totals["ranking_behavior_violation_count"],
        },
        "non_execution_guarantees": {
            "coordination_execution_absent": not audit.coordination_execution_enabled,
            "orchestration_execution_absent": not audit.orchestration_execution_enabled,
            "runtime_certification_engine_absent": not audit.runtime_certification_engine_enabled,
            "runtime_enforcement_engine_absent": not audit.runtime_enforcement_engine_enabled,
            "routing_absent": not audit.routing_enabled,
            "scheduling_absent": not audit.scheduling_enabled,
            "dispatch_absent": not audit.dispatch_enabled,
            "traversal_execution_absent": not audit.traversal_execution_enabled,
            "optimization_absent": not audit.optimization_enabled,
            "recommendation_absent": not audit.recommendation_enabled,
            "ranking_absent": not audit.ranking_enabled,
            "scoring_absent": not audit.scoring_enabled,
            "selection_absent": not audit.selection_enabled,
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "certification_runtime_state_machine_absent": not audit.certification_runtime_state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "coordination_continuity_certification": export_v3_8_coordination_continuity_certification_audit(
            audit
        ),
        "certification_state_semantics": {
            CERTIFICATION_STATE_CERTIFIED: (
                "deterministic continuity evidence satisfies certification requirements"
            ),
            CERTIFICATION_STATE_UNCERTIFIED: (
                "deterministic evidence does not satisfy certification requirements"
            ),
            CERTIFICATION_STATE_BLOCKED: "certification is blocked by prior coordination findings",
            CERTIFICATION_STATE_UNSUPPORTED: "certification includes unsupported coordination states",
            CERTIFICATION_STATE_PROHIBITED: "certification includes prohibited coordination states",
            CERTIFICATION_STATE_UNKNOWN: "insufficient deterministic evidence exists",
            CERTIFICATION_STATE_EXPERIMENTAL: "explicitly labeled experimental certification only",
            CERTIFICATION_STATE_PLANNING_ONLY: "certification-only, no runtime execution",
            CERTIFICATION_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 9 is certification-only",
            "v3.8 Phase 9 does not enable runtime certification engines",
            "v3.8 Phase 9 does not enable runtime enforcement engines",
            "v3.8 Phase 9 does not enable coordination execution",
            "v3.8 Phase 9 does not enable orchestration execution",
            "v3.8 Phase 9 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 9 does not enable optimization or recommendations",
            "v3.8 Phase 9 does not enable ranking, scoring, or selection",
            "v3.8 Phase 9 does not enable authorization",
            "v3.8 Phase 9 does not enable runtime engines or state machines",
            "v3.8 Phase 9 does not enable callable coordination flows",
            "v3.8 Phase 9 does not enable persistent runtime mutation",
            "v3.8 Phase 9 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "certification_result_count": totals["certification_result_count"],
            "continuity_certification_failure_count": totals[
                "continuity_certification_failure_count"
            ],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "certified_visible": totals["certified_visible_count"] == totals["certified_count"],
            "uncertified_fail_visible": totals["fail_visible_uncertified_count"]
            == totals["uncertified_count"],
            "blocked_fail_visible": totals["fail_visible_blocked_count"] == totals["blocked_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "foundation_context_verified": totals["foundation_context_count"]
            == totals["certification_result_count"],
            "boundary_context_verified": totals["boundary_context_count"]
            == totals["certification_result_count"],
            "compatibility_context_verified": totals["compatibility_context_count"]
            == totals["certification_result_count"],
            "evaluation_context_verified": totals["evaluation_context_count"]
            == totals["certification_result_count"],
            "session_context_verified": totals["session_context_count"]
            == totals["certification_result_count"],
            "scenario_context_verified": totals["scenario_context_count"]
            == totals["certification_result_count"],
            "aggregation_context_verified": totals["aggregation_context_count"]
            == totals["certification_result_count"],
            "integrity_context_verified": totals["integrity_context_count"]
            == totals["certification_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"]
            == totals["certification_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"]
            == totals["certification_result_count"],
            "provenance_verified": totals["provenance_continuity_count"]
            == totals["certification_result_count"],
            "immutable_certification_evidence_records_verified": totals[
                "immutable_certification_evidence_record_count"
            ]
            == totals["certification_result_count"],
            "runtime_certification_state_machine_count": totals[
                "runtime_certification_state_machine_count"
            ],
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
            "non_executable_verified": audit.non_executable,
            "orchestration_boundaries_enforced": totals["execution_boundary_violation_count"] == 0,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.8 Coordination Continuity Certification",
        "",
        "## What Phase 9 Adds",
        "",
        "Phase 9 adds deterministic coordination continuity certification across foundation, boundary, compatibility, evaluation, session, scenario, aggregation, and integrity evidence.",
        "",
        "Certification records are immutable audit and certification evidence records. They certify continuity without enabling runtime behavior.",
        "",
        "## Certification Boundaries",
        "",
        "Continuity certification differs from execution because it only records deterministic certification evidence.",
        "",
        "Continuity certification differs from runtime enforcement because it does not run an enforcement or certification engine.",
        "",
        "## Context Preservation Across Phases 1-8",
        "",
        f"- Foundation-context count: `{report['context_guarantees']['foundation_context_count']}`",
        f"- Boundary-context count: `{report['context_guarantees']['boundary_context_count']}`",
        f"- Compatibility-context count: `{report['context_guarantees']['compatibility_context_count']}`",
        f"- Evaluation-context count: `{report['context_guarantees']['evaluation_context_count']}`",
        f"- Session-context count: `{report['context_guarantees']['session_context_count']}`",
        f"- Scenario-context count: `{report['context_guarantees']['scenario_context_count']}`",
        f"- Aggregation-context count: `{report['context_guarantees']['aggregation_context_count']}`",
        f"- Integrity-context count: `{report['context_guarantees']['integrity_context_count']}`",
        f"- All results certify context: `{report['context_guarantees']['all_results_certify_context']}`",
        "",
        "## Certification States",
        "",
        "- `certified` means deterministic continuity evidence satisfies certification requirements.",
        "- `uncertified` means deterministic evidence does not satisfy certification requirements.",
        "- `blocked` means certification is blocked by prior coordination findings.",
        "- `unsupported` means certification includes unsupported coordination states.",
        "- `prohibited` means certification includes prohibited coordination states.",
        "- `unknown` means insufficient deterministic evidence exists.",
        "- `experimental` means explicitly labeled experimental certification only.",
        "- `planning_only` means certification-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Certified State Differences",
        "",
        "Uncertified records contain explicit certification failure codes.",
        "",
        "Blocked records are stopped by prior coordination findings.",
        "",
        "Unsupported records include unsupported coordination states.",
        "",
        "Prohibited records include intentionally forbidden coordination states.",
        "",
        "Unknown records lack sufficient deterministic evidence.",
        "",
        "All non-certified states remain fail-visible.",
        "",
        "## Certification Failure Visibility",
        "",
        "Certification failure visibility keeps failed foundation, boundary, compatibility, evaluation, session, scenario, aggregation, integrity, provenance, replay, rollback, explainability, non-execution, and fail-visible continuity checks explicit.",
        "",
        f"- Continuity-certification failure count: `{report['certification_totals']['continuity_certification_failure_count']}`",
        f"- Hidden-risk count: `{report['certification_totals']['hidden_risk_count']}`",
        "",
        "## Certification Totals",
        "",
        f"- Certification result count: `{report['certification_totals']['certification_result_count']}`",
        f"- Certified count: `{report['certification_totals']['certified_count']}`",
        f"- Uncertified count: `{report['certification_totals']['uncertified_count']}`",
        f"- Blocked count: `{report['certification_totals']['blocked_count']}`",
        f"- Unsupported count: `{report['certification_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['certification_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['certification_totals']['unknown_count']}`",
        f"- Experimental count: `{report['certification_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['certification_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['certification_totals']['non_executable_count']}`",
        f"- Execution-boundary violations: `{report['certification_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Certified visible: `{report['visibility_guarantees']['certified_visible']}`",
        f"- Uncertified fail-visible: `{report['visibility_guarantees']['uncertified_fail_visible']}`",
        f"- Blocked fail-visible: `{report['visibility_guarantees']['blocked_fail_visible']}`",
        f"- Unsupported fail-visible: `{report['visibility_guarantees']['unsupported_fail_visible']}`",
        f"- Prohibited fail-visible: `{report['visibility_guarantees']['prohibited_fail_visible']}`",
        f"- Unknown fail-visible: `{report['visibility_guarantees']['unknown_fail_visible']}`",
        "",
        "## Replay Rollback And Provenance",
        "",
        f"- Replay-safe evidence count: `{report['replay_guarantees']['replay_safe_evidence_count']}`",
        f"- All results have replay evidence: `{report['replay_guarantees']['all_results_have_replay_evidence']}`",
        f"- Rollback-safe evidence count: `{report['rollback_guarantees']['rollback_safe_evidence_count']}`",
        f"- All results have rollback evidence: `{report['rollback_guarantees']['all_results_have_rollback_evidence']}`",
        f"- Provenance continuity count: `{report['provenance_guarantees']['provenance_continuity_count']}`",
        f"- All results preserve provenance: `{report['provenance_guarantees']['all_results_preserve_provenance']}`",
        "",
        "## Deterministic Evidence",
        "",
        f"- Audit status: `{report['summary']['audit_status']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Certification hash: `{report['deterministic_guarantees']['certification_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Why This Remains Non-Executable",
        "",
        f"- Runtime certification engine absent: `{report['non_execution_guarantees']['runtime_certification_engine_absent']}`",
        f"- Runtime enforcement engine absent: `{report['non_execution_guarantees']['runtime_enforcement_engine_absent']}`",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Recommendation absent: `{report['non_execution_guarantees']['recommendation_absent']}`",
        f"- Optimization absent: `{report['non_execution_guarantees']['optimization_absent']}`",
        f"- Ranking absent: `{report['non_execution_guarantees']['ranking_absent']}`",
        f"- Scoring absent: `{report['non_execution_guarantees']['scoring_absent']}`",
        f"- Selection absent: `{report['non_execution_guarantees']['selection_absent']}`",
        f"- State machine absent: `{report['non_execution_guarantees']['state_machine_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 9 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Runtime certification engines.",
        "- Runtime enforcement engines.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Ranking.",
        "- Scoring.",
        "- Selection.",
        "- Authorization.",
        "- Runtime engines.",
        "- State machines.",
        "- Runtime mutation.",
        "- Callable coordination flows.",
        "- Hidden transitions.",
        "- Silent fallback logic.",
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
        / "v3_8_coordination_continuity_certification_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_CONTINUITY_CERTIFICATION.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_continuity_certification_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
