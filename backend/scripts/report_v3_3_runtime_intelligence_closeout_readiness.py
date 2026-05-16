"""Generate the v3.3 runtime intelligence closeout readiness report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.runtime_intelligence.closeout_readiness_audit import (  # noqa: E402
    build_runtime_intelligence_closeout_readiness_audit,
    evaluate_runtime_intelligence_closeout_readiness_audit,
    summarize_runtime_intelligence_closeout_readiness_audit,
)


DETERMINISTIC_GENERATED_AT = "2026-05-15T00:00:00+00:00"


def build_v3_3_runtime_intelligence_closeout_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[2]
    audit = build_runtime_intelligence_closeout_readiness_audit(repo_root=root)
    evaluation = evaluate_runtime_intelligence_closeout_readiness_audit(audit)
    summary = summarize_runtime_intelligence_closeout_readiness_audit(audit)
    return {
        "schema_version": "v3_3.runtime_intelligence_closeout_readiness_report.1",
        "generated_at": DETERMINISTIC_GENERATED_AT,
        "phase": "v3.3_phase_12_runtime_intelligence_closeout_readiness_audit",
        "recommendation": "V3_3_READY_FOR_FUTURE_CONTROLLED_EXECUTION_PLANNING_ONLY",
        "v3_3_closeout_audit_only": True,
        "runtime_intelligence_planning_only": True,
        "runtime_manifest_consumption_enabled": False,
        "production_runtime_routing_authorized": False,
        "production_runtime_prohibited": True,
        "production_authoritative_manifest_treatment": False,
        "live_runtime_execution_enabled": False,
        "live_session_execution_enabled": False,
        "live_drift_detection_enabled": False,
        "live_replay_execution_enabled": False,
        "live_synthesis_execution_enabled": False,
        "live_decision_routing_enabled": False,
        "active_runtime_reasoning_decisions_enabled": False,
        "recommendation_logic_enabled": False,
        "closeout_audit": audit,
        "evaluation": evaluation,
        "summary": {
            **audit["summary"],
            "audited_phase_count": audit["audited_phase_count"],
            "expected_phase_count": audit["expected_phase_count"],
            "compatibility_chain_validation_result": audit["compatibility_chain_validation"]["passed"],
            "governance_coverage_validation_result": audit["governance_coverage_validation"]["passed"],
            "readiness_blocker_count": len(audit["readiness_blockers"]),
            "readiness_risk_count": len(audit["readiness_risks"]),
            "readiness_limitation_count": len(audit["readiness_limitations"]),
            "deterministic_hash": audit["deterministic_hash"],
        },
        "closeout_summary": summary,
        "readiness_status": audit["readiness_status"],
        "readiness_blockers": audit["readiness_blockers"],
        "readiness_risks": audit["readiness_risks"],
        "readiness_limitations": audit["readiness_limitations"],
        "future_controlled_execution_planning_recommendations": audit["future_controlled_execution_planning_recommendations"],
        "compatibility_chain_validation": audit["compatibility_chain_validation"],
        "governance_coverage_validation": audit["governance_coverage_validation"],
        "safety_confirmations": audit["safety_confirmations"],
    }


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    coverage = report["governance_coverage_validation"]
    compatibility = report["compatibility_chain_validation"]
    lines = [
        "# v3.3 Runtime Intelligence Closeout Readiness",
        "",
        "## Final Readiness Status",
        "",
        f"- Readiness status: `{report['readiness_status']}`",
        f"- Audited phases: {summary['audited_phase_count']} of {summary['expected_phase_count']}",
        f"- Compatibility chain valid: {compatibility['passed']}",
        f"- Governance coverage valid: {coverage['passed']}",
        f"- Deterministic audit hash: `{summary['deterministic_hash']}`",
        "",
        "This passing readiness status is planning-only. It does not authorize controlled execution, production runtime routing, default runtime manifest consumption, or production-authoritative runtime intelligence.",
        "",
        "## v3.3 Phase Chain Summary",
        "",
        "v3.3 established deterministic planning-only contracts for runtime intelligence classification, evidence, provenance, reasoning chains, explanations, confidence, evidence synthesis, decision boundaries, replay orchestration, drift audit, and session governance. Phase 12 audits that chain without adding a new runtime contract family.",
        "",
        "## What v3.3 Accomplished",
        "",
        "- Deterministic contract ordering, stable hashing, replay validation, duplicate detection, and cross-contract reference validation across Phases 1 through 11.",
        "- Explicit governance visibility for unsupported states, provenance, source and hash requirements, drift, conflicts, blockers, limitations, confidence boundaries, decision boundaries, replay, and session isolation.",
        "- A closeout readiness classification for future controlled-execution planning.",
        "",
        "## What v3.3 Did Not Enable",
        "",
        "- Production runtime routing remains prohibited.",
        "- Default runtime manifest consumption remains disabled.",
        "- Production-authoritative manifest treatment remains prohibited.",
        "- Live runtime execution, live session execution, live drift detection, live replay execution, live synthesis execution, live decision routing, active runtime reasoning decisions, and recommendation logic remain disabled.",
        "",
        "## Remaining Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["readiness_limitations"])
    lines.extend(
        [
            "",
            "## Remaining Risks",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["readiness_risks"])
    lines.extend(
        [
            "",
            "## Future Controlled Execution Planning Notes",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["future_controlled_execution_planning_recommendations"])
    lines.extend(
        [
            "",
            "## Blocker Summary",
            "",
        ]
    )
    if report["readiness_blockers"]:
        lines.extend(f"- `{item['blocker_id']}`: {item['count']}" for item in report["readiness_blockers"])
    else:
        lines.append("- No closeout blockers were detected.")
    lines.extend(
        [
            "",
            "## Explicit Production Prohibition",
            "",
            "Production runtime remains prohibited. Default runtime manifest consumption remains disabled. Production-authoritative manifest treatment remains prohibited. Future controlled-execution planning must remain non-production until a later explicit governance phase defines otherwise.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("docs/generated/v3_3_runtime_intelligence_closeout_readiness_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("docs/migration/V3_3_RUNTIME_INTELLIGENCE_CLOSEOUT_READINESS.md"),
    )
    args = parser.parse_args()
    report = build_v3_3_runtime_intelligence_closeout_readiness_report(args.repo_root)
    json_output = args.repo_root / args.json_output
    markdown_output = args.repo_root / args.markdown_output
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown_report(report, markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
