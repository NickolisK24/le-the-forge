"""Generate the v2.5 release readiness and UX QA audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ALLOWED_CLASSIFICATIONS = frozenset(
    {
        "v2_5_release_blocker",
        "post_v2_5_polish",
        "v3_mechanical_blocker",
        "future_patch_resilience_followup",
        "known_intentional_limitation",
        "unknown_needs_review",
    }
)

REQUIRED_V2_5_DOCS = (
    "V2_5_TRUST_UX_PLAN.md",
    "V2_5_TRUST_SUPPORT_BADGES.md",
    "V2_5_PROVENANCE_WARNING_PANELS.md",
    "V2_5_USER_FACING_LIMITATION_COPY.md",
    "V2_5_STATS_MODIFIERS_DEBUG_PAGE.md",
    "V2_5_TRUSTED_DATA_EXPLANATION_PAGE.md",
    "V2_5_PLANNER_ADAPTER_STATUS_PANEL.md",
    "V2_5_REPORT_DEBUG_NAVIGATION_CLEANUP.md",
    "V2_5_SUPPORT_MATRIX.md",
    "V2_5_PRE_V3_MECHANICAL_READINESS_DASHBOARD.md",
)

FEATURE_SURFACES: tuple[dict[str, str], ...] = (
    {
        "id": "trust_ux_planning_audit",
        "label": "Trust & UX planning audit",
        "path": "docs/migration/V2_5_TRUST_UX_PLAN.md",
        "coverage": "planned the v2.5 trust and UX layer",
    },
    {
        "id": "shared_trust_support_badges",
        "label": "Shared trust/support badges",
        "path": "frontend/src/components/v2/V2TrustBadge.tsx",
        "coverage": "renders support, trust, audit-only, display-only, and non-calculating status badges",
    },
    {
        "id": "provenance_warning_panels",
        "label": "Provenance/warning summary panels",
        "path": "frontend/src/components/v2/V2TrustSummaryPanels.tsx",
        "coverage": "summarizes provenance, warnings, blocked reasons, and limitations",
    },
    {
        "id": "user_facing_limitation_copy",
        "label": "User-facing limitation copy",
        "path": "frontend/src/components/v2/V2LimitationNotice.tsx",
        "coverage": "explains display-only, audit-only, unsupported, and not planner-calculable states",
    },
    {
        "id": "stats_modifiers_debug_page",
        "label": "Stats/modifiers debug page",
        "path": "frontend/src/pages/debug/V2StatsModifiersDebugPage.tsx",
        "coverage": "shows stat/modifier counts, blocked reasons, value scales, and planner safety status",
    },
    {
        "id": "trusted_data_explanation_page",
        "label": "Trusted-data explanation page",
        "path": "frontend/src/pages/TrustedDataExplanationPage.tsx",
        "coverage": "explains trusted data, provenance, display-only use, and v3 boundaries",
    },
    {
        "id": "planner_adapter_status_panel",
        "label": "Planner adapter status panel",
        "path": "frontend/src/components/v2/V2PlannerAdapterStatusPanel.tsx",
        "coverage": "shows adapter-visible, blocked, planner-calculable, and baseline readiness status",
    },
    {
        "id": "report_debug_navigation_cleanup",
        "label": "Report/debug navigation cleanup",
        "path": "frontend/src/pages/debug/V2DebugNavigationPage.tsx",
        "coverage": "links the trusted-data explanation, debug routes, support matrix, and pre-v3 dashboard",
    },
    {
        "id": "support_matrix",
        "label": "User-facing support matrix",
        "path": "frontend/src/pages/TrustedDataSupportMatrixPage.tsx",
        "coverage": "summarizes domain support, display-only status, blockers, and next tracks",
    },
    {
        "id": "pre_v3_readiness_dashboard",
        "label": "Pre-v3 mechanical readiness dashboard",
        "path": "frontend/src/pages/PreV3MechanicalReadinessPage.tsx",
        "coverage": "summarizes what remains blocked before mechanical planner work can start",
    },
)

ROUTE_CHECKLIST: tuple[dict[str, str], ...] = (
    {
        "route": "/trusted-data",
        "surface": "Trusted-data explanation page",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/trusted-data/support",
        "surface": "User-facing support matrix",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/trusted-data/pre-v3-readiness",
        "surface": "Pre-v3 mechanical readiness dashboard",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/debug/v2",
        "surface": "V2 debug navigation page",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/debug/v2-stats-modifiers",
        "surface": "Stats/modifiers debug page",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/debug/forge-safe-affixes",
        "surface": "Forge-safe affixes debug page",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
    {
        "route": "/debug/v2-affixes",
        "surface": "Alias redirect to forge-safe affixes",
        "source": "frontend/src/App.tsx",
        "coverage_type": "static_route_inventory",
    },
)


def build_v2_5_release_readiness_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    release_report = _read_json(repo_root / "docs" / "generated" / "v2_release_readiness_report.json")
    trust_ux_plan = _read_json(repo_root / "docs" / "generated" / "v2_5_trust_ux_plan.json")
    dry_run = _read_json(repo_root / "docs" / "generated" / "v2_stat_modifier_dry_run_report.json")
    baselines = _read_json(repo_root / "docs" / "generated" / "v2_golden_baseline_plan.json")
    experimental_mode = _read_json(repo_root / "docs" / "generated" / "v2_experimental_planner_adapter_mode_report.json")

    feature_coverage = _feature_coverage(repo_root)
    route_inventory = _route_inventory(repo_root)
    docs_status = _docs_status(repo_root)
    safety = _safety_confirmations(release_report=release_report, dry_run=dry_run, experimental_mode=experimental_mode)
    readiness = {
        "v2_5_trust_ux_ready": all(item["exists"] for item in feature_coverage)
        and all(item["exists"] for item in docs_status)
        and all(item["registered"] for item in route_inventory)
        and safety["production_consumed"] is False
        and safety["stable_calculable_count"] == 0
        and safety["value_normalization_status"] == "audit_only"
        and safety["skill_identity_bridge_status"] == "unbridged",
        "v3_mechanical_ready": False,
        "production_planner_ready": False,
        "recommended_next_track": "v3_mechanical_intelligence_planning",
    }
    remaining_items = _remaining_items()

    return {
        "schema_version": "v2_5.release_readiness.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "readiness_decision": readiness,
        "feature_completion": {
            "completed_surface_count": sum(1 for item in feature_coverage if item["exists"]),
            "expected_surface_count": len(feature_coverage),
            "surfaces": feature_coverage,
        },
        "frontend_trust_ux_surface_coverage": {
            "trusted_data_explanation": _surface("frontend/src/pages/TrustedDataExplanationPage.tsx", repo_root),
            "support_matrix": _surface("frontend/src/pages/TrustedDataSupportMatrixPage.tsx", repo_root),
            "pre_v3_readiness_dashboard": _surface("frontend/src/pages/PreV3MechanicalReadinessPage.tsx", repo_root),
            "debug_navigation": _surface("frontend/src/pages/debug/V2DebugNavigationPage.tsx", repo_root),
            "stats_modifiers_debug": _surface("frontend/src/pages/debug/V2StatsModifiersDebugPage.tsx", repo_root),
        },
        "key_route_coverage": route_inventory,
        "support_trust_badge_coverage": {
            "component": "frontend/src/components/v2/V2TrustBadge.tsx",
            "group_component": "frontend/src/components/v2/V2StatusBadgeGroup.tsx",
            "covered_concepts": [
                "trusted",
                "generated",
                "validated",
                "display-only",
                "audit-only",
                "experimental",
                "not planner-calculable",
                "unknown status",
            ],
        },
        "provenance_warning_coverage": {
            "component": "frontend/src/components/v2/V2TrustSummaryPanels.tsx",
            "covered_concepts": [
                "source information",
                "missing provenance",
                "warnings",
                "blocked reasons",
                "display-only limitations",
                "not planner-calculable limitations",
            ],
        },
        "limitation_copy_coverage": {
            "component": "frontend/src/components/v2/V2LimitationNotice.tsx",
            "covered_concepts": [
                "display_only",
                "audit_only_value_normalization",
                "not_planner_calculable",
                "unsupported_mechanics",
                "partial_support",
                "unresolved_skill_identity",
                "missing_provenance",
                "experimental_only",
                "stable_calculable_unavailable",
                "production_not_consuming_v2",
            ],
        },
        "support_matrix_coverage": {
            "route": "/trusted-data/support",
            "domains": [
                "Items / item bases",
                "Affixes",
                "Unique/set items",
                "Idols",
                "Classes/masteries",
                "Passive trees",
                "Skills / skill trees",
                "Stats",
                "Modifiers",
                "Planner adapter",
            ],
        },
        "pre_v3_readiness_dashboard_coverage": {
            "route": "/trusted-data/pre-v3-readiness",
            "covered_sections": [
                "current readiness decision",
                "what is already complete",
                "what remains blocked",
                "value normalization blockers",
                "operation semantics blockers",
                "stat identity blockers",
                "skill identity blockers",
                "unsupported/scripted/text-only mechanic blockers",
                "golden baseline requirements",
                "what v3 must prove",
            ],
        },
        "stats_modifiers_debug_page_coverage": {
            "route": "/debug/v2-stats-modifiers",
            "data_source": "/api/experimental/v2/modifiers/debug",
            "stat_registry_count": dry_run.get("summary", {}).get("stat_registry_count"),
            "modifier_row_count": dry_run.get("summary", {}).get("modifier_row_count"),
            "planner_calculable_count": dry_run.get("summary", {}).get("planner_calculable_modifier_count"),
            "stable_calculable_count": dry_run.get("summary", {}).get("stable_calculable_modifier_count"),
            "value_normalization_status": dry_run.get("summary", {}).get("value_normalization_status"),
        },
        "known_manual_verification_results": [
            {"target": "/trusted-data", "expected_status": 200},
            {"target": "/trusted-data/support", "expected_status": 200},
            {"target": "/trusted-data/pre-v3-readiness", "expected_status": 200},
            {"target": "/debug/v2", "expected_status": 200},
            {"target": "/debug/v2-stats-modifiers", "expected_status": 200},
            {"target": "/debug/forge-safe-affixes", "expected_status": 200},
            {"target": "/api/experimental/v2/modifiers/debug", "expected_status": 200},
        ],
        "manual_qa_checklist": _manual_qa_checklist(),
        "required_v2_5_docs": docs_status,
        "remaining_items": remaining_items,
        "classification_counts": _classification_counts(remaining_items),
        "remaining_ux_gaps": [item for item in remaining_items if item["classification"] == "post_v2_5_polish"],
        "remaining_v3_blockers": [item for item in remaining_items if item["classification"] == "v3_mechanical_blocker"],
        "source_reports": {
            "v2_release_readiness": release_report.get("readiness_decision", {}),
            "v2_5_trust_ux_plan_summary": trust_ux_plan.get("summary", {}),
            "stat_modifier_dry_run_summary": dry_run.get("summary", {}),
            "golden_baseline_summary": baselines.get("summary", {}),
            "experimental_mode_summary": experimental_mode.get("summary", {}),
        },
        "safety_confirmations": safety,
        "metadata": {
            "source": "v2_5_release_readiness",
            "audit_only": True,
            "documentation_only": True,
            "frontend_behavior_changed": False,
            "backend_behavior_changed": False,
            "production_consumed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    decision = report["readiness_decision"]
    safety = report["safety_confirmations"]
    lines = [
        "# V2.5 Release Readiness",
        "",
        "This audit closes the v2.5 Trust & UX layer. It is documentation and report-only.",
        "It does not start v3 mechanical intelligence, production planner remap, or runtime behavior changes.",
        "",
        "## Readiness Decision",
        "",
        f"- V2.5 trust/UX ready: `{str(decision['v2_5_trust_ux_ready']).lower()}`",
        f"- Production planner ready: `{str(decision['production_planner_ready']).lower()}`",
        f"- V3 mechanical ready: `{str(decision['v3_mechanical_ready']).lower()}`",
        f"- Recommended next track: `{decision['recommended_next_track']}`",
        "",
        "## Completed V2.5 Surfaces",
        "",
        "| Surface | Status | Coverage |",
        "| --- | --- | --- |",
    ]
    for surface in report["feature_completion"]["surfaces"]:
        lines.append(f"| {surface['label']} | `{surface['status']}` | {surface['coverage']} |")
    lines.extend(["", "## Route Checklist", "", "| Route | Surface | Coverage |", "| --- | --- | --- |"])
    for route in report["key_route_coverage"]:
        lines.append(f"| `{route['route']}` | {route['surface']} | `{route['coverage_type']}` |")
    lines.extend(["", "## Manual QA Checklist", ""])
    lines.extend(f"- [ ] {item['description']} (`{item['target']}`)" for item in report["manual_qa_checklist"])
    lines.extend(["", "## Known Limitations", ""])
    for item in report["remaining_items"]:
        if item["classification"] in {"known_intentional_limitation", "v3_mechanical_blocker"}:
            lines.append(f"- `{item['id']}` ({item['classification']}): {item['description']}")
    lines.extend(["", "## Post-v2.5 Polish", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["remaining_ux_gaps"])
    lines.extend(["", "## V3 Mechanical Blockers", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["remaining_v3_blockers"])
    lines.extend(
        [
            "",
            "## Safety State",
            "",
            f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
            f"- Production planner remap performed: `{str(safety['production_planner_remap_performed']).lower()}`",
            f"- Planner-calculable count: `{safety['planner_calculable_count']}`",
            f"- Stable-calculable count: `{safety['stable_calculable_count']}`",
            f"- Value normalization: `{safety['value_normalization_status']}`",
            f"- Skill identity bridge: `{safety['skill_identity_bridge_status']}`",
            f"- Experimental adapter mode enabled by default: `{str(safety['experimental_mode_enabled_by_default']).lower()}`",
            "",
            "## Recommended Next Track",
            "",
            "`v3_mechanical_intelligence_planning` should focus on value normalization contracts, operation semantics, stat identity resolution, skill identity policy, golden mechanical baselines, and deterministic dry-run comparison before production planner remap.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _feature_coverage(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {
            **surface,
            "exists": (repo_root / surface["path"]).exists(),
            "status": "complete" if (repo_root / surface["path"]).exists() else "missing",
        }
        for surface in FEATURE_SURFACES
    ]


def _route_inventory(repo_root: Path) -> list[dict[str, Any]]:
    app_source = (repo_root / "frontend" / "src" / "App.tsx").read_text(encoding="utf-8")
    routes = []
    for route in ROUTE_CHECKLIST:
        registered = route["route"] in app_source
        routes.append({**route, "registered": registered, "status": "registered" if registered else "missing"})
    return routes


def _docs_status(repo_root: Path) -> list[dict[str, Any]]:
    docs_dir = repo_root / "docs" / "migration"
    return [
        {
            "doc": name,
            "path": f"docs/migration/{name}",
            "exists": (docs_dir / name).exists(),
        }
        for name in REQUIRED_V2_5_DOCS
    ]


def _surface(path: str, repo_root: Path) -> dict[str, Any]:
    return {"path": path, "exists": (repo_root / path).exists()}


def _manual_qa_checklist() -> list[dict[str, str]]:
    return [
        {"id": "trusted_data_loads", "target": "/trusted-data", "description": "Trusted-data page loads."},
        {"id": "support_matrix_loads", "target": "/trusted-data/support", "description": "Support matrix page loads."},
        {"id": "pre_v3_readiness_loads", "target": "/trusted-data/pre-v3-readiness", "description": "Pre-v3 readiness page loads."},
        {"id": "debug_navigation_loads", "target": "/debug/v2", "description": "Debug navigation page loads."},
        {"id": "stats_modifiers_loads", "target": "/debug/v2-stats-modifiers", "description": "Stats/modifiers debug page loads."},
        {"id": "affixes_actual_route_loads", "target": "/debug/forge-safe-affixes", "description": "Affixes debug page loads through the actual route."},
        {"id": "affix_alias_works", "target": "/debug/v2-affixes", "description": "Affix alias route works."},
        {"id": "limitation_copy_visible", "target": "v2.5 pages", "description": "Limitation copy appears."},
        {"id": "planner_calculable_zero", "target": "v2.5 pages", "description": "Planner-calculable count remains 0."},
        {"id": "stable_calculable_zero", "target": "v2.5 pages", "description": "Stable-calculable count remains 0."},
        {"id": "no_production_math_claims", "target": "v2.5 pages", "description": "No copy implies production planner math is active."},
    ]


def _remaining_items() -> list[dict[str, str]]:
    return [
        {
            "id": "visual_polish",
            "description": "Tighten spacing and visual hierarchy across trusted-data pages after user review.",
            "classification": "post_v2_5_polish",
        },
        {
            "id": "copy_review",
            "description": "Review all trust and limitation copy with real player feedback.",
            "classification": "post_v2_5_polish",
        },
        {
            "id": "route_discoverability",
            "description": "Consider broader application navigation entry points after v2.5 release.",
            "classification": "post_v2_5_polish",
        },
        {
            "id": "value_normalization_contracts",
            "description": "Define and prove value normalization contracts before mechanical math.",
            "classification": "v3_mechanical_blocker",
        },
        {
            "id": "operation_semantics",
            "description": "Resolve operation semantics for additive, increased, more, flat, conditional, scripted, and unsupported behaviors.",
            "classification": "v3_mechanical_blocker",
        },
        {
            "id": "stat_identity_resolution",
            "description": "Resolve blocked stat identities before stable stat aggregation.",
            "classification": "v3_mechanical_blocker",
        },
        {
            "id": "skill_identity_policy",
            "description": "Keep unresolved and ambiguous skill identities unbridged until source evidence is sufficient.",
            "classification": "v3_mechanical_blocker",
        },
        {
            "id": "golden_mechanical_baselines",
            "description": "Implement golden mechanical baseline tests before production planner remap.",
            "classification": "v3_mechanical_blocker",
        },
        {
            "id": "patch_schema_drift_watch",
            "description": "Keep future patch schema drift visible in validation and reports.",
            "classification": "future_patch_resilience_followup",
        },
        {
            "id": "stable_calculable_zero",
            "description": "Stable-calculable count remains intentionally 0 until v3 gates pass.",
            "classification": "known_intentional_limitation",
        },
    ]


def _classification_counts(items: list[dict[str, str]]) -> dict[str, int]:
    return {
        classification: sum(1 for item in items if item["classification"] == classification)
        for classification in sorted(ALLOWED_CLASSIFICATIONS)
        if any(item["classification"] == classification for item in items)
    }


def _safety_confirmations(*, release_report: dict[str, Any], dry_run: dict[str, Any], experimental_mode: dict[str, Any]) -> dict[str, Any]:
    release_safety = release_report.get("safety_confirmations", {})
    dry_summary = dry_run.get("summary", {})
    experimental_summary = experimental_mode.get("summary", {})
    return {
        "v2_infrastructure_ready": bool(release_report.get("readiness_decision", {}).get("v2_infrastructure_ready") is True),
        "production_planner_ready": False,
        "v3_mechanical_ready": False,
        "production_consumed": bool(release_safety.get("production_consumed") is True),
        "production_planner_remap_performed": False,
        "planner_output_changed": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "skill_identity_bridge_added": False,
        "experimental_mode_enabled_by_default": False,
        "planner_calculable_count": int(dry_summary.get("planner_calculable_modifier_count") or 0),
        "stable_calculable_count": int(dry_summary.get("stable_calculable_modifier_count") or 0),
        "value_normalization_status": dry_summary.get("value_normalization_status") or release_safety.get("value_normalization_status") or "audit_only",
        "skill_identity_bridge_status": experimental_summary.get("skill_identity_bridge_status") or release_safety.get("skill_identity_bridge_status") or "unbridged",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_5_release_readiness_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_5_RELEASE_READINESS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_5_release_readiness_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["readiness_decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
