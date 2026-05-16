"""Generate the v3.8 coordination boundary intelligence audit report."""

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

from runtime_coordination.coordination_boundary_intelligence import (  # noqa: E402
    audit_v3_8_coordination_boundary_intelligence,
    export_v3_8_coordination_boundary_intelligence_audit,
)
from runtime_coordination.coordination_boundary_models import (  # noqa: E402
    BOUNDARY_CLASSIFICATION_EXPERIMENTAL,
    BOUNDARY_CLASSIFICATION_NON_EXECUTABLE,
    BOUNDARY_CLASSIFICATION_PLANNING_ONLY,
    BOUNDARY_CLASSIFICATION_PROHIBITED,
    BOUNDARY_CLASSIFICATION_SUPPORTED,
    BOUNDARY_CLASSIFICATION_UNKNOWN,
    BOUNDARY_CLASSIFICATION_UNSUPPORTED,
    hash_v3_8_boundary_audit,
    validate_v3_8_boundary_hash_stability,
    validate_v3_8_boundary_serialization_stability,
)
from runtime_coordination.coordination_foundation_models import deterministic_hash  # noqa: E402


DETERMINISTIC_GENERATED_AT = "2026-05-16T00:00:00+00:00"


def build_v3_8_coordination_boundary_intelligence_report(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = audit_v3_8_coordination_boundary_intelligence()
    serialization = validate_v3_8_boundary_serialization_stability(audit)
    hashing = validate_v3_8_boundary_hash_stability(audit)
    totals = dict(audit.validation_totals)
    report = {
        "schema_version": "v3_8.coordination_boundary_intelligence_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase_name": "v3.8_coordination_boundary_intelligence",
        "repo_root": str(root),
        "architectural_purpose": (
            "deterministic classification and audit of orchestration-planning coordination boundaries"
        ),
        "audit_status": audit.audit_status,
        "source_foundation_id": audit.source_foundation_id,
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
        "callable_coordination_flow_enabled": audit.callable_coordination_flow_enabled,
        "persistent_runtime_mutation_enabled": audit.persistent_runtime_mutation_enabled,
        "hidden_transition_enabled": audit.hidden_transition_enabled,
        "silent_fallback_enabled": audit.silent_fallback_enabled,
        "boundary_totals": {
            "boundary_count": totals["boundary_count"],
            "finding_count": totals["finding_count"],
            "supported_boundary_count": totals["supported_boundary_count"],
            "unsupported_boundary_count": totals["unsupported_boundary_count"],
            "prohibited_boundary_count": totals["prohibited_boundary_count"],
            "unknown_boundary_count": totals["unknown_boundary_count"],
            "experimental_boundary_count": totals["experimental_boundary_count"],
            "planning_only_boundary_count": totals["planning_only_boundary_count"],
            "non_executable_boundary_count": totals["non_executable_boundary_count"],
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "classification_counts": dict(audit.classification_counts),
        "visibility_guarantees": {
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_boundary_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_boundary_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"]
            == totals["unknown_boundary_count"],
            "supported_hidden_risk_count": totals["supported_hidden_risk_count"],
            "hidden_finding_count": totals["hidden_finding_count"],
        },
        "deterministic_guarantees": {
            "boundary_serialization_stable": serialization["stable"],
            "boundary_hash_stable": hashing["stable"],
            "boundary_hash": hash_v3_8_boundary_audit(audit),
            "serialization_first_length": serialization["first_length"],
            "serialization_second_length": serialization["second_length"],
            "hash_algorithm": hashing["hash_algorithm"],
        },
        "replay_guarantees": {
            "replay_safe_evidence_count": totals["replay_safe_evidence_count"],
            "all_findings_have_replay_evidence": totals["replay_safe_evidence_count"] == totals["finding_count"],
        },
        "rollback_guarantees": {
            "rollback_safe_evidence_count": totals["rollback_safe_evidence_count"],
            "all_findings_have_rollback_evidence": totals["rollback_safe_evidence_count"] == totals["finding_count"],
        },
        "provenance_guarantees": {
            "provenance_continuity_count": totals["provenance_continuity_count"],
            "all_findings_preserve_provenance": totals["provenance_continuity_count"] == totals["finding_count"],
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
            "callable_coordination_flow_absent": not audit.callable_coordination_flow_enabled,
            "persistent_runtime_mutation_absent": not audit.persistent_runtime_mutation_enabled,
            "hidden_transition_absent": not audit.hidden_transition_enabled,
            "silent_fallback_absent": not audit.silent_fallback_enabled,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
        },
        "boundary_audit": export_v3_8_coordination_boundary_intelligence_audit(audit),
        "classification_semantics": {
            BOUNDARY_CLASSIFICATION_SUPPORTED: "deterministically supported as planning coordination boundary evidence",
            BOUNDARY_CLASSIFICATION_UNSUPPORTED: "not currently supported and kept fail-visible",
            BOUNDARY_CLASSIFICATION_PROHIBITED: "intentionally blocked and kept fail-visible",
            BOUNDARY_CLASSIFICATION_UNKNOWN: "not enough deterministic evidence exists and kept fail-visible",
            BOUNDARY_CLASSIFICATION_EXPERIMENTAL: "audit-only evidence with no runtime capability",
            BOUNDARY_CLASSIFICATION_PLANNING_ONLY: "coordination evidence only, not runtime path selection",
            BOUNDARY_CLASSIFICATION_NON_EXECUTABLE: "explicit confirmation that execution behavior is absent",
        },
        "explicit_limitations": [
            "v3.8 Phase 2 is non-executable",
            "v3.8 Phase 2 does not enable orchestration execution",
            "v3.8 Phase 2 does not enable runtime coordination engines",
            "v3.8 Phase 2 does not enable routing, scheduling, dispatch, or traversal execution",
            "v3.8 Phase 2 does not enable optimization or recommendation systems",
            "v3.8 Phase 2 does not enable execution authorization",
            "v3.8 Phase 2 does not enable callable coordination flows",
            "v3.8 Phase 2 does not enable persistent runtime mutation",
            "v3.8 Phase 2 does not enable hidden transitions or silent fallback behavior",
        ],
        "summary": {
            "audit_status": audit.audit_status,
            "boundary_count": totals["boundary_count"],
            "finding_count": totals["finding_count"],
            "deterministic_serialization_verified": serialization["stable"],
            "deterministic_hashing_verified": hashing["stable"],
            "unsupported_fail_visible": totals["fail_visible_unsupported_count"]
            == totals["unsupported_boundary_count"],
            "prohibited_fail_visible": totals["fail_visible_prohibited_count"]
            == totals["prohibited_boundary_count"],
            "unknown_fail_visible": totals["fail_visible_unknown_count"]
            == totals["unknown_boundary_count"],
            "replay_verified": totals["replay_safe_evidence_count"] == totals["finding_count"],
            "rollback_verified": totals["rollback_safe_evidence_count"] == totals["finding_count"],
            "provenance_verified": totals["provenance_continuity_count"] == totals["finding_count"],
            "non_executable_verified": audit.non_executable,
            "execution_boundary_violation_count": totals["execution_boundary_violation_count"],
            "orchestration_boundaries_enforced": totals["execution_boundary_violation_count"] == 0,
        },
    }
    report["deterministic_report_hash"] = deterministic_hash(
        {key: value for key, value in report.items() if key != "deterministic_report_hash"}
    )
    return report


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# v3.8 Coordination Boundary Intelligence",
        "",
        "## What Phase 2 Adds",
        "",
        "Phase 2 adds deterministic coordination boundary intelligence on top of the v3.8 coordination foundation layer.",
        "",
        "It identifies, classifies, explains, and audits coordination boundary states across Phase 1 foundation objects.",
        "",
        "This phase is NON-executable.",
        "",
        "## Why Boundary Intelligence Matters",
        "",
        "Coordination foundations become trustworthy only when every boundary is visible, classified, explainable, and tied to provenance, replay, and rollback evidence.",
        "",
        "Boundary intelligence prevents unsupported, prohibited, or unknown coordination states from being silently treated as supported behavior.",
        "",
        "## Boundary Classifications",
        "",
        "- `supported` means deterministic planning coordination evidence exists for the boundary.",
        "- `unsupported` means the coordination state is not currently supported and must remain fail-visible.",
        "- `prohibited` means the coordination state is intentionally blocked and must remain fail-visible.",
        "- `unknown` means not enough deterministic evidence exists and the state must remain fail-visible.",
        "- `experimental` means audit-only evidence with no runtime capability.",
        "- `planning_only` means evidence describes planning coordination only and does not select runtime paths.",
        "- `non_executable` means execution behavior is explicitly absent.",
        "",
        "## Fail-Visible Coordination Boundaries",
        "",
        f"- Unsupported fail-visible: `{report['visibility_guarantees']['unsupported_fail_visible']}`",
        f"- Prohibited fail-visible: `{report['visibility_guarantees']['prohibited_fail_visible']}`",
        f"- Unknown fail-visible: `{report['visibility_guarantees']['unknown_fail_visible']}`",
        f"- Supported hidden risk count: `{report['visibility_guarantees']['supported_hidden_risk_count']}`",
        f"- Hidden finding count: `{report['visibility_guarantees']['hidden_finding_count']}`",
        "",
        "## Report Totals",
        "",
        f"- Boundary count: `{report['boundary_totals']['boundary_count']}`",
        f"- Finding count: `{report['boundary_totals']['finding_count']}`",
        f"- Supported boundaries: `{report['boundary_totals']['supported_boundary_count']}`",
        f"- Unsupported boundaries: `{report['boundary_totals']['unsupported_boundary_count']}`",
        f"- Prohibited boundaries: `{report['boundary_totals']['prohibited_boundary_count']}`",
        f"- Unknown boundaries: `{report['boundary_totals']['unknown_boundary_count']}`",
        f"- Experimental boundaries: `{report['boundary_totals']['experimental_boundary_count']}`",
        f"- Planning-only boundaries: `{report['boundary_totals']['planning_only_boundary_count']}`",
        f"- Non-executable boundaries: `{report['boundary_totals']['non_executable_boundary_count']}`",
        f"- Execution-boundary violations: `{report['boundary_totals']['execution_boundary_violation_count']}`",
        "",
        "## Replay And Rollback Preservation",
        "",
        f"- Replay-safe evidence count: `{report['replay_guarantees']['replay_safe_evidence_count']}`",
        f"- All findings have replay evidence: `{report['replay_guarantees']['all_findings_have_replay_evidence']}`",
        f"- Rollback-safe evidence count: `{report['rollback_guarantees']['rollback_safe_evidence_count']}`",
        f"- All findings have rollback evidence: `{report['rollback_guarantees']['all_findings_have_rollback_evidence']}`",
        "",
        "## Provenance Preservation",
        "",
        f"- Provenance continuity count: `{report['provenance_guarantees']['provenance_continuity_count']}`",
        f"- All findings preserve provenance: `{report['provenance_guarantees']['all_findings_preserve_provenance']}`",
        "",
        "## Deterministic Evidence",
        "",
        f"- Audit status: `{report['summary']['audit_status']}`",
        f"- Serialization stable: `{report['summary']['deterministic_serialization_verified']}`",
        f"- Hash stable: `{report['summary']['deterministic_hashing_verified']}`",
        f"- Boundary hash: `{report['deterministic_guarantees']['boundary_hash']}`",
        f"- Report hash: `{report['deterministic_report_hash']}`",
        "",
        "## Non-Execution Boundaries",
        "",
        f"- Coordination execution absent: `{report['non_execution_guarantees']['coordination_execution_absent']}`",
        f"- Orchestration execution absent: `{report['non_execution_guarantees']['orchestration_execution_absent']}`",
        f"- Routing absent: `{report['non_execution_guarantees']['routing_absent']}`",
        f"- Scheduling absent: `{report['non_execution_guarantees']['scheduling_absent']}`",
        f"- Dispatch absent: `{report['non_execution_guarantees']['dispatch_absent']}`",
        f"- Traversal execution absent: `{report['non_execution_guarantees']['traversal_execution_absent']}`",
        f"- Optimization absent: `{report['non_execution_guarantees']['optimization_absent']}`",
        f"- Recommendation absent: `{report['non_execution_guarantees']['recommendation_absent']}`",
        f"- Execution authorization absent: `{report['non_execution_guarantees']['execution_authorization_absent']}`",
        f"- Callable coordination flow absent: `{report['non_execution_guarantees']['callable_coordination_flow_absent']}`",
        f"- Persistent runtime mutation absent: `{report['non_execution_guarantees']['persistent_runtime_mutation_absent']}`",
        f"- Hidden transition absent: `{report['non_execution_guarantees']['hidden_transition_absent']}`",
        f"- Silent fallback absent: `{report['non_execution_guarantees']['silent_fallback_absent']}`",
        "",
        "## Phase 2 Does Not Enable",
        "",
        "- Orchestration execution.",
        "- Runtime coordination engines.",
        "- Routing.",
        "- Scheduling.",
        "- Dispatch.",
        "- Traversal execution.",
        "- Optimization.",
        "- Recommendations.",
        "- Execution authorization.",
        "- Callable coordination flows.",
        "- Persistent runtime mutation.",
        "- Hidden transitions.",
        "- Silent fallback behavior.",
        "- Production behavior.",
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
        / "v3_8_coordination_boundary_intelligence_report.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "docs"
        / "migration"
        / "V3_8_COORDINATION_BOUNDARY_INTELLIGENCE.md",
    )
    args = parser.parse_args(argv)
    report = build_v3_8_coordination_boundary_intelligence_report(args.repo_root)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

