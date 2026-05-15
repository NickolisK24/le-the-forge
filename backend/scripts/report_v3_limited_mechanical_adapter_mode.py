"""Generate the v3 limited mechanical adapter mode report."""

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

from app.planner_adapters.v3.limited_mechanical_adapter import (  # noqa: E402
    EXECUTED_CATEGORIES,
    NON_EXECUTED_CATEGORIES,
    V3LimitedMechanicalAdapter,
    build_sample_limited_adapter_inputs,
)


def build_v3_limited_mechanical_adapter_mode_report() -> dict[str, Any]:
    comparison_reports = build_sample_limited_adapter_inputs()
    adapter = V3LimitedMechanicalAdapter()
    disabled = adapter.execute(
        comparison_reports=comparison_reports,
        enabled=False,
        allowed_domains={"item_affix", "passive_skill"},
    )
    enabled = adapter.execute(
        comparison_reports=comparison_reports,
        enabled=True,
        allowed_domains={"item_affix", "passive_skill"},
    )
    item_only = adapter.execute(
        comparison_reports=comparison_reports,
        enabled=True,
        allowed_domains={"item_affix"},
        run_id="v3_phase_10_limited_mechanical_adapter_item_only_gate_sample",
    )
    return {
        "schema_version": "v3.limited_mechanical_adapter_mode_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "mode_disabled_behavior": disabled["mode"],
        "mode_enabled_behavior": enabled["mode"],
        "summary": enabled["summary"],
        "execution_gate_summary": enabled["execution_gate_summary"],
        "domain_summary": enabled["domain_summary"],
        "execution_category_counts": enabled["execution_category_counts"],
        "blocked_reasons": enabled["blocked_reasons"],
        "candidate_aggregates": enabled["candidate_aggregates"],
        "sample_execution": enabled,
        "item_only_gate_sample": item_only,
        "disabled_response": disabled,
        "safety_confirmations": enabled["safety_confirmations"],
        "supported_execution_categories": sorted(EXECUTED_CATEGORIES),
        "blocked_execution_categories": sorted(NON_EXECUTED_CATEGORIES),
        "deterministic_guarantees": [
            "comparison rows are sorted by domain and output key before execution",
            "candidate aggregates are sorted by domain and aggregate key",
            "stable JSON serialization with sorted keys is used for deterministic hashes",
            "generated timestamps are excluded from deterministic hashes",
        ],
        "rollback_debug_guarantees": [
            "no production planner output is consumed or mutated",
            "execution rows retain comparison category, candidate value, provenance, metadata, and blocked reasons",
            "candidate aggregates retain source output keys and provenance",
            "domain gates can block an entire domain without deleting comparison evidence",
        ],
        "current_limitations": [
            "execution consumes only supplied comparison reports, not production planner runtime output",
            "only rows accepted by dry-run comparison are executable",
            "aggregates are deterministic candidate sums for audit, not live stat aggregation",
            "unsupported, text-only, scripted, unknown-operation, unresolved-identity, conditional, and triggered rows remain blocked",
            "combat, DPS, crafting, optimizer, simulation, and production stat remap behavior is not implemented",
        ],
        "remaining_blockers_before_production_remap_gate_audit": [
            "source-backed candidate adapter inventory for each supported domain",
            "golden baseline approval for limited candidate aggregates",
            "formal production remap gate review",
            "explicit rollback and kill-switch plan for any future production opt-in",
            "approved semantics for conditional, triggered, cooldown, duration, chance, and proc behavior",
            "approved identity bridge policy for passive and skill rows",
        ],
        "metadata": {
            "source": "v3_limited_mechanical_adapter",
            "experimental": True,
            "default_enabled": False,
            "production_consumer": False,
            "production_behavior_changed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    safety = report["safety_confirmations"]
    lines = [
        "# V3 Limited Mechanical Adapter Mode",
        "",
        "Phase 10 introduces the first limited candidate execution path behind explicit dry-run and domain gates.",
        "It is not production mechanical remap work and it does not change production planner behavior.",
        "",
        "## Gate",
        "",
        f"- Default enabled: `{str(report['mode_disabled_behavior']['default_enabled']).lower()}`",
        f"- Disabled response active: `{str(report['mode_disabled_behavior']['active']).lower()}`",
        f"- Enabled only by explicit request: `{str(report['mode_enabled_behavior']['active']).lower()}`",
        f"- Production consumer: `{str(report['mode_enabled_behavior']['production_consumer']).lower()}`",
        f"- Allowed domains: `{', '.join(report['mode_enabled_behavior']['allowed_domains'])}`",
        "",
        "## Summary",
        "",
        f"- Executed rows: `{summary['executed_row_count']}`",
        f"- Rejected rows: `{summary['rejected_row_count']}`",
        f"- Blocked rows: `{summary['blocked_row_count']}`",
        f"- Candidate aggregates: `{summary['aggregate_count']}`",
        f"- Deterministic hash: `{report['sample_execution']['deterministic_hash']}`",
        "",
        "## Execution Categories",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]
    for category, count in report["execution_category_counts"].items():
        lines.append(f"| `{category}` | `{count}` |")
    lines.extend(["", "## Blocked Reasons", "", "| Reason | Count |", "| --- | ---: |"])
    for row in report["blocked_reasons"]:
        lines.append(f"| `{row['reason']}` | `{row['count']}` |")
    lines.extend(["", "## Execution Gates", ""])
    for gate, value in report["execution_gate_summary"].items():
        lines.append(f"- {gate}: `{value}`")
    lines.extend(
        [
            "",
            "## Safety Confirmations",
            "",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production enabled: `{str(safety['production_enabled']).lower()}`",
            f"- Production planner output changed: `{str(safety['production_planner_output_changed']).lower()}`",
            f"- Planner remap performed: `{str(safety['planner_remap_performed']).lower()}`",
            f"- Live stat aggregation changed: `{str(safety['live_stat_aggregation_changed']).lower()}`",
            f"- Candidate execution default enabled: `{str(safety['candidate_execution_default_enabled']).lower()}`",
            "",
            "## Current Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["current_limitations"])
    lines.extend(["", "## Remaining Blockers Before Production Remap Gate Audit", ""])
    lines.extend(f"- {item}" for item in report["remaining_blockers_before_production_remap_gate_audit"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_limited_mechanical_adapter_mode_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_LIMITED_MECHANICAL_ADAPTER_MODE.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_limited_mechanical_adapter_mode_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
