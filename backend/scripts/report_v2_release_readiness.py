"""Generate the v2 release readiness and production blocker audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REQUIRED_PREVIOUS_REPORTS = (
    "v2_backend_repository_report.json",
    "v2_api_contract_report.json",
    "v2_validation_ci_report.json",
    "v2_planner_adapter_report.json",
    "v2_planner_remap_readiness_report.json",
    "v2_planner_adapter_diagnostics_report.json",
    "v2_planner_metadata_remap_report.json",
    "v2_item_base_display_metadata_report.json",
    "v2_affix_display_provenance_report.json",
    "v2_passive_skill_identity_remap_report.json",
    "v2_stat_modifier_dry_run_report.json",
    "v2_golden_baseline_plan.json",
    "v2_experimental_planner_adapter_mode_report.json",
)

WORK_CLASSIFICATIONS = frozenset(
    {
        "v2_release_blocker",
        "v2_5_trust_ux_followup",
        "v3_mechanical_intelligence_blocker",
        "future_patch_resilience_followup",
        "known_intentional_limitation",
        "unknown_needs_review",
    }
)


def build_v2_release_readiness_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    generated_dir = repo_root / "docs" / "generated"
    reports = _load_reports(generated_dir)

    backend = reports["v2_backend_repository_report.json"]
    api = reports["v2_api_contract_report.json"]
    validation = reports["v2_validation_ci_report.json"]
    adapter = reports["v2_planner_adapter_report.json"]
    diagnostics = reports["v2_planner_adapter_diagnostics_report.json"]
    metadata = reports["v2_planner_metadata_remap_report.json"]
    item_metadata = reports["v2_item_base_display_metadata_report.json"]
    affix_metadata = reports["v2_affix_display_provenance_report.json"]
    passive_skill = reports["v2_passive_skill_identity_remap_report.json"]
    dry_run = reports["v2_stat_modifier_dry_run_report.json"]
    baselines = reports["v2_golden_baseline_plan.json"]
    experimental_mode = reports["v2_experimental_planner_adapter_mode_report.json"]

    evidence = _readiness_evidence(
        backend=backend,
        api=api,
        validation=validation,
        adapter=adapter,
        diagnostics=diagnostics,
        metadata=metadata,
        item_metadata=item_metadata,
        affix_metadata=affix_metadata,
        passive_skill=passive_skill,
        dry_run=dry_run,
        baselines=baselines,
        experimental_mode=experimental_mode,
    )
    readiness = {
        "v2_infrastructure_ready": evidence["all_required_reports_present"]
        and evidence["validation_status"] == "pass"
        and evidence["repository_loaded_domain_count"] == evidence["repository_domain_count"]
        and evidence["missing_artifact_count"] == 0
        and evidence["invalid_repository_count"] == 0
        and evidence["api_route_count"] >= 38
        and evidence["experimental_mode_default_enabled"] is False
        and evidence["production_consumed"] is False,
        "production_planner_ready": False,
        "mechanical_remap_ready": False,
        "recommended_next_track": "v2_5_trust_ux_layer",
    }

    production_blockers = _production_blockers(adapter=adapter, dry_run=dry_run, passive_skill=passive_skill, baselines=baselines, experimental_mode=experimental_mode)
    work_items = _classified_work_items()
    classification_counts = _classification_counts(work_items)
    v2_5_followups = [item for item in work_items if item["classification"] == "v2_5_trust_ux_followup"]
    v3_blockers = [item for item in work_items if item["classification"] == "v3_mechanical_intelligence_blocker"]

    return {
        "schema_version": "v2.release_readiness.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "readiness_decision": readiness,
        "readiness_evidence": evidence,
        "infrastructure_completeness": {
            "trusted_data_bundles": "complete_for_v2_infrastructure",
            "repository_layer": "complete",
            "api_contracts": "complete",
            "frontend_debug_consumption": "complete_with_known_full_suite_caveat",
            "validation_ci": validation.get("summary", {}).get("status", "unknown"),
            "planner_adapter_boundary": "complete_read_only",
            "metadata_display_remaps": "complete_non_calculating",
            "dry_run_comparison": "complete_non_calculating",
            "golden_baseline_scaffold": "complete_non_mechanical",
            "experimental_mode": "complete_disabled_by_default",
        },
        "trusted_data_coverage": {
            "repository_domains": backend.get("summary", {}).get("repository_domain_count"),
            "loaded_domains": backend.get("summary", {}).get("loaded_repository_count"),
            "experimental_routes": backend.get("summary", {}).get("experimental_route_count"),
            "valid_json_reports": validation.get("summary", {}).get("valid_json_report_count"),
            "modifier_records_inspected": dry_run.get("summary", {}).get("modifier_row_count"),
            "stat_registry_entries": dry_run.get("summary", {}).get("stat_registry_count"),
        },
        "platform_status": {
            "adapter_boundary": adapter.get("summary", {}),
            "diagnostics": diagnostics.get("summary", {}),
            "planner_metadata": metadata.get("summary", {}),
            "item_base_display_metadata": item_metadata.get("summary", {}),
            "affix_display_provenance": affix_metadata.get("summary", {}),
            "passive_skill_identity": passive_skill.get("summary", {}),
            "stat_modifier_dry_run": dry_run.get("summary", {}),
            "golden_baselines": baselines.get("summary", {}),
            "experimental_mode": experimental_mode.get("summary", {}),
        },
        "production_blockers": production_blockers,
        "classified_remaining_work": work_items,
        "classification_counts": classification_counts,
        "v2_5_trust_ux_followups": v2_5_followups,
        "v3_mechanical_intelligence_blockers": v3_blockers,
        "required_previous_reports": _required_report_status(generated_dir),
        "validation_evidence": {
            "backend_validation_status": validation.get("summary", {}).get("status"),
            "production_non_consumption_guard": validation.get("backend_checks", {}).get("production_non_consumption_guard"),
            "focused_frontend_caveat": validation.get("known_caveats", []),
            "valid_json_report_count": validation.get("summary", {}).get("valid_json_report_count"),
            "missing_generated_report_count": validation.get("summary", {}).get("missing_generated_report_count"),
            "invalid_json_report_count": validation.get("summary", {}).get("invalid_json_report_count"),
        },
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
            "planner_calculable_count": 0,
            "stable_calculable_count": 0,
            "value_normalization_status": "audit_only",
            "skill_identity_bridge_status": "unbridged",
        },
        "future_next_step": {
            "recommended_track": "v2_5_trust_ux_layer",
            "v2_5_goal": "make trust, support, provenance, warnings, and limitations easier to understand without changing planner math",
            "v3_goal": "mechanical intelligence after value, operation, identity, and golden baseline blockers are resolved",
        },
        "metadata": {
            "source": "v2_release_readiness",
            "read_only": True,
            "audit_only": True,
            "production_consumed": False,
            "planner_remap_performed": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    decision = report["readiness_decision"]
    safety = report["safety_confirmations"]
    evidence = report["readiness_evidence"]
    lines = [
        "# V2 Release Readiness",
        "",
        "Phase 25 audits whether the v2 trusted-data platform is ready to ship as infrastructure.",
        "It does not enable production planner consumption or mechanical remap behavior.",
        "",
        "## Readiness Decision",
        "",
        f"- V2 infrastructure ready: `{str(decision['v2_infrastructure_ready']).lower()}`",
        f"- Production planner ready: `{str(decision['production_planner_ready']).lower()}`",
        f"- Mechanical remap ready: `{str(decision['mechanical_remap_ready']).lower()}`",
        f"- Recommended next track: `{decision['recommended_next_track']}`",
        "",
        "## Evidence",
        "",
        f"- Required previous reports present: `{str(evidence['all_required_reports_present']).lower()}`",
        f"- Validation status: `{evidence['validation_status']}`",
        f"- Repository domains loaded: `{evidence['repository_loaded_domain_count']} / {evidence['repository_domain_count']}`",
        f"- Missing artifacts: `{evidence['missing_artifact_count']}`",
        f"- Invalid repositories: `{evidence['invalid_repository_count']}`",
        f"- Experimental routes documented: `{evidence['api_route_count']}`",
        f"- Experimental mode default enabled: `{str(evidence['experimental_mode_default_enabled']).lower()}`",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(safety['production_consumed']).lower()}`",
        f"- Production planner remap performed: `{str(safety['production_planner_remap_performed']).lower()}`",
        f"- Planner-calculable count: `{safety['planner_calculable_count']}`",
        f"- Stable-calculable count: `{safety['stable_calculable_count']}`",
        f"- Value normalization: `{safety['value_normalization_status']}`",
        f"- Skill identity bridge: `{safety['skill_identity_bridge_status']}`",
        "",
        "## Production Blockers",
        "",
        "| Blocker | Classification | Status |",
        "| --- | --- | --- |",
    ]
    for blocker in report["production_blockers"]:
        lines.append(f"| `{blocker['id']}` | `{blocker['classification']}` | `{blocker['status']}` |")
    lines.extend(["", "## V2.5 Trust & UX Followups", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["v2_5_trust_ux_followups"])
    lines.extend(["", "## V3 Mechanical Intelligence Blockers", ""])
    lines.extend(f"- `{item['id']}`: {item['description']}" for item in report["v3_mechanical_intelligence_blockers"])
    lines.extend(
        [
            "",
            "## Runtime Behavior",
            "",
            "- No production planner route was added.",
            "- No stat or modifier calculation behavior was changed.",
            "- No crafting, simulation, or stat aggregation behavior was changed.",
            "- No value scale was promoted.",
            "- No unresolved skill identity reference was bridged.",
            "- The experimental planner adapter mode remains disabled by default.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_reports(generated_dir: Path) -> dict[str, dict[str, Any]]:
    return {name: _read_json(generated_dir / name) for name in REQUIRED_PREVIOUS_REPORTS}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _required_report_status(generated_dir: Path) -> list[dict[str, Any]]:
    return [
        {
            "report": name,
            "path": str(generated_dir / name),
            "exists": (generated_dir / name).exists(),
        }
        for name in REQUIRED_PREVIOUS_REPORTS
    ]


def _readiness_evidence(**reports: dict[str, Any]) -> dict[str, Any]:
    backend = reports["backend"]
    validation = reports["validation"]
    experimental_mode = reports["experimental_mode"]
    backend_summary = backend.get("summary", {})
    validation_summary = validation.get("summary", {})
    mode_disabled = experimental_mode.get("mode_disabled_behavior", {})
    return {
        "all_required_reports_present": all(bool(report) for report in reports.values()),
        "validation_status": validation_summary.get("status"),
        "repository_domain_count": int(backend_summary.get("repository_domain_count") or 0),
        "repository_loaded_domain_count": int(backend_summary.get("loaded_repository_count") or 0),
        "missing_artifact_count": int(backend_summary.get("missing_artifact_count") or 0),
        "invalid_repository_count": int(backend_summary.get("invalid_repository_count") or 0),
        "missing_method_count": int(backend_summary.get("missing_method_count") or 0),
        "api_route_count": int(backend_summary.get("experimental_route_count") or validation_summary.get("api_route_count") or 0),
        "valid_json_report_count": int(validation_summary.get("valid_json_report_count") or 0),
        "missing_generated_report_count": int(validation_summary.get("missing_generated_report_count") or 0),
        "invalid_json_report_count": int(validation_summary.get("invalid_json_report_count") or 0),
        "experimental_mode_default_enabled": bool(mode_disabled.get("default_enabled") is True),
        "production_consumed": bool(validation_summary.get("production_consumed") is True),
    }


def _production_blockers(
    *,
    adapter: dict[str, Any],
    dry_run: dict[str, Any],
    passive_skill: dict[str, Any],
    baselines: dict[str, Any],
    experimental_mode: dict[str, Any],
) -> list[dict[str, Any]]:
    adapter_summary = adapter.get("summary", {})
    dry_summary = dry_run.get("summary", {})
    identity_summary = passive_skill.get("skill_identity_audit_summary", {})
    baseline_summary = baselines.get("summary", {})
    mode_disabled = experimental_mode.get("mode_disabled_behavior", {})
    return [
        _blocker("stable_calculable_zero", "Stable-calculable count is 0.", adapter_summary.get("stable_calculable_count"), "v3_mechanical_intelligence_blocker"),
        _blocker("value_normalization_audit_only", "Value normalization remains audit-only.", dry_summary.get("value_normalization_status"), "v3_mechanical_intelligence_blocker"),
        _blocker("source_units_unresolved", "Source-unit value scales remain unresolved.", dry_summary.get("source_unit_value_scale_count"), "v3_mechanical_intelligence_blocker"),
        _blocker("unknown_value_scales_unresolved", "Unknown value scales remain unresolved.", dry_summary.get("unknown_value_scale_count"), "v3_mechanical_intelligence_blocker"),
        _blocker("unknown_operations_unresolved", "Unknown operations remain unresolved.", dry_run.get("operation_distribution", {}).get("unknown"), "v3_mechanical_intelligence_blocker"),
        _blocker("unresolved_stat_identities_blocked", "Unresolved stat identities remain blocked.", dry_run.get("stat_identity_findings", {}).get("unknown"), "v3_mechanical_intelligence_blocker"),
        _blocker("skill_identity_gaps_unbridged", "Unresolved and ambiguous skill identities remain unbridged.", identity_summary, "known_intentional_limitation"),
        _blocker("unsupported_scripted_text_only_excluded", "Unsupported, scripted, and text-only mechanics remain excluded.", dry_run.get("unsupported_scripted_text_only_counts", {}), "known_intentional_limitation"),
        _blocker("mechanical_baselines_missing", "Golden mechanical baselines are not implemented yet.", baseline_summary.get("blocked_fixture_count"), "v3_mechanical_intelligence_blocker"),
        _blocker("experimental_mode_not_production_mode", "Experimental adapter mode is disabled by default and is not production mode.", mode_disabled.get("default_enabled"), "known_intentional_limitation"),
    ]


def _blocker(blocker_id: str, description: str, evidence: Any, classification: str) -> dict[str, Any]:
    return {
        "id": blocker_id,
        "description": description,
        "classification": classification,
        "status": "blocked",
        "evidence": evidence,
    }


def _classified_work_items() -> list[dict[str, str]]:
    return [
        {
            "id": "trust_badges",
            "description": "Improve user-facing support, trust, and provenance badges.",
            "classification": "v2_5_trust_ux_followup",
        },
        {
            "id": "unsupported_messaging",
            "description": "Make unsupported and text-only mechanic messaging clearer in debug and planner-adjacent views.",
            "classification": "v2_5_trust_ux_followup",
        },
        {
            "id": "stats_modifier_debug_pages",
            "description": "Add dedicated frontend pages for stat and modifier registry exploration.",
            "classification": "v2_5_trust_ux_followup",
        },
        {
            "id": "route_report_navigation",
            "description": "Improve navigation across trusted-data reports and experimental debug routes.",
            "classification": "v2_5_trust_ux_followup",
        },
        {
            "id": "value_normalization_contracts",
            "description": "Define source-unit to planner-normalized value contracts with proof.",
            "classification": "v3_mechanical_intelligence_blocker",
        },
        {
            "id": "operation_semantics",
            "description": "Resolve unknown operation semantics before mechanical stat math.",
            "classification": "v3_mechanical_intelligence_blocker",
        },
        {
            "id": "stat_identity_resolution",
            "description": "Resolve unknown stat identities before stable stat aggregation.",
            "classification": "v3_mechanical_intelligence_blocker",
        },
        {
            "id": "skill_identity_bridge_policy",
            "description": "Keep remaining skill identity gaps blocked unless future source data proves them.",
            "classification": "v3_mechanical_intelligence_blocker",
        },
        {
            "id": "golden_mechanical_baselines",
            "description": "Lock representative current planner output before any mechanical remap.",
            "classification": "v3_mechanical_intelligence_blocker",
        },
        {
            "id": "patch_schema_drift_watch",
            "description": "Keep report validation resilient to future source export schema changes.",
            "classification": "future_patch_resilience_followup",
        },
        {
            "id": "stable_count_zero",
            "description": "Stable-calculable count remains intentionally zero for v2 infrastructure release.",
            "classification": "known_intentional_limitation",
        },
    ]


def _classification_counts(work_items: list[dict[str, str]]) -> dict[str, int]:
    return {
        classification: sum(1 for item in work_items if item["classification"] == classification)
        for classification in sorted(WORK_CLASSIFICATIONS)
        if any(item["classification"] == classification for item in work_items)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="docs/generated/v2_release_readiness_report.json")
    parser.add_argument("--markdown-output", default="docs/migration/V2_RELEASE_READINESS.md")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_release_readiness_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    print(json.dumps(report["readiness_decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
