"""Generate the v3.7 closeout and v3.8 planning-readiness report."""

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
from app.runtime_orchestration.v3_7_closeout_readiness_audit import (  # noqa: E402
    audit_v3_7_closeout_and_v3_8_readiness,
    count_v3_7_closeout_findings_by_classification,
    export_v3_7_closeout_and_v3_8_readiness_result,
)
from app.runtime_orchestration.v3_7_closeout_readiness_models import (  # noqa: E402
    validate_v3_7_closeout_hash_stability,
    validate_v3_7_closeout_serialization_stability,
)


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_7_closeout_and_v3_8_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    result = audit_v3_7_closeout_and_v3_8_readiness()
    serialization = validate_v3_7_closeout_serialization_stability(result)
    hashing = validate_v3_7_closeout_hash_stability(result)
    report = {
        "schema_version": "v3_7.closeout_and_v3_8_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.7_closeout_and_v3.8_readiness",
        "repo_root": str(root),
        "architectural_purpose": "closeout certification and readiness auditing for deterministic orchestration planning intelligence",
        "closeout_is_non_executable": result.closeout_is_non_executable,
        "closeout_certifies_planning_intelligence_continuity_only": result.closeout_certifies_planning_intelligence_continuity_only,
        "ready_for_future_deterministic_planning_expansion": result.readiness_for_v3_8_planning,
        "runtime_execution_readiness_certified": result.runtime_execution_readiness_certified,
        "execution_authorization_enabled": result.execution_authorization_enabled,
        "orchestration_execution_enabled": result.orchestration_execution_enabled,
        "routing_enabled": result.routing_enabled,
        "scheduling_enabled": result.scheduling_enabled,
        "dispatch_enabled": result.dispatch_enabled,
        "traversal_enabled": result.traversal_enabled,
        "runtime_path_selection_enabled": result.runtime_path_selection_enabled,
        "scenario_execution_selection_enabled": result.scenario_execution_selection_enabled,
        "execution_recommendation_enabled": result.execution_recommendation_enabled,
        "optimization_for_execution_enabled": result.optimization_for_execution_enabled,
        "callable_execution_flow_enabled": result.callable_execution_flow_enabled,
        "runtime_orchestration_engine_enabled": result.runtime_orchestration_engine_enabled,
        "runtime_mutation_enabled": result.runtime_mutation_enabled,
        "persistent_runtime_writes_enabled": result.persistent_runtime_writes_enabled,
        "autonomous_orchestration_enabled": result.autonomous_orchestration_enabled,
        "total_phases_audited": result.total_phases_audited,
        "continuity_validation_totals": dict(result.continuity_validation_totals),
        "replay_rollback_totals": dict(result.replay_rollback_totals),
        "provenance_explainability_totals": dict(result.provenance_explainability_totals),
        "integrity_certification_totals": {
            "integrity_continuity": result.continuity_validation_totals["integrity_continuity"],
            "certification_continuity": result.continuity_validation_totals["certification_continuity"],
        },
        "execution_boundary_audit_totals": dict(result.execution_boundary_audit_totals),
        "hidden_risk_totals": dict(result.hidden_risk_totals),
        "validation_totals": dict(result.validation_totals),
        "finding_totals": {
            "finding_count": len(result.findings),
            "finding_classification_counts": count_v3_7_closeout_findings_by_classification(result.findings),
            "blocking_finding_count": sum(1 for finding in result.findings if finding.blocks_closeout),
            "fail_visible_finding_count": sum(1 for finding in result.findings if finding.fail_visible and not finding.hidden),
        },
        "deterministic_guarantees": {
            **dict(result.deterministic_guarantees),
            "closeout_serialization_stable": serialization["stable"],
            "closeout_hash_stable": hashing["stable"],
            "closeout_hash": result.deterministic_closeout_hash,
        },
        "non_executable_confirmation": result.closeout_is_non_executable,
        "no_execution_authorization_confirmation": not result.execution_authorization_enabled,
        "readiness_for_v3_8_planning_confirmation": result.readiness_for_v3_8_planning,
        "no_runtime_readiness_confirmation": not result.runtime_execution_readiness_certified,
        "routing_scheduling_dispatch_traversal_prohibited_confirmation": not any(
            (result.routing_enabled, result.scheduling_enabled, result.dispatch_enabled, result.traversal_enabled)
        ),
        "closeout_record": export_v3_7_closeout_and_v3_8_readiness_result(result),
        "explicit_limitations": [
            "v3.7 is non-executable",
            "v3.7 does not enable orchestration execution",
            "v3.7 does not enable routing, scheduling, dispatch, or traversal",
            "v3.7 does not enable orchestration optimization",
            "v3.7 does not enable execution authorization",
            "v3.7 established deterministic orchestration planning intelligence only",
            "v3.8 may expand planning intelligence but may not enable runtime orchestration execution",
        ],
        "summary": {
            "closeout_status": result.closeout_status,
            "v3_8_readiness_classification": result.v3_8_readiness_classification,
            "total_phases_audited": result.total_phases_audited,
            "validation_status": result.validation_totals["validation_status"],
            "validation_error_count": result.validation_totals["error_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "continuity_verified": result.continuity_validation_totals["certification_continuity"],
            "execution_boundary_verified": result.execution_boundary_audit_totals["execution_boundary_preserved"],
            "replay_verified": result.replay_rollback_totals["replay_safe"],
            "rollback_verified": result.replay_rollback_totals["rollback_safe"],
            "provenance_verified": result.provenance_explainability_totals["provenance_safe"],
            "explainability_verified": result.provenance_explainability_totals["explainability_safe"],
            "non_executable_verified": result.closeout_is_non_executable,
            "no_execution_authorization_verified": not result.execution_authorization_enabled,
            "no_runtime_readiness_verified": not result.runtime_execution_readiness_certified,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.7 Closeout and v3.8 Readiness",
        "",
        "## Architectural Purpose",
        "",
        "v3.7 closeout validates deterministic orchestration planning intelligence continuity across graph foundations, governance boundaries, compatibility reasoning, evaluation reasoning, planning sessions, planning scenarios, intelligence aggregation, integrity enforcement, and continuity certification.",
        "",
        "v3.7 is NON-executable.",
        "",
        "v3.7 does NOT enable orchestration execution.",
        "",
        "v3.7 does NOT enable routing, scheduling, dispatch, or traversal.",
        "",
        "v3.7 does NOT enable orchestration optimization.",
        "",
        "v3.7 does NOT enable execution authorization.",
        "",
        "v3.7 established deterministic orchestration planning intelligence ONLY.",
        "",
        "v3.8 may expand planning intelligence but may NOT enable runtime orchestration execution.",
        "",
        "## Planning Intelligence Maturity vs Runtime Orchestration Capability",
        "",
        "Planning intelligence maturity means deterministic, replay-safe, rollback-safe, provenance-safe, explainability-safe evidence that describes structural planning continuity.",
        "",
        "Runtime orchestration capability would mean executable behavior, runtime routing, scheduling, dispatch, traversal, path selection, optimization, recommendation, or callable control systems. This closeout does not create those capabilities.",
        "",
        "## Closeout Totals",
        "",
        f"- Closeout status: `{report['summary']['closeout_status']}`",
        f"- v3.8 readiness classification: `{report['summary']['v3_8_readiness_classification']}`",
        f"- Total phases audited: `{report['total_phases_audited']}`",
        f"- Validation errors: `{report['validation_totals']['error_count']}`",
        f"- Execution-boundary violations: `{report['execution_boundary_audit_totals']['execution_boundary_violation_count']}`",
        f"- Hidden risk detected: `{report['hidden_risk_totals']['hidden_risk_detected']}`",
        f"- Serialization stable: `{report['deterministic_guarantees']['closeout_serialization_stable']}`",
        f"- Hash stable: `{report['deterministic_guarantees']['closeout_hash_stable']}`",
        "",
        "## Explicit Non-Execution Guarantees",
        "",
        "- Runtime execution readiness is not certified.",
        "- Execution authorization remains disabled.",
        "- Orchestration execution remains disabled.",
        "- Routing remains disabled.",
        "- Scheduling remains disabled.",
        "- Dispatch remains disabled.",
        "- Traversal remains disabled.",
        "- Runtime path selection remains disabled.",
        "- Scenario execution selection remains disabled.",
        "- Optimization for execution remains disabled.",
        "- Recommendation to execute remains disabled.",
        "- Callable execution flows remain disabled.",
        "- Runtime orchestration engines remain disabled.",
        "",
        "## Generated Evidence",
        "",
        f"- Deterministic report hash: `{report['deterministic_report_hash']}`",
        f"- Deterministic closeout hash: `{report['deterministic_guarantees']['closeout_hash']}`",
        f"- Certification hash: `{report['deterministic_guarantees']['certification_hash']}`",
        f"- Certification validation hash: `{report['deterministic_guarantees']['certification_validation_hash']}`",
        f"- Certification audit hash: `{report['deterministic_guarantees']['certification_audit_hash']}`",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "generated" / "v3_7_closeout_and_v3_8_readiness_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "docs" / "migration" / "V3_7_CLOSEOUT_AND_V3_8_READINESS.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_7_closeout_and_v3_8_readiness_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
