"""Read-only diagnostics for future v2 planner adapter consumption."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .adapter import V2PlannerSafeAdapter


DISPLAY_ONLY_DEPENDENCY_CLASSIFICATIONS = frozenset({"ready_for_adapter_later"})
BLOCKED_DEPENDENCY_CLASSIFICATIONS = frozenset(
    {
        "blocked_by_value_normalization",
        "blocked_by_identity_resolution",
        "blocked_by_unsupported_mechanics",
        "blocked_by_missing_tests",
        "blocked_by_schema_mismatch",
        "blocked_by_behavioral_risk",
        "manual_only_currently",
        "unknown_needs_review",
    }
)


def build_planner_adapter_diagnostics(*, root: str | Path | None = None, sample_limit: int = 10) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[4]
    generated_dir = repo_root / "docs" / "generated"

    adapter_summary = V2PlannerSafeAdapter(root=repo_root).summarize_eligibility(sample_limit=sample_limit)
    readiness = _load_json(generated_dir / "v2_planner_remap_readiness_report.json")

    display_only_candidates = _display_only_candidates(readiness)
    blocked_mechanical_data = _blocked_mechanical_data(readiness)
    future_phase_status = _future_phase_status(readiness)
    top_blocked_reasons = _top_blocked_reasons(adapter_summary["blocked_reason_counts"])
    domain_modes = _domain_modes(adapter_summary["domains"])
    safety = _safety_confirmations(adapter_summary, readiness)

    return {
        "schema_version": "v2.planner_adapter_diagnostics.1",
        "summary": {
            "domains_checked": adapter_summary["summary"]["domain_count"],
            "adapter_visible_record_count": adapter_summary["summary"]["inspected_modifier_count"],
            "planner_calculable_record_count": adapter_summary["summary"]["eligible_planner_calculable_count"],
            "blocked_record_count": adapter_summary["summary"]["blocked_modifier_count"],
            "stable_calculable_count": adapter_summary["summary"]["stable_calculable_count"],
            "display_only_candidate_count": len(display_only_candidates),
            "blocked_mechanical_category_count": len(blocked_mechanical_data),
            "production_consumed": False,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "domains": domain_modes,
        "adapter_visible_data": {
            "description": "Records the v2 adapter can inspect and explain.",
            "domain_count": adapter_summary["summary"]["domain_count"],
            "record_count": adapter_summary["summary"]["inspected_modifier_count"],
        },
        "planner_calculable_data": {
            "description": "Records the adapter would allow into planner math today.",
            "record_count": adapter_summary["summary"]["eligible_planner_calculable_count"],
            "stable_calculable_count": adapter_summary["summary"]["stable_calculable_count"],
            "status": "none_available",
        },
        "display_only_candidates": display_only_candidates,
        "blocked_mechanical_data": blocked_mechanical_data,
        "blocked_reason_counts": dict(sorted(adapter_summary["blocked_reason_counts"].items())),
        "top_blocked_reasons": top_blocked_reasons,
        "future_remap_phase_status": future_phase_status,
        "safety_confirmations": safety,
        "samples": {
            "eligible": adapter_summary["eligible_samples"],
            "blocked": adapter_summary["blocked_samples"],
        },
        "metadata": {
            "source": "v2_planner_adapter_diagnostics",
            "read_only": True,
            "diagnostic_only": True,
            "optional_route_added": False,
            "production_planner_import_required": False,
            "planner_remap_performed": False,
        },
    }


def _domain_modes(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for domain in domains:
        inspected = int(domain.get("inspected_count", 0) or 0)
        eligible = int(domain.get("eligible_count", 0) or 0)
        blocked = int(domain.get("blocked_count", 0) or 0)
        mode = "planner_calculable" if eligible else "adapter_visible_blocked"
        results.append(
            {
                "domain": domain.get("domain"),
                "mode": mode,
                "adapter_visible_count": inspected,
                "planner_calculable_count": eligible,
                "blocked_count": blocked,
                "stable_calculable_count": int(domain.get("stable_calculable_count", 0) or 0),
                "blocked_reason_counts": domain.get("blocked_reason_counts", {}),
            }
        )
    return results


def _display_only_candidates(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in readiness.get("dependency_classifications", []):
        classification = str(item.get("classification") or "")
        if classification not in DISPLAY_ONLY_DEPENDENCY_CLASSIFICATIONS:
            continue
        candidates.append(
            {
                "category": item.get("category"),
                "classification": classification,
                "mode": "display_only_candidate",
                "notes": item.get("blockers", []),
                "planner_calculable": False,
            }
        )
    return candidates


def _blocked_mechanical_data(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    for item in readiness.get("dependency_classifications", []):
        classification = str(item.get("classification") or "")
        if classification not in BLOCKED_DEPENDENCY_CLASSIFICATIONS:
            continue
        blocked.append(
            {
                "category": item.get("category"),
                "classification": classification,
                "mode": "blocked_mechanical_data",
                "blocked_reasons": item.get("blockers", []),
                "planner_calculable": False,
            }
        )
    return blocked


def _future_phase_status(readiness: dict[str, Any]) -> list[dict[str, Any]]:
    phase_status: list[dict[str, Any]] = []
    for phase in readiness.get("future_remap_sequence", []):
        order = int(phase.get("order", 0) or 0)
        if order in {1, 2, 3, 4, 5}:
            status = "diagnostic_or_display_only_candidate"
        else:
            status = "blocked_until_safety_gates_pass"
        phase_status.append(
            {
                "order": order,
                "name": phase.get("name"),
                "status": status,
                "goal": phase.get("goal"),
                "required_tests": phase.get("required_tests", []),
            }
        )
    return phase_status


def _top_blocked_reasons(blocked_reason_counts: dict[str, int], *, limit: int = 10) -> list[dict[str, Any]]:
    counter = Counter({str(reason): int(count) for reason, count in blocked_reason_counts.items()})
    return [
        {"reason": reason, "count": count}
        for reason, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _safety_confirmations(adapter_summary: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    readiness_safety = readiness.get("safety_confirmations", {}) if isinstance(readiness, dict) else {}
    return {
        "production_consumed": False,
        "planner_remap_performed": False,
        "planner_output_changed": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "skill_identity_bridge_added": False,
        "stable_calculable_count": int(adapter_summary["summary"].get("stable_calculable_count", 0) or 0),
        "eligible_planner_calculable_count": int(
            adapter_summary["summary"].get("eligible_planner_calculable_count", 0) or 0
        ),
        "blocked_modifier_count": int(adapter_summary["summary"].get("blocked_modifier_count", 0) or 0),
        "value_normalization_status": "audit_only",
        "skill_identity_bridge_status": "unbridged",
        "unresolved_skill_reference_count": readiness_safety.get("unresolved_skill_reference_count"),
        "ambiguous_skill_reference_count": readiness_safety.get("ambiguous_skill_reference_count"),
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
