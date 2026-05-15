"""Generate the v3 production planner remap gate audit report."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.planner_adapters.v3.limited_mechanical_adapter import V3LimitedMechanicalAdapter, build_sample_limited_adapter_inputs  # noqa: E402
from scripts.report_v3_limited_mechanical_adapter_mode import build_v3_limited_mechanical_adapter_mode_report  # noqa: E402


AUDIT_CATEGORIES = [
    "remap_ready",
    "remap_blocked",
    "partially_ready",
    "requires_policy_decision",
    "blocked_by_missing_baseline",
    "blocked_by_identity_gap",
    "blocked_by_unknown_operation",
    "blocked_by_unsupported_mechanics",
    "blocked_by_value_normalization",
    "blocked_by_missing_provenance",
    "blocked_by_non_determinism",
    "blocked_by_missing_rollback_visibility",
]


def build_v3_production_remap_gate_audit_report() -> dict[str, Any]:
    limited_report = build_v3_limited_mechanical_adapter_mode_report()
    repeated_execution = V3LimitedMechanicalAdapter().execute(
        comparison_reports=build_sample_limited_adapter_inputs(),
        enabled=True,
        allowed_domains={"item_affix", "passive_skill"},
    )
    gates = _audit_gates(limited_report=limited_report, repeated_execution=repeated_execution)
    domain_findings = _domain_stable_calculable_findings(limited_report["sample_execution"]["execution_rows"])
    category_counts = Counter(gate["audit_category"] for gate in gates)
    production_remap_allowed = all(gate["production_remap_gate_passed"] for gate in gates)

    return {
        "schema_version": "v3.production_remap_gate_audit_report.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "final_recommendation": "PRODUCTION_REMAP_READY" if production_remap_allowed else "PRODUCTION_REMAP_NOT_READY",
        "production_remap_allowed": production_remap_allowed,
        "production_remap_enabled": False,
        "summary": {
            "audit_gate_count": len(gates),
            "passing_gate_count": sum(1 for gate in gates if gate["production_remap_gate_passed"]),
            "blocking_gate_count": sum(1 for gate in gates if not gate["production_remap_gate_passed"]),
            "candidate_execution_row_count": limited_report["summary"]["executed_row_count"],
            "candidate_blocked_row_count": limited_report["summary"]["blocked_row_count"],
            "candidate_rejected_row_count": limited_report["summary"]["rejected_row_count"],
            "stable_calculable_domain_count": sum(1 for row in domain_findings if row["stable_calculable_for_production_remap"]),
            "deterministic": _deterministic_passed(limited_report, repeated_execution),
            "production_planner_output_changed": False,
        },
        "audit_category_counts": dict(sorted(category_counts.items())),
        "audit_gates": gates,
        "remap_ready_categories": sorted(
            {gate["gate_id"] for gate in gates if gate["audit_category"] == "remap_ready" and gate["production_remap_gate_passed"]}
        ),
        "remap_blocked_categories": sorted(
            {gate["audit_category"] for gate in gates if not gate["production_remap_gate_passed"]}
        ),
        "stable_calculable_findings": domain_findings,
        "deterministic_guarantees": _deterministic_guarantees(limited_report, repeated_execution),
        "rollback_debug_guarantees": _rollback_debug_guarantees(limited_report),
        "unsupported_mechanic_guarantees": _unsupported_mechanic_guarantees(limited_report),
        "current_blockers": _current_blockers(gates),
        "limited_adapter_audit": limited_report,
        "metadata": {
            "source": "v3_production_remap_gate_audit",
            "audit_only": True,
            "production_consumer": False,
            "production_behavior_changed": False,
            "production_remap_performed": False,
            "planner_remap_performed": False,
        },
    }


def _audit_gates(*, limited_report: dict[str, Any], repeated_execution: dict[str, Any]) -> list[dict[str, Any]]:
    counts = limited_report["execution_category_counts"]
    summary = limited_report["summary"]
    safety = limited_report["safety_confirmations"]
    sample_execution = limited_report["sample_execution"]

    return [
        _gate(
            "production_isolation",
            "remap_ready",
            safety["production_consumed"] is False
            and safety["production_enabled"] is False
            and safety["production_planner_output_changed"] is False
            and safety["planner_remap_performed"] is False
            and safety["live_stat_aggregation_changed"] is False,
            "candidate execution is non-production-consuming and planner output is unchanged",
        ),
        _gate(
            "deterministic_integrity",
            "blocked_by_non_determinism",
            _deterministic_passed(limited_report, repeated_execution),
            "deterministic hashes must match across repeated audit builds",
        ),
        _gate(
            "rollback_debug_visibility",
            "blocked_by_missing_rollback_visibility",
            _rollback_visibility_passed(sample_execution),
            "execution rows, aggregates, category counts, blocked reasons, and safety confirmations must be visible",
        ),
        _gate(
            "value_normalization_readiness",
            "blocked_by_value_normalization",
            counts.get("blocked_value_normalization", 0) == 0,
            "audit-only or unknown value normalization rows still block remap",
        ),
        _gate(
            "operation_semantics_readiness",
            "blocked_by_unknown_operation",
            counts.get("blocked_unknown_operation", 0) == 0
            and counts.get("blocked_conditional_semantics", 0) == 0
            and counts.get("blocked_triggered_semantics", 0) == 0,
            "unknown, conditional, and triggered operation semantics still block remap",
        ),
        _gate(
            "stat_identity_readiness",
            "blocked_by_identity_gap",
            counts.get("blocked_unresolved_stat_identity", 0) == 0,
            "unresolved stat identity rows still block remap",
        ),
        _gate(
            "skill_identity_readiness",
            "blocked_by_identity_gap",
            counts.get("blocked_unresolved_skill_identity", 0) == 0 and counts.get("blocked_ambiguous_skill_identity", 0) == 0,
            "unresolved or ambiguous skill identity rows still block remap",
        ),
        _gate(
            "unsupported_mechanic_exclusion",
            "blocked_by_unsupported_mechanics",
            counts.get("blocked_unsupported_mechanic", 0) == 0
            and counts.get("blocked_text_only_mechanic", 0) == 0
            and counts.get("blocked_scripted_mechanic", 0) == 0,
            "unsupported, text-only, and scripted rows remain excluded and block production remap",
        ),
        _gate(
            "provenance_readiness",
            "blocked_by_missing_provenance",
            counts.get("blocked_missing_provenance", 0) == 0,
            "candidate rows without provenance still block remap",
        ),
        _gate(
            "golden_baseline_evidence",
            "blocked_by_missing_baseline",
            False,
            "limited adapter fixtures do not constitute production golden baseline approval",
        ),
        _gate(
            "comparison_backed_execution",
            "partially_ready",
            summary["executed_row_count"] > 0
            and all(row["gate_evidence"]["comparison_backed"] for row in sample_execution["execution_rows"] if row["status"] == "executed"),
            "executed candidate rows are backed by accepted dry-run comparison rows",
            production_gate_override=False,
        ),
        _gate(
            "policy_decisions",
            "requires_policy_decision",
            False,
            "production remap requires approved identity, operation semantics, rollback, and limited opt-in policies",
        ),
    ]


def _gate(
    gate_id: str,
    audit_category: str,
    passed: bool,
    explanation: str,
    *,
    production_gate_override: bool | None = None,
) -> dict[str, Any]:
    production_gate_passed = passed if production_gate_override is None else production_gate_override
    if passed and production_gate_override is None:
        reported_category = "remap_ready"
    else:
        reported_category = audit_category
    return {
        "gate_id": gate_id,
        "audit_category": reported_category,
        "status": "passed" if passed else "blocked",
        "production_remap_gate_passed": production_gate_passed,
        "explanation": explanation,
    }


def _domain_stable_calculable_findings(execution_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    domains = sorted({row["domain"] for row in execution_rows})
    for domain in domains:
        rows = [row for row in execution_rows if row["domain"] == domain]
        executed = [row for row in rows if row["status"] == "executed"]
        blocked = [row for row in rows if row["status"] == "blocked"]
        rejected = [row for row in rows if row["status"] == "rejected"]
        findings.append(
            {
                "domain": domain,
                "executed_row_count": len(executed),
                "blocked_row_count": len(blocked),
                "rejected_row_count": len(rejected),
                "stable_calculable_for_dry_run_audit": bool(executed),
                "stable_calculable_for_production_remap": False,
                "finding": "partially_ready" if executed else "remap_blocked",
                "production_remap_blocker": "domain still has blocked or rejected candidate rows",
            }
        )
    return findings


def _deterministic_passed(limited_report: dict[str, Any], repeated_execution: dict[str, Any]) -> bool:
    return (
        limited_report["sample_execution"]["deterministic_hash"] == repeated_execution["deterministic_hash"]
        and limited_report["summary"]["deterministic"] is True
        and repeated_execution["summary"]["deterministic"] is True
    )


def _rollback_visibility_passed(sample_execution: dict[str, Any]) -> bool:
    required = {"deterministic_hash", "execution_category_counts", "execution_rows", "candidate_aggregates", "blocked_reasons", "safety_confirmations"}
    visible = set(sample_execution.get("rollback_visibility", {}).get("debug_visibility", []))
    return required <= visible


def _deterministic_guarantees(limited_report: dict[str, Any], repeated_execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "passed": _deterministic_passed(limited_report, repeated_execution),
        "sample_hash": limited_report["sample_execution"]["deterministic_hash"],
        "repeated_hash": repeated_execution["deterministic_hash"],
        "guarantees": limited_report["deterministic_guarantees"],
    }


def _rollback_debug_guarantees(limited_report: dict[str, Any]) -> dict[str, Any]:
    sample_execution = limited_report["sample_execution"]
    return {
        "passed": _rollback_visibility_passed(sample_execution),
        "debug_visibility": sample_execution["rollback_visibility"]["debug_visibility"],
        "guarantees": limited_report["rollback_debug_guarantees"],
    }


def _unsupported_mechanic_guarantees(limited_report: dict[str, Any]) -> dict[str, Any]:
    rows = limited_report["sample_execution"]["execution_rows"]
    blocked_categories = {"blocked_unsupported_mechanic", "blocked_text_only_mechanic", "blocked_scripted_mechanic"}
    blocked_rows = [row for row in rows if row["execution_category"] in blocked_categories]
    return {
        "passed": bool(blocked_rows) and all(row["status"] == "blocked" for row in blocked_rows),
        "blocked_row_count": len(blocked_rows),
        "blocked_categories": sorted(blocked_categories),
        "promoted_to_execution": [row["output_key"] for row in blocked_rows if row["status"] == "executed"],
    }


def _current_blockers(gates: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "gate_id": gate["gate_id"],
            "audit_category": gate["audit_category"],
            "explanation": gate["explanation"],
        }
        for gate in gates
        if not gate["production_remap_gate_passed"]
    ]


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# V3 Production Planner Remap Gate Audit",
        "",
        "Phase 11 is an audit-only gate review. It does not perform production remap or change production planner behavior.",
        "",
        "## Recommendation",
        "",
        f"- Final recommendation: `{report['final_recommendation']}`",
        f"- Production remap allowed: `{str(report['production_remap_allowed']).lower()}`",
        f"- Production remap enabled: `{str(report['production_remap_enabled']).lower()}`",
        "",
        "## Summary",
        "",
        f"- Audit gates: `{summary['audit_gate_count']}`",
        f"- Passing gates: `{summary['passing_gate_count']}`",
        f"- Blocking gates: `{summary['blocking_gate_count']}`",
        f"- Candidate executed rows: `{summary['candidate_execution_row_count']}`",
        f"- Candidate blocked rows: `{summary['candidate_blocked_row_count']}`",
        f"- Candidate rejected rows: `{summary['candidate_rejected_row_count']}`",
        f"- Stable production-remap domains: `{summary['stable_calculable_domain_count']}`",
        f"- Deterministic: `{str(summary['deterministic']).lower()}`",
        "",
        "## Gate Results",
        "",
        "| Gate | Status | Category | Production Gate Passed |",
        "| --- | --- | --- | --- |",
    ]
    for gate in report["audit_gates"]:
        lines.append(
            f"| `{gate['gate_id']}` | `{gate['status']}` | `{gate['audit_category']}` | `{str(gate['production_remap_gate_passed']).lower()}` |"
        )
    lines.extend(["", "## Stable-Calculable Findings", "", "| Domain | Executed | Blocked | Rejected | Production Remap Stable |", "| --- | ---: | ---: | ---: | --- |"])
    for finding in report["stable_calculable_findings"]:
        lines.append(
            f"| `{finding['domain']}` | `{finding['executed_row_count']}` | `{finding['blocked_row_count']}` | `{finding['rejected_row_count']}` | `{str(finding['stable_calculable_for_production_remap']).lower()}` |"
        )
    lines.extend(["", "## Current Blockers", ""])
    lines.extend(f"- `{blocker['gate_id']}`: {blocker['explanation']}" for blocker in report["current_blockers"])
    lines.extend(
        [
            "",
            "## Guarantees",
            "",
            f"- Deterministic guarantees passed: `{str(report['deterministic_guarantees']['passed']).lower()}`",
            f"- Rollback/debug guarantees passed: `{str(report['rollback_debug_guarantees']['passed']).lower()}`",
            f"- Unsupported-mechanic guarantees passed: `{str(report['unsupported_mechanic_guarantees']['passed']).lower()}`",
            "",
            "## Conclusion",
            "",
            "Production remap is not allowed from this audit state. The limited adapter remains suitable for opt-in audit execution only.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v3_production_remap_gate_audit_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V3_PRODUCTION_REMAP_GATE_AUDIT.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v3_production_remap_gate_audit_report()
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(report["final_recommendation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
