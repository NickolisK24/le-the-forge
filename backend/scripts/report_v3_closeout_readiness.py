"""Generate the v3 closeout and v3.1 readiness report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.report_v3_production_remap_gate_audit import build_v3_production_remap_gate_audit_report  # noqa: E402


def build_v3_closeout_readiness_report() -> dict[str, Any]:
    remap_audit = build_v3_production_remap_gate_audit_report()
    return {
        "schema_version": "v3.closeout_readiness_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "phase": "v3_closeout_and_v3_1_readiness",
        "final_v3_conclusion": "V3_INFRASTRUCTURE_COMPLETE_PRODUCTION_REMAP_NOT_READY",
        "production_remap_allowed": remap_audit["production_remap_allowed"],
        "production_remap_enabled": False,
        "v3_success_definition": "mechanical intelligence infrastructure phase, not production remap phase",
        "v3_achievements": _v3_achievements(),
        "production_safety_guarantees": _production_safety_guarantees(remap_audit),
        "deterministic_guarantees": remap_audit["deterministic_guarantees"],
        "rollback_debug_guarantees": remap_audit["rollback_debug_guarantees"],
        "blocked_mechanic_guarantees": remap_audit["unsupported_mechanic_guarantees"],
        "stable_calculable_findings": remap_audit["stable_calculable_findings"],
        "remap_gate_audit_summary": {
            "final_recommendation": remap_audit["final_recommendation"],
            "audit_gate_count": remap_audit["summary"]["audit_gate_count"],
            "passing_gate_count": remap_audit["summary"]["passing_gate_count"],
            "blocking_gate_count": remap_audit["summary"]["blocking_gate_count"],
            "stable_calculable_domain_count": remap_audit["summary"]["stable_calculable_domain_count"],
            "remap_ready_categories": remap_audit["remap_ready_categories"],
            "remap_blocked_categories": remap_audit["remap_blocked_categories"],
        },
        "remaining_blockers": remap_audit["current_blockers"],
        "why_production_remap_is_blocked": _why_production_remap_is_blocked(remap_audit),
        "v3_1_readiness_plan": _v3_1_readiness_plan(),
        "future_roadmap": _future_roadmap(),
        "closeout_confirmations": {
            "production_planner_math_unchanged": True,
            "production_remap_not_enabled": True,
            "candidate_execution_experimental_only": True,
            "unsupported_mechanics_remain_blocked": True,
            "scripted_mechanics_remain_blocked": True,
            "text_only_mechanics_remain_blocked": True,
            "ambiguous_identities_remain_blocked": True,
            "runtime_planner_behavior_changed": False,
            "production_stat_aggregation_added": False,
            "new_candidate_execution_domains_added": False,
        },
        "metadata": {
            "source": "v3_closeout_readiness",
            "closeout_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "production_remap_performed": False,
            "planner_remap_performed": False,
        },
    }


def _v3_achievements() -> list[dict[str, str]]:
    return [
        {
            "area": "trusted_data_foundation",
            "status": "completed",
            "summary": "v2.5 trusted-data architecture shipped before v3 mechanical work continued.",
        },
        {
            "area": "dry_run_comparison",
            "status": "completed",
            "summary": "deterministic candidate-vs-current comparison envelopes exist behind explicit opt-in gates.",
        },
        {
            "area": "item_affix_comparison",
            "status": "completed",
            "summary": "item base, implicit, and standard affix candidate rows can be compared without production consumption.",
        },
        {
            "area": "passive_skill_comparison",
            "status": "completed",
            "summary": "passive and skill candidate rows can be compared while identity gaps and complex semantics remain blocked.",
        },
        {
            "area": "limited_candidate_execution",
            "status": "completed",
            "summary": "accepted dry-run rows can produce deterministic audit aggregates without live stat aggregation.",
        },
        {
            "area": "production_remap_gate_audit",
            "status": "completed",
            "summary": "audit proves production remap is not ready and documents the blocking gates.",
        },
    ]


def _production_safety_guarantees(remap_audit: dict[str, Any]) -> dict[str, Any]:
    limited_safety = remap_audit["limited_adapter_audit"]["safety_confirmations"]
    return {
        "production_consumed": limited_safety["production_consumed"],
        "production_enabled": limited_safety["production_enabled"],
        "production_planner_output_changed": limited_safety["production_planner_output_changed"],
        "planner_remap_performed": limited_safety["planner_remap_performed"],
        "live_stat_aggregation_changed": limited_safety["live_stat_aggregation_changed"],
        "combat_simulation_changed": limited_safety["combat_simulation_changed"],
        "crafting_behavior_changed": limited_safety["crafting_behavior_changed"],
        "optimizer_behavior_changed": limited_safety["optimizer_behavior_changed"],
        "candidate_execution_default_enabled": limited_safety["candidate_execution_default_enabled"],
    }


def _why_production_remap_is_blocked(remap_audit: dict[str, Any]) -> list[str]:
    return [
        "no domain is stable-calculable for production remap",
        "limited adapter output is audit aggregation, not live stat aggregation",
        "golden baseline evidence is not sufficient for production promotion",
        "value normalization still has audit-only blocked rows",
        "unknown, conditional, and triggered operation semantics remain blocked",
        "stat and skill identity gaps remain blocked",
        "unsupported, text-only, and scripted mechanics remain excluded",
        "candidate provenance is not complete",
        "production promotion policy decisions are still required",
    ]


def _v3_1_readiness_plan() -> dict[str, Any]:
    return {
        "phase_name": "v3.1 Mechanical Parity Hardening",
        "objective": "harden comparison-backed parity evidence before any future production remap gate can be reconsidered",
        "workstreams": [
            "golden baseline expansion",
            "parity snapshot infrastructure",
            "delta explanation hardening",
            "rollback validation",
            "comparison stability auditing",
            "approved normalization promotion strategy",
            "approved operation promotion strategy",
            "limited stable-calculable domain progression",
            "explainability hardening",
            "policy-driven production promotion requirements",
        ],
        "entry_criteria": [
            "v3 closeout report accepted",
            "production remap remains disabled",
            "limited candidate execution remains opt-in and audit-only",
            "blocked mechanics remain visibly blocked",
        ],
        "exit_criteria": [
            "expanded golden baselines exist for supported rows",
            "parity snapshots are deterministic and reviewable",
            "approved normalization and operation policies are documented",
            "rollback validation has repeatable evidence",
            "production remap gate audit can be rerun with reduced blockers",
        ],
    }


def _future_roadmap() -> list[dict[str, Any]]:
    return [
        {
            "phase": "v3.1",
            "name": "Mechanical Parity Hardening",
            "goal": "turn audit fixtures and comparison scaffolding into stronger parity evidence while keeping production remap disabled",
            "non_goals": ["production remap", "live DPS replacement", "unsupported mechanic promotion"],
        },
        {
            "phase": "v3.5",
            "name": "Controlled Mechanical Candidate Expansion",
            "goal": "expand source-backed candidate coverage only where normalization, operation semantics, identity, provenance, and baselines are approved",
            "non_goals": ["default production consumption", "tooltip-derived formulas", "scripted behavior promotion"],
        },
        {
            "phase": "v4",
            "name": "Production Mechanical Promotion Candidate",
            "goal": "consider production promotion only after remap gate audits prove deterministic parity, rollback readiness, policy approval, and stable-calculable domains",
            "non_goals": ["promotion without gate approval", "silent behavior changes", "unsupported mechanic execution"],
        },
    ]


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    confirmations = report["closeout_confirmations"]
    remap = report["remap_gate_audit_summary"]
    lines = [
        "# V3 Closeout And V3.1 Readiness",
        "",
        "V3 closes as a successful mechanical intelligence infrastructure phase. It is not a production remap phase.",
        "",
        "## Closeout Result",
        "",
        f"- Final v3 conclusion: `{report['final_v3_conclusion']}`",
        f"- Production remap allowed: `{str(report['production_remap_allowed']).lower()}`",
        f"- Production remap enabled: `{str(report['production_remap_enabled']).lower()}`",
        f"- v3.1 phase: `{report['v3_1_readiness_plan']['phase_name']}`",
        "",
        "## V3 Achievements",
        "",
    ]
    lines.extend(f"- `{item['area']}`: {item['summary']}" for item in report["v3_achievements"])
    lines.extend(
        [
            "",
            "## Production Safety",
            "",
            f"- Production planner math unchanged: `{str(confirmations['production_planner_math_unchanged']).lower()}`",
            f"- Runtime planner behavior changed: `{str(confirmations['runtime_planner_behavior_changed']).lower()}`",
            f"- Candidate execution experimental only: `{str(confirmations['candidate_execution_experimental_only']).lower()}`",
            f"- Production stat aggregation added: `{str(confirmations['production_stat_aggregation_added']).lower()}`",
            "",
            "## Remap Gate Audit Summary",
            "",
            f"- Final recommendation: `{remap['final_recommendation']}`",
            f"- Audit gates: `{remap['audit_gate_count']}`",
            f"- Passing gates: `{remap['passing_gate_count']}`",
            f"- Blocking gates: `{remap['blocking_gate_count']}`",
            f"- Stable-calculable production domains: `{remap['stable_calculable_domain_count']}`",
            "",
            "## Stable-Calculable Findings",
            "",
            "| Domain | Dry-Run Audit Rows | Blocked Rows | Rejected Rows | Production Remap Stable |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for finding in report["stable_calculable_findings"]:
        lines.append(
            f"| `{finding['domain']}` | `{finding['executed_row_count']}` | `{finding['blocked_row_count']}` | `{finding['rejected_row_count']}` | `{str(finding['stable_calculable_for_production_remap']).lower()}` |"
        )
    lines.extend(["", "## Why Production Remap Remains Blocked", ""])
    lines.extend(f"- {item}" for item in report["why_production_remap_is_blocked"])
    lines.extend(["", "## V3.1 Readiness Plan", ""])
    lines.append(f"Objective: {report['v3_1_readiness_plan']['objective']}")
    lines.extend(["", "Workstreams:"])
    lines.extend(f"- {item}" for item in report["v3_1_readiness_plan"]["workstreams"])
    lines.extend(["", "## Future Roadmap", ""])
    for phase in report["future_roadmap"]:
        lines.append(f"- `{phase['phase']}` {phase['name']}: {phase['goal']}")
    lines.extend(
        [
            "",
            "## Closeout Confirmations",
            "",
            f"- Unsupported mechanics remain blocked: `{str(confirmations['unsupported_mechanics_remain_blocked']).lower()}`",
            f"- Scripted mechanics remain blocked: `{str(confirmations['scripted_mechanics_remain_blocked']).lower()}`",
            f"- Text-only mechanics remain blocked: `{str(confirmations['text_only_mechanics_remain_blocked']).lower()}`",
            f"- Ambiguous identities remain blocked: `{str(confirmations['ambiguous_identities_remain_blocked']).lower()}`",
            f"- Production remap not enabled: `{str(confirmations['production_remap_not_enabled']).lower()}`",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_closeout_readiness_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_CLOSEOUT_AND_V3_1_READINESS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_closeout_readiness_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps({
        "final_v3_conclusion": report["final_v3_conclusion"],
        "production_remap_allowed": report["production_remap_allowed"],
        "production_remap_enabled": report["production_remap_enabled"],
        "v3_1_phase": report["v3_1_readiness_plan"]["phase_name"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
