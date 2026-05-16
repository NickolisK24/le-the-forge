"""Generate the v3.8 coordination compatibility reasoning report."""

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

from runtime_coordination.coordination_compatibility_models import (  # noqa: E402
    COMPATIBILITY_STATE_COMPATIBLE,
    COMPATIBILITY_STATE_EXPERIMENTAL,
    COMPATIBILITY_STATE_INCOMPATIBLE,
    COMPATIBILITY_STATE_NON_EXECUTABLE,
    COMPATIBILITY_STATE_PLANNING_ONLY,
    COMPATIBILITY_STATE_PROHIBITED,
    COMPATIBILITY_STATE_UNKNOWN,
    COMPATIBILITY_STATE_UNSUPPORTED,
    hash_v3_8_compatibility_audit,
    validate_v3_8_compatibility_hash_stability,
    validate_v3_8_compatibility_serialization_stability,
)
from runtime_coordination.coordination_compatibility_reasoning import (  # noqa: E402
    export_v3_8_coordination_compatibility_reasoning_audit,
    reason_v3_8_coordination_compatibility,
)
from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_compatibility_reasoning_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = reason_v3_8_coordination_compatibility()
    serialization = validate_v3_8_compatibility_serialization_stability(audit)
    hashing = validate_v3_8_compatibility_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_compatibility_reasoning_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_compatibility_reasoning",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic boundary-aware compatibility reasoning for orchestration-planning coordination"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
        "source_boundary_audit_id": audit.source_boundary_audit_id,
        "non_executable": audit.non_executable,
        "coordination_execution_enabled": audit.coordination_execution_enabled,
        "orchestration_execution_enabled": audit.orchestration_execution_enabled,
        "routing_enabled": audit.routing_enabled,
        "scheduling_enabled": audit.scheduling_enabled,
        "dispatch_enabled": audit.dispatch_enabled,
        "traversal_execution_enabled": audit.traversal_execution_enabled,
        "optimization_enabled": audit.optimization_enabled,
        "recommendation_enabled": audit.recommendation_enabled,
        "execution_authorization_enabled": audit.execution_authorization_enabled,
        "runtime_engine_enabled": audit.runtime_engine_enabled,
        "state_machine_enabled": audit.state_machine_enabled,
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "compatibility_totals": {
            "compatibility_result_count": totals["compatibility_result_count"],
            "compatible_count": totals["compatible_count"],
            "incompatible_count": totals["incompatible_count"],
            "unsupported_count": totals["unsupported_count"],
            "prohibited_count": totals["prohibited_count"],
            "unknown_count": totals["unknown_count"],
            "experimental_count": totals["experimental_count"],
            "planning_only_count": totals["planning_only_count"],
            "non_executable_count": totals["non_executable_count"],
            "boundary_context_count": totals["boundary_context_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "state_counts": dict(audit.state_counts),
        "visibility_guarantees": {
            "incompatible_fail_visible": totals["fail_visible_incompatible_count"]
            == totals["incompatible_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
        },
        "boundary_context_guarantees": {
            "boundary_context_count": totals["boundary_context_count"],
            "boundary_context_preserved_count": totals["boundary_context_preserved_count"],
            "all_results_preserve_boundary_context": totals["boundary_context_count"]
            == totals["compatibility_result_count"]
            == totals["boundary_context_preserved_count"],
        },
        "deterministic_guarantees": {
            "compatibility_serialization_stable": serialization["stable"],
            "compatibility_hash_stable": hashing["stable"],
            "compatibility_hash": hash_v3_8_compatibility_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_results_have_replay_evidence": totals["replay_safe_evidence_count"]
            == totals["compatibility_result_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_results_have_rollback_evidence": totals["rollback_safe_evidence_count"]
            == totals["compatibility_result_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_results_preserve_provenance": totals["provenance_continuity_count"]
            == totals["compatibility_result_count"],
        },
        "non_execution_guarantees": {
            "coordination_execution_absent": not audit.coordination_execution_enabled,
            "orchestration_execution_absent": not audit.orchestration_execution_enabled,
            "routing_absent": not audit.routing_enabled,
            "scheduling_absent": not audit.scheduling_enabled,
            "dispatch_absent": not audit.dispatch_enabled,
            "traversal_execution_absent": not audit.traversal_execution_enabled,
            "optimization_absent": not audit.optimization_enabled,
            "recommendation_absent": not audit.recommendation_enabled,
            "execution_authorization_absent": not audit.execution_authorization_enabled,
            "runtime_engine_absent": not audit.runtime_engine_enabled,
            "state_machine_absent": not audit.state_machine_enabled,
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "compatibility_reasoning": export_v3_8_coordination_compatibility_reasoning_audit(audit),
        "compatibility_state_semantics": {
            COMPATIBILITY_STATE_COMPATIBLE: "deterministic evidence supports planning coordination compatibility",
            COMPATIBILITY_STATE_INCOMPATIBLE: "deterministic evidence shows structures cannot safely coordinate",
            COMPATIBILITY_STATE_UNSUPPORTED: "not currently supported and kept fail-visible",
            COMPATIBILITY_STATE_PROHIBITED: "intentionally blocked and kept fail-visible",
            COMPATIBILITY_STATE_UNKNOWN: "not enough deterministic evidence exists and kept fail-visible",
            COMPATIBILITY_STATE_EXPERIMENTAL: "explicitly labeled experimental reasoning only",
            COMPATIBILITY_STATE_PLANNING_ONLY: "reasoning-only, no runtime execution",
            COMPATIBILITY_STATE_NON_EXECUTABLE: "structurally incapable of execution",
        },
        "explicit_limitations": [
            "v3.8 Phase 3 is reasoning-only",
            "v3.8 Phase 3 does not enable coordination execution",
            "v3.8 Phase 3 does not enable orchestration execution",
            "v3.8 Phase 3 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 3 does not enable optimization or recommendations",
            "v3.8 Phase 3 does not enable execution authorization",
            "v3.8 Phase 3 does not enable runtime engines or state machines",
            "v3.8 Phase 3 does not enable callable execution paths",
            "v3.8 Phase 3 does not enable persistent runtime mutation",
            "v3.8 Phase 3 does not enable hidden transitions or silent fallback logic",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "compatibility_result_count": totals["compatibility_result_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "incompatible_fail_visible": totals["fail_visible_incompatible_count"]
            == totals["incompatible_count"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"] == totals["unknown_count"],
            "boundary_context_verified": totals["boundary_context_count"]
            == totals["compatibility_result_count"],
            "replay_verified": totals["replay_safe_evidence_count"] == totals["compatibility_result_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"] == totals["compatibility_result_count"],
            "provenance_verified": totals["provenance_continuity_count"]
            == totals["compatibility_result_count"],
            "hidden_risk_count": totals["hidden_risk_count"],
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
        "# v3.8 Coordination Compatibility Reasoning",
        "",
        "## What Phase 3 Adds",
        "",
        "Phase 3 adds deterministic coordination compatibility reasoning on top of coordination foundations and coordination boundary intelligence.",
        "",
        "It evaluates coordination references, relationship chains, and boundary findings to classify compatibility states without enabling runtime behavior.",
        "",
        "## Compatibility Reasoning vs Execution",
        "",
        "Compatibility reasoning explains whether coordination evidence can be treated as compatible planning evidence. It does not execute, route, schedule, dispatch, traverse, optimize, recommend, authorize, mutate, or create callable flows.",
        "",
        "## Compatibility States",
        "",
        "- `compatible` means deterministic evidence supports planning coordination compatibility.",
        "- `incompatible` means deterministic evidence shows structures cannot safely coordinate.",
        "- `unsupported` means the coordination state is not currently supported.",
        "- `prohibited` means the coordination state is intentionally blocked.",
        "- `unknown` means not enough deterministic evidence exists.",
        "- `experimental` means the reasoning is explicitly labeled experimental.",
        "- `planning_only` means reasoning-only and no execution.",
        "- `non_executable` means structurally incapable of execution.",
        "",
        "## Non-Compatible State Differences",
        "",
        "Incompatible states have deterministic evidence that the structures cannot safely coordinate.",
        "",
        "Unsupported states are not currently supported, but are not necessarily blocked by policy.",
        "",
        "Prohibited states are intentionally blocked.",
        "",
        "Unknown states lack enough deterministic evidence and cannot be inferred as compatible.",
        "",
        "All non-compatible states remain fail-visible.",
        "",
        "## Boundary Context Preservation",
        "",
        f"- Boundary-context count: `{report['boundary_context_guarantees']['boundary_context_count']}`",
        f"- Boundary-context preserved count: `{report['boundary_context_guarantees']['boundary_context_preserved_count']}`",
        f"- All results preserve boundary context: `{report['boundary_context_guarantees']['all_results_preserve_boundary_context']}`",
        "",
        "## Compatibility Totals",
        "",
        f"- Compatibility result count: `{report['compatibility_totals']['compatibility_result_count']}`",
        f"- Compatible count: `{report['compatibility_totals']['compatible_count']}`",
        f"- Incompatible count: `{report['compatibility_totals']['incompatible_count']}`",
        f"- Unsupported count: `{report['compatibility_totals']['unsupported_count']}`",
        f"- Prohibited count: `{report['compatibility_totals']['prohibited_count']}`",
        f"- Unknown count: `{report['compatibility_totals']['unknown_count']}`",
        f"- Experimental count: `{report['compatibility_totals']['experimental_count']}`",
        f"- Planning-only count: `{report['compatibility_totals']['planning_only_count']}`",
        f"- Non-executable count: `{report['compatibility_totals']['non_executable_count']}`",
        f"- Hidden-risk count: `{report['compatibility_totals']['hidden_risk_count']}`",
        f"- Execution-boundary violations: `{report['compatibility_totals']['execution_boundary_violation_count']}`",
        "",
        "## Visibility Guarantees",
        "",
        f"- Incompatible fail-visible: `{report['visibility_guarantees']['incompatible_fail_visible']}`",
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
        f"- Compatibility hash: `{report['deterministic_guarantees']['compatibility_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Why This Remains Non-Executable",
        "",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Runtime engine absent: `{report['non_execution_guarantees']['runtime_engine_absent']}`",
        f"- State machine absent: `{report['non_execution_guarantees']['state_machine_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 3 Does Not Enable",
        "",
        "- Coordination execution.",
        "- Orchestration execution.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Execution authorization.",
        "- Runtime engines.",
        "- State machines.",
        "- Persistent mutation.",
        "- Callable execution paths.",
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
        / "v3_8_coordination_compatibility_reasoning_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_COMPATIBILITY_REASONING.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_compatibility_reasoning_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
