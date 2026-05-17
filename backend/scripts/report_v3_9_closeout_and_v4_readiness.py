"""Generate the v3.9 closeout and v4.0 readiness report."""

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

from runtime_transition.v3_9_closeout_readiness_audit import (  # noqa: E402
    V3_9_PHASE_SPECS,
    audit_v3_9_closeout_readiness,
    default_v3_9_closeout_readiness_input,
)
from runtime_transition.v3_9_closeout_readiness_models import (  # noqa: E402
    V3_9_CLOSEOUT_READY_FOR_V4_PLANNING,
    V3_9_CLOSEOUT_WITH_WARNINGS,
    V3_9_NOT_READY_FOR_V4_PLANNING,
    V39CloseoutReadinessReport,
    export_v3_9_closeout_readiness_report,
)


DETERMINISTIC_GENERATED_AT = "2026-05-17T00:00:00+00:00"
REQUIRED_CLOSEOUT_SENTENCE = (
    "v3.9 is closed out as deterministic transition intelligence only. It does NOT enable orchestration "
    "execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, "
    "selection, authorization, approval, remediation, repair, or runtime mutation."
)


def build_v3_9_closeout_and_v4_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    closeout = audit_v3_9_closeout_readiness(default_v3_9_closeout_readiness_input(root))
    exported = export_v3_9_closeout_readiness_report(closeout)
    summary = closeout.summary
    report = {
        "schema_version": "v3_9.closeout_and_v4_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.9_phase_10_closeout_and_v4_readiness",
        "closeout_scope": "full_v3_9_transition_intelligence_chain",
        "audit_only": True,
        "readiness_only": True,
        "final_closeout_classification": summary.final_closeout_classification,
        "v4_0_readiness_classification": summary.v4_readiness_classification,
        "v4_0_readiness_boundary": (
            "EpochForge is ready to plan the next version from a deterministic, certified, "
            "transition-intelligence foundation without enabling runtime behavior."
        ),
        "v4_0_readiness_does_not_mean": "EpochForge is ready to execute orchestration.",
        "phase_evidence": exported["phase_evidence"],
        "findings": exported["findings"],
        "required_phase_coverage": [
            {
                "phase_id": spec.phase_id,
                "phase_name": spec.phase_name,
                "report_path": spec.report_path,
                "migration_doc_path": spec.migration_doc_path,
                "status_field": spec.status_field,
                "expected_status": spec.expected_status,
                "required_count_fields": list(spec.required_count_fields),
            }
            for spec in V3_9_PHASE_SPECS
        ],
        "summary": {
            "final_closeout_classification": summary.final_closeout_classification,
            "v4_0_readiness_classification": summary.v4_readiness_classification,
            "phase_evidence_count": summary.phase_evidence_count,
            "generated_report_count": summary.generated_report_count,
            "migration_doc_count": summary.migration_doc_count,
            "missing_report_count": summary.missing_report_count,
            "missing_doc_count": summary.missing_doc_count,
            "validation_error_count": summary.validation_error_count,
            "blocker_count": summary.blocker_count,
            "warning_count": summary.warning_count,
            "hidden_behavior_count": summary.hidden_behavior_count,
            "hidden_finding_count": summary.hidden_finding_count,
            "hidden_risk_count": summary.hidden_risk_count,
            "hidden_non_safe_state_count": summary.hidden_non_safe_state_count,
            "execution_capability_enabled_count": summary.execution_capability_enabled_count,
            "orchestration_capability_introduced_count": summary.orchestration_capability_introduced_count,
            "recommendation_ranking_scoring_selection_capability_introduced_count": (
                summary.recommendation_ranking_scoring_selection_capability_introduced_count
            ),
            "authorization_approval_remediation_repair_capability_introduced_count": (
                summary.authorization_approval_remediation_repair_capability_introduced_count
            ),
            "runtime_mutation_capability_introduced_count": summary.runtime_mutation_capability_introduced_count,
            "integrity_enforcement_status": summary.integrity_enforcement_status,
            "continuity_certification_status": summary.continuity_certification_status,
            "deterministic_summary_hash": summary.deterministic_summary_hash,
        },
        "deterministic_guarantee_summary": {
            "stable_phase_evidence_order": tuple(item["phase_id"] for item in exported["phase_evidence"])
            == tuple(sorted(item["phase_id"] for item in exported["phase_evidence"])),
            "stable_finding_order": tuple(item["deterministic_order"] for item in exported["findings"])
            == tuple(sorted(item["deterministic_order"] for item in exported["findings"])),
            "deterministic_closeout_hash": closeout.deterministic_report_hash,
            "deterministic_summary_hash": summary.deterministic_summary_hash,
            "phase_1_to_9_reports_audited": summary.phase_evidence_count == len(V3_9_PHASE_SPECS),
            "all_reports_are_json_objects": summary.generated_report_count == len(V3_9_PHASE_SPECS),
            "all_migration_docs_present": summary.migration_doc_count == len(V3_9_PHASE_SPECS),
            "validation_errors_absent": summary.validation_error_count == 0,
            "report_level_capability_leakage_absent": (
                summary.execution_capability_enabled_count
                + summary.orchestration_capability_introduced_count
                + summary.recommendation_ranking_scoring_selection_capability_introduced_count
                + summary.authorization_approval_remediation_repair_capability_introduced_count
                + summary.runtime_mutation_capability_introduced_count
            )
            == 0,
        },
        "non_execution_guarantees": {
            "orchestration_execution_enabled": closeout.orchestration_execution_enabled,
            "transition_execution_enabled": closeout.transition_execution_enabled,
            "graph_traversal_enabled": closeout.graph_traversal_enabled,
            "routing_enabled": closeout.routing_enabled,
            "scheduling_enabled": closeout.scheduling_enabled,
            "dispatch_enabled": closeout.dispatch_enabled,
            "runtime_orchestration_engine_enabled": closeout.runtime_orchestration_engine_enabled,
            "runtime_mutation_enabled": closeout.runtime_mutation_enabled,
            "authorization_enabled": closeout.authorization_enabled,
            "approval_enabled": closeout.approval_enabled,
            "optimization_enabled": closeout.optimization_enabled,
            "recommendation_enabled": closeout.recommendation_enabled,
            "ranking_enabled": closeout.ranking_enabled,
            "scoring_enabled": closeout.scoring_enabled,
            "selection_enabled": closeout.selection_enabled,
            "remediation_enabled": closeout.remediation_enabled,
            "repair_enabled": closeout.repair_enabled,
            "silent_correction_enabled": closeout.silent_correction_enabled,
            "hidden_fallback_enabled": closeout.hidden_fallback_enabled,
            "v4_runtime_behavior_enabled": closeout.v4_runtime_behavior_enabled,
        },
        "v4_0_planning_boundaries": {
            "deterministic_evidence_required": True,
            "provenance_continuity_required": True,
            "replay_continuity_required": True,
            "rollback_continuity_required": True,
            "explainability_continuity_required": True,
            "visibility_continuity_required": True,
            "integrity_continuity_required": True,
            "non_execution_boundaries_required": True,
            "hidden_recommendation_ranking_scoring_selection_behavior_allowed": False,
            "runtime_mutation_behavior_allowed": False,
        },
        "readiness_semantics": {
            V3_9_CLOSEOUT_READY_FOR_V4_PLANNING: "all v3.9 evidence is complete with no warnings",
            V3_9_CLOSEOUT_WITH_WARNINGS: "v3.9 is complete with expected fail-visible warnings and v4.0 planning remains safe",
            V3_9_NOT_READY_FOR_V4_PLANNING: "v3.9 evidence exists but deterministic or safety guarantees fail",
        },
        "closeout_report": exported,
    }
    report["deterministic_report_hash"] = _hash_report(report)
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v3.9 Closeout and v4.0 Readiness",
        "",
        "## Closeout Status",
        "",
        f"- Final closeout classification: `{summary['final_closeout_classification']}`",
        f"- v4.0 readiness classification: `{summary['v4_0_readiness_classification']}`",
        f"- Phase evidence count: `{summary['phase_evidence_count']}`",
        f"- Generated report count: `{summary['generated_report_count']}`",
        f"- Migration doc count: `{summary['migration_doc_count']}`",
        f"- Validation error count: `{summary['validation_error_count']}`",
        f"- Warning count: `{summary['warning_count']}`",
        "",
        REQUIRED_CLOSEOUT_SENTENCE,
        "",
        "## What v3.9 Accomplished",
        "",
        "v3.9 established a deterministic transition intelligence chain covering transition foundations, boundary intelligence, compatibility intelligence, evaluation intelligence, session intelligence, scenario intelligence, intelligence aggregation, integrity enforcement, and continuity certification.",
        "",
        "## What v3.9 Did Not Enable",
        "",
        "v3.9 did not enable execution, traversal, routing, scheduling, dispatch, optimization, recommendation, ranking, scoring, selection, authorization, approval, remediation, repair, runtime mutation, production behavior, silent correction, or hidden fallback.",
        "",
        "## Complete Transition Intelligence Chain",
        "",
    ]
    for phase in report["required_phase_coverage"]:
        lines.append(f"- `{phase['phase_id']}`: {phase['phase_name']} -> `{phase['report_path']}`")
    lines.extend(
        [
            "",
            "## v4.0 Planning Readiness",
            "",
            "v4.0 readiness means EpochForge is ready to plan the next version from a deterministic, certified, transition-intelligence foundation.",
            "",
            "It does not mean EpochForge is ready to execute orchestration.",
            "",
            "## Remaining Warnings",
            "",
            "Fail-visible warnings remain descriptive evidence. They do not enable prohibited behavior and do not silently authorize runtime behavior.",
            "",
            f"- Hidden behavior count: `{summary['hidden_behavior_count']}`",
            f"- Hidden finding count: `{summary['hidden_finding_count']}`",
            f"- Hidden risk count: `{summary['hidden_risk_count']}`",
            f"- Hidden non-safe state count: `{summary['hidden_non_safe_state_count']}`",
            "",
            "## Non-Execution Guarantees",
            "",
            "- Orchestration execution remains prohibited.",
            "- Transition execution remains prohibited.",
            "- Graph traversal remains prohibited.",
            "- Routing remains prohibited.",
            "- Scheduling remains prohibited.",
            "- Dispatch remains prohibited.",
            "- Runtime orchestration engines remain prohibited.",
            "- Authorization and approval remain prohibited.",
            "- Remediation and repair remain prohibited.",
            "- Runtime mutation remains prohibited.",
            "",
            "## Non-Recommendation Guarantees",
            "",
            "- Recommendation behavior remains prohibited.",
            "- Ranking behavior remains prohibited.",
            "- Scoring behavior remains prohibited.",
            "- Selection behavior remains prohibited.",
            "- Optimization behavior remains prohibited.",
            "- Hidden preference or prioritization behavior remains prohibited.",
            "",
            "## Required v4.0 Boundaries",
            "",
            "- Preserve deterministic evidence.",
            "- Preserve provenance continuity.",
            "- Preserve replay continuity.",
            "- Preserve rollback continuity.",
            "- Preserve explainability continuity.",
            "- Preserve visibility continuity.",
            "- Preserve integrity continuity.",
            "- Preserve non-execution boundaries.",
            "- Preserve no hidden recommendation, ranking, scoring, or selection behavior.",
            "- Preserve no runtime mutation behavior.",
            "",
            "## Generated Evidence",
            "",
            "- JSON report: `docs/generated/v3_9_closeout_and_v4_readiness_report.json`",
            "- This migration note: `docs/migration/V3_9_CLOSEOUT_AND_V4_READINESS.md`",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _hash_report(report: dict[str, Any]) -> str:
    from runtime_transition.transition_foundation_hashing import deterministic_hash

    return deterministic_hash({key: value for key, value in report.items() if key != "deterministic_report_hash"})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_9_closeout_and_v4_readiness_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_9_CLOSEOUT_AND_V4_READINESS.md"),
    )
    args = parser.parse_args()
    report = build_v3_9_closeout_and_v4_readiness_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
