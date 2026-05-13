"""Generate the v2.5 trust and UX planning audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


UX_CLASSIFICATIONS = frozenset(
    {
        "ready_for_v2_5",
        "needs_copy_design",
        "needs_frontend_component",
        "needs_backend_summary",
        "debug_only",
        "blocked_by_v3_mechanics",
        "blocked_by_missing_route",
        "blocked_by_missing_user_flow",
        "unknown_needs_review",
    }
)

FRONTEND_INVENTORY = (
    {
        "id": "v2_affixes_debug",
        "path": "frontend/src/pages/debug/ForgeSafeAffixesDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "surface affix trust, provenance, and unsupported/value-scale limitation summaries",
    },
    {
        "id": "v2_items_debug",
        "path": "frontend/src/pages/debug/V2ItemsDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "surface item/base display metadata and implicit limitation summaries",
    },
    {
        "id": "v2_unique_set_debug",
        "path": "frontend/src/pages/debug/V2UniqueSetDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "explain unsupported unique/set behavior without implying calculation support",
    },
    {
        "id": "v2_idols_debug",
        "path": "frontend/src/pages/debug/V2IdolsDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "surface idol support and warning summaries",
    },
    {
        "id": "v2_class_mastery_debug",
        "path": "frontend/src/pages/debug/V2ClassMasteryDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "explain class/mastery identity and unresolved skill ownership limitations",
    },
    {
        "id": "v2_passives_debug",
        "path": "frontend/src/pages/debug/V2PassivesDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "surface passive identity/provenance while keeping effects non-calculating",
    },
    {
        "id": "v2_skills_debug",
        "path": "frontend/src/pages/debug/V2SkillsDebugPage.tsx",
        "current_role": "debug_page",
        "v2_5_need": "surface skill identity gaps and unsupported skill behavior clearly",
    },
    {
        "id": "v2_envelope_helpers",
        "path": "frontend/src/lib/v2ApiEnvelope.ts",
        "current_role": "shared_helper",
        "v2_5_need": "reuse parsed support/provenance/debug data for user-facing summaries",
    },
    {
        "id": "v2_envelope_panels",
        "path": "frontend/src/components/v2/V2EnvelopePanels.tsx",
        "current_role": "shared_component",
        "v2_5_need": "evolve debug panels into clearer trust/support summary components",
    },
    {
        "id": "build_planner_page",
        "path": "frontend/src/components/features/build/BuildPlannerPage.tsx",
        "current_role": "planner_user_flow",
        "v2_5_need": "add non-calculating trust status copy only after shared UX components exist",
    },
)

UX_ITEMS: tuple[dict[str, Any], ...] = (
    {
        "id": "support_trust_badges",
        "category": "support/trust badges",
        "classification": "needs_frontend_component",
        "user_facing": True,
        "developer_only": False,
        "description": "Create reusable badges for support status, trust level, stable-calculable status, and audit-only status.",
        "available_data": ["support_summary", "support_status", "trust_level", "stable_calculable_count"],
        "target_surfaces": ["v2 debug pages", "planner-adjacent metadata panels"],
        "blocked_by_v3": False,
    },
    {
        "id": "provenance_summaries",
        "category": "provenance summaries",
        "classification": "needs_frontend_component",
        "user_facing": True,
        "developer_only": False,
        "description": "Summarize source artifact, source path, extraction provenance, and generated report origin without dumping raw JSON.",
        "available_data": ["provenance", "source_path", "generated artifacts", "repository reports"],
        "target_surfaces": ["item", "affix", "passive", "skill", "stats/modifiers"],
        "blocked_by_v3": False,
    },
    {
        "id": "limitation_warnings",
        "category": "limitation warnings",
        "classification": "needs_copy_design",
        "user_facing": True,
        "developer_only": False,
        "description": "Write clear user-facing copy for what is visible, what is debug-only, and what is not calculated yet.",
        "available_data": ["blocked_reason_counts", "safety_confirmations", "release readiness blockers"],
        "target_surfaces": ["trusted-data explanation page", "planner-adjacent panels"],
        "blocked_by_v3": False,
    },
    {
        "id": "unsupported_mechanic_messaging",
        "category": "unsupported mechanic messaging",
        "classification": "ready_for_v2_5",
        "user_facing": True,
        "developer_only": False,
        "description": "Expose concise unsupported/scripted/text-only explanations while preserving raw debug details separately.",
        "available_data": ["unsupported reports", "special_behavior_classification", "blocked_reason_counts"],
        "target_surfaces": ["uniques/sets", "passives", "skills", "stats/modifiers"],
        "blocked_by_v3": False,
    },
    {
        "id": "stable_calculable_explanation",
        "category": "stable-calculable explanation",
        "classification": "needs_copy_design",
        "user_facing": True,
        "developer_only": False,
        "description": "Explain that stable-calculable is currently zero because safety gates are doing their job.",
        "available_data": ["stable_calculable_count", "adapter report", "release readiness report"],
        "target_surfaces": ["trusted-data explanation page", "stats/modifiers debug"],
        "blocked_by_v3": False,
    },
    {
        "id": "audit_only_value_policy_explanation",
        "category": "audit-only value normalization explanation",
        "classification": "needs_copy_design",
        "user_facing": True,
        "developer_only": False,
        "description": "Explain source units, unknown scales, and why values are not planner-normalized.",
        "available_data": ["value normalization report", "source_units count", "unknown value scale count"],
        "target_surfaces": ["stats/modifiers debug", "trusted-data explanation page"],
        "blocked_by_v3": False,
    },
    {
        "id": "skill_identity_gap_explanation",
        "category": "skill identity gap explanation",
        "classification": "needs_copy_design",
        "user_facing": True,
        "developer_only": False,
        "description": "Explain 60/63 safe identity matches and why the remaining unresolved/ambiguous references are not bridged.",
        "available_data": ["skill identity report", "passive/skill identity remap report"],
        "target_surfaces": ["skills debug", "classes/masteries debug", "trusted-data explanation page"],
        "blocked_by_v3": False,
    },
    {
        "id": "planner_safe_adapter_explanation",
        "category": "planner-safe adapter explanation",
        "classification": "needs_copy_design",
        "user_facing": True,
        "developer_only": False,
        "description": "Explain adapter-visible versus planner-calculable versus display-only data.",
        "available_data": ["planner adapter diagnostics", "experimental adapter mode report"],
        "target_surfaces": ["planner-adjacent status panel", "trusted-data explanation page"],
        "blocked_by_v3": False,
    },
    {
        "id": "stats_modifiers_debug_page",
        "category": "dedicated stats/modifiers debug page",
        "classification": "needs_frontend_component",
        "user_facing": False,
        "developer_only": False,
        "description": "Add a focused debug page for stat registry, modifier registry, blocked reasons, operations, and value scale distributions.",
        "available_data": ["stat registry", "modifier registry", "dry-run report", "blocked reason report"],
        "target_surfaces": ["new v2 stats/modifiers debug page"],
        "blocked_by_v3": False,
    },
    {
        "id": "report_navigation",
        "category": "report/navigation improvements",
        "classification": "needs_frontend_component",
        "user_facing": True,
        "developer_only": False,
        "description": "Add clearer navigation between trusted-data pages, reports, and limitation summaries.",
        "available_data": ["experimental route coverage", "migration docs", "generated reports"],
        "target_surfaces": ["debug navigation", "trusted-data explanation page"],
        "blocked_by_v3": False,
    },
    {
        "id": "trusted_data_explanation_page",
        "category": "non-developer trusted-data explanation page",
        "classification": "needs_frontend_component",
        "user_facing": True,
        "developer_only": False,
        "description": "Create a plain-language page that explains what v2 can show, cannot calculate, and why.",
        "available_data": ["release readiness report", "support summaries", "blocked reason summaries"],
        "target_surfaces": ["new trusted-data explanation route"],
        "blocked_by_v3": False,
    },
    {
        "id": "what_can_calculate_messaging",
        "category": "what this tool can/cannot calculate yet messaging",
        "classification": "ready_for_v2_5",
        "user_facing": True,
        "developer_only": False,
        "description": "Surface concise messaging that current production planner math remains legacy and v2 is trusted metadata/display infrastructure.",
        "available_data": ["release readiness decision", "safety confirmations"],
        "target_surfaces": ["planner-adjacent panels", "trusted-data explanation page"],
        "blocked_by_v3": False,
    },
    {
        "id": "raw_debug_payloads",
        "category": "developer-only raw debug payloads",
        "classification": "debug_only",
        "user_facing": False,
        "developer_only": True,
        "description": "Keep raw API envelopes, full provenance paths, and sample blocked records in debug views rather than user-facing planner flows.",
        "available_data": ["debug", "raw reports", "samples"],
        "target_surfaces": ["debug pages only"],
        "blocked_by_v3": False,
    },
    {
        "id": "mechanical_delta_explanations",
        "category": "mechanical calculation explanations",
        "classification": "blocked_by_v3_mechanics",
        "user_facing": False,
        "developer_only": False,
        "description": "Do not promise mechanical deltas until value normalization, operation semantics, and golden baselines exist.",
        "available_data": ["dry-run report", "golden baseline plan"],
        "target_surfaces": ["future mechanical readiness dashboard"],
        "blocked_by_v3": True,
    },
)

V2_5_SEQUENCE: tuple[dict[str, Any], ...] = (
    {"order": 1, "id": "shared_trust_support_badges", "description": "Build shared trust/support badge components.", "primary_items": ["support_trust_badges"]},
    {"order": 2, "id": "shared_provenance_warning_panels", "description": "Build shared provenance and warning summary panels.", "primary_items": ["provenance_summaries", "limitation_warnings"]},
    {"order": 3, "id": "user_facing_limitation_copy", "description": "Write and apply limitation copy for unsupported, audit-only, and non-calculating states.", "primary_items": ["unsupported_mechanic_messaging", "stable_calculable_explanation", "audit_only_value_policy_explanation", "skill_identity_gap_explanation"]},
    {"order": 4, "id": "stats_modifiers_debug_page", "description": "Add a dedicated stats/modifiers debug page.", "primary_items": ["stats_modifiers_debug_page"]},
    {"order": 5, "id": "trusted_data_explanation_page", "description": "Add a non-developer trusted-data explanation page.", "primary_items": ["trusted_data_explanation_page", "what_can_calculate_messaging"]},
    {"order": 6, "id": "planner_safe_adapter_status_panel", "description": "Expose planner-safe adapter status as non-calculating context.", "primary_items": ["planner_safe_adapter_explanation"]},
    {"order": 7, "id": "report_debug_navigation_cleanup", "description": "Improve navigation across reports and debug routes.", "primary_items": ["report_navigation"]},
    {"order": 8, "id": "user_facing_support_matrix", "description": "Create a compact support matrix for domains and mechanics.", "primary_items": ["support_trust_badges", "unsupported_mechanic_messaging"]},
    {"order": 9, "id": "pre_v3_mechanical_readiness_dashboard", "description": "Create a readiness dashboard that remains warning-only until v3 gates pass.", "primary_items": ["mechanical_delta_explanations"]},
)


def build_v2_5_trust_ux_plan(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    release_report = _read_json(repo_root / "docs" / "generated" / "v2_release_readiness_report.json")
    items = [dict(item) for item in UX_ITEMS]
    frontend_inventory = _frontend_inventory(repo_root)

    return {
        "schema_version": "v2_5.trust_ux_plan.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": {
            "ux_item_count": len(items),
            "ready_for_v2_5_count": _count(items, "ready_for_v2_5"),
            "needs_copy_design_count": _count(items, "needs_copy_design"),
            "needs_frontend_component_count": _count(items, "needs_frontend_component"),
            "debug_only_count": _count(items, "debug_only"),
            "blocked_by_v3_mechanics_count": _count(items, "blocked_by_v3_mechanics"),
            "frontend_inventory_count": len(frontend_inventory),
            "v2_infrastructure_ready": bool(release_report.get("readiness_decision", {}).get("v2_infrastructure_ready") is True),
            "production_planner_ready": False,
            "mechanical_remap_ready": False,
            "stable_calculable_count": 0,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "allowed_classifications": sorted(UX_CLASSIFICATIONS),
        "ux_items": items,
        "classification_counts": {
            classification: _count(items, classification)
            for classification in sorted(UX_CLASSIFICATIONS)
            if _count(items, classification)
        },
        "v2_5_implementation_sequence": [dict(step) for step in V2_5_SEQUENCE],
        "user_facing_concepts": [item for item in items if item["user_facing"]],
        "developer_only_concepts": [item for item in items if item["developer_only"]],
        "frontend_inventory": frontend_inventory,
        "frontend_gaps": _frontend_gaps(),
        "backend_report_data_available_for_ux": _backend_report_data(release_report),
        "debug_only_boundaries": [
            "raw API envelopes",
            "full blocked record samples",
            "full source path dumps",
            "developer provenance internals",
            "mechanical dry-run deltas before v3 baselines",
        ],
        "safety_confirmations": {
            "production_consumed": False,
            "production_planner_remap_performed": False,
            "planner_output_changed": False,
            "crafting_behavior_changed": False,
            "simulation_behavior_changed": False,
            "stat_aggregation_behavior_changed": False,
            "value_normalization_promoted": False,
            "skill_identity_bridge_added": False,
            "experimental_mode_enabled_by_default": False,
            "stable_calculable_count": 0,
            "v2_infrastructure_ready": bool(release_report.get("readiness_decision", {}).get("v2_infrastructure_ready") is True),
            "production_planner_ready": False,
            "mechanical_remap_ready": False,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "future_next_step": {
            "recommendation": "start with shared trust/support badges and provenance/warning panels",
            "do_not_start": [
                "v3 mechanical intelligence",
                "production planner remap",
                "value normalization promotion",
                "skill identity bridging",
            ],
        },
        "metadata": {
            "source": "v2_5_trust_ux_plan",
            "planning_only": True,
            "frontend_behavior_changed": False,
            "backend_behavior_changed": False,
            "production_consumed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    safety = report["safety_confirmations"]
    lines = [
        "# V2.5 Trust UX Plan",
        "",
        "This audit plans the v2.5 trust and UX layer.",
        "It does not implement UI behavior, planner remap, value normalization, or mechanical calculation changes.",
        "",
        "## Safety State",
        "",
        f"- V2 infrastructure ready: `{str(safety['v2_infrastructure_ready']).lower()}`",
        f"- Production planner ready: `{str(safety['production_planner_ready']).lower()}`",
        f"- Mechanical remap ready: `{str(safety['mechanical_remap_ready']).lower()}`",
        f"- Stable-calculable count: `{safety['stable_calculable_count']}`",
        f"- Value normalization: `{safety['value_normalization_status']}`",
        f"- Skill identity bridge: `{safety['skill_identity_bridge_status']}`",
        "",
        "## UX Item Summary",
        "",
        f"- UX items: `{summary['ux_item_count']}`",
        f"- Ready for v2.5: `{summary['ready_for_v2_5_count']}`",
        f"- Needs copy design: `{summary['needs_copy_design_count']}`",
        f"- Needs frontend component: `{summary['needs_frontend_component_count']}`",
        f"- Debug-only: `{summary['debug_only_count']}`",
        f"- Blocked by v3 mechanics: `{summary['blocked_by_v3_mechanics_count']}`",
        "",
        "## Proposed Sequence",
        "",
        "| Order | Step | Description |",
        "| ---: | --- | --- |",
    ]
    for step in report["v2_5_implementation_sequence"]:
        lines.append(f"| `{step['order']}` | `{step['id']}` | {step['description']} |")
    lines.extend(["", "## UX Items", "", "| Item | Classification | User-facing |", "| --- | --- | --- |"])
    for item in report["ux_items"]:
        lines.append(f"| `{item['id']}` | `{item['classification']}` | `{str(item['user_facing']).lower()}` |")
    lines.extend(["", "## Frontend Gaps", ""])
    lines.extend(f"- `{gap['id']}`: {gap['description']}" for gap in report["frontend_gaps"])
    lines.extend(["", "## Developer-Only Concepts", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["developer_only_concepts"])
    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No frontend behavior was changed.",
            "- No backend runtime behavior was changed.",
            "- No production planner route was added.",
            "- No stat or modifier calculation behavior was changed.",
            "- No value scale was promoted.",
            "- No unresolved skill identity reference was bridged.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _frontend_inventory(repo_root: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for item in FRONTEND_INVENTORY:
        row = dict(item)
        row["exists"] = (repo_root / item["path"]).exists()
        inventory.append(row)
    return inventory


def _frontend_gaps() -> list[dict[str, str]]:
    return [
        {
            "id": "shared_user_facing_badges_missing",
            "description": "Debug panels summarize support/provenance, but reusable user-facing trust badges are not yet implemented.",
        },
        {
            "id": "stats_modifiers_page_missing",
            "description": "Stat and modifier registries do not yet have a dedicated frontend debug page.",
        },
        {
            "id": "trusted_data_explanation_page_missing",
            "description": "There is no non-developer page explaining trusted data, limitations, and current calculation boundaries.",
        },
        {
            "id": "planner_status_panel_missing",
            "description": "Planner-adjacent views do not yet show v2 adapter status as non-calculating context.",
        },
        {
            "id": "support_matrix_missing",
            "description": "Users cannot yet scan a compact support matrix by domain and mechanic type.",
        },
    ]


def _backend_report_data(release_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "release_readiness_decision": release_report.get("readiness_decision", {}),
        "production_blockers": release_report.get("production_blockers", []),
        "platform_status_keys": sorted((release_report.get("platform_status") or {}).keys()),
        "trusted_data_coverage": release_report.get("trusted_data_coverage", {}),
        "validation_evidence": release_report.get("validation_evidence", {}),
    }


def _count(items: list[dict[str, Any]], classification: str) -> int:
    return sum(1 for item in items if item["classification"] == classification)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_5_trust_ux_plan.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_5_TRUST_UX_PLAN.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_5_trust_ux_plan(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
