"""Report v2 planner remap readiness without changing planner behavior."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ALLOWED_CLASSIFICATIONS = {
    "ready_for_adapter_later",
    "blocked_by_value_normalization",
    "blocked_by_identity_resolution",
    "blocked_by_unsupported_mechanics",
    "blocked_by_missing_tests",
    "blocked_by_schema_mismatch",
    "blocked_by_behavioral_risk",
    "manual_only_currently",
    "unknown_needs_review",
}

REPORT_FILENAME = "v2_planner_remap_readiness_report.json"
DOC_FILENAME = "V2_PLANNER_REMAP_READINESS.md"

PRODUCTION_SCAN_ROOTS = [
    ("backend/app/routes", "backend_route"),
    ("backend/app/services", "backend_service"),
    ("backend/app/engines", "backend_engine"),
    ("backend/app/stats", "backend_stats"),
    ("backend/app/domain", "backend_domain"),
    ("backend/app/game_data", "legacy_game_data"),
    ("backend/app/constants", "backend_constants"),
    ("frontend/src", "frontend"),
]

PLANNER_KEYWORDS = [
    "planner",
    "build",
    "craft",
    "simulate",
    "simulation",
    "stat",
    "affix",
    "item",
    "unique",
    "idol",
    "passive",
    "skill",
    "reference",
    "game_data",
    "constants",
]

ENTRYPOINT_HINTS = {
    "backend/app/routes/affixes.py": "legacy affix API route",
    "backend/app/routes/craft.py": "crafting API route",
    "backend/app/routes/passives.py": "passive API route",
    "backend/app/routes/ref.py": "production reference API route",
    "backend/app/routes/simulate.py": "simulation API route",
    "backend/app/routes/skills.py": "skill API route",
    "backend/app/routes/optimize.py": "optimizer API route",
    "backend/app/routes/analysis.py": "analysis API route",
    "backend/app/services/craft_service.py": "crafting service",
    "backend/app/services/passive_stat_resolver.py": "passive stat resolver",
    "backend/app/services/simulation_service.py": "simulation service",
    "backend/app/engines/stat_engine.py": "legacy stat aggregation engine",
    "backend/app/engines/stat_resolution_pipeline.py": "stat resolution pipeline",
    "backend/app/engines/craft_engine.py": "crafting math engine",
    "backend/app/engines/craft_simulator.py": "crafting simulator",
    "backend/app/engines/combat_simulator.py": "combat simulator",
    "backend/app/engines/combat_engine.py": "combat DPS engine",
    "backend/app/game_data/game_data_loader.py": "legacy game data loader",
    "frontend/src/services/buildApi.ts": "frontend build API client",
    "frontend/src/services/craftingApi.ts": "frontend crafting API client",
    "frontend/src/lib/simulation.ts": "frontend simulation helpers",
    "frontend/src/lib/crafting.ts": "frontend crafting helpers",
    "frontend/src/components/features/build/BuildPlannerPage.tsx": "frontend planner page",
    "frontend/src/components/features/build-workspace/UnifiedBuildPage.tsx": "frontend build workspace",
}


def build_v2_planner_remap_readiness_report(*, root: str | Path | None = None) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    generated_dir = repo_root / "docs" / "generated"

    planner_adapter = _load_json(generated_dir / "v2_planner_adapter_report.json")
    validation_ci = _load_json(generated_dir / "v2_validation_ci_report.json")
    modifier_validation = _load_json(generated_dir / "v2_modifier_validation_report.json")
    value_policy = _load_json(generated_dir / "v2_value_normalization_policy_report.json")
    skill_identity = _load_json(generated_dir / "v2_skill_identity_alignment_report.json")

    production_inventory = _inventory_production_dependencies(repo_root)
    dependencies = _dependency_classifications(planner_adapter, skill_identity)
    remap_sequence = _future_remap_sequence()
    safety = _safety_confirmations(planner_adapter, validation_ci, modifier_validation, value_policy, skill_identity)
    hardcoded_sources = _hardcoded_and_legacy_sources(repo_root)

    classification_counts = Counter(dep["classification"] for dep in dependencies)

    return {
        "summary": {
            "generated_at": datetime.now(UTC).isoformat(),
            "production_planner_entrypoint_count": len(production_inventory["backend_entrypoints"]),
            "frontend_planner_entrypoint_count": len(production_inventory["frontend_entrypoints"]),
            "legacy_or_hardcoded_source_count": len(hardcoded_sources),
            "dependency_category_count": len(dependencies),
            "remap_phase_count": len(remap_sequence),
            "production_consumed": safety["production_consumed"],
            "stable_calculable_count": safety["stable_calculable_count"],
            "eligible_planner_calculable_count": safety["eligible_planner_calculable_count"],
            "blocked_modifier_count": safety["blocked_modifier_count"],
            "value_normalization_status": safety["value_normalization_status"],
            "skill_identity_bridge_status": safety["skill_identity_bridge_status"],
            "status": "ready_for_review",
        },
        "safety_confirmations": safety,
        "production_inventory": production_inventory,
        "hardcoded_and_legacy_data_sources": hardcoded_sources,
        "dependency_classifications": dependencies,
        "dependency_classification_counts": dict(sorted(classification_counts.items())),
        "future_remap_sequence": remap_sequence,
        "tests_required_before_remap": _tests_required_before_remap(),
        "gaps_between_current_planner_and_v2": _planner_shape_gaps(),
        "metadata": {
            "phase": "16",
            "source": "v2_planner_remap_readiness",
            "audit_only": True,
            "planner_remap_performed": False,
            "production_routes_added": False,
            "value_normalization_promoted": False,
            "skill_identity_bridge_added": False,
        },
    }


def write_report(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(report: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V2 Planner Remap Readiness",
        "",
        "Phase 16 audits planner-facing dependencies and defines a safe future remap order.",
        "It does not change production planner, crafting, simulation, or stat behavior.",
        "",
        "## Safety State",
        "",
        f"- Production consumed: `{str(report['safety_confirmations']['production_consumed']).lower()}`",
        f"- Planner remap performed: `{str(report['safety_confirmations']['planner_remap_performed']).lower()}`",
        f"- Stable-calculable count: `{report['safety_confirmations']['stable_calculable_count']}`",
        f"- Eligible planner-calculable count: `{report['safety_confirmations']['eligible_planner_calculable_count']}`",
        f"- Blocked modifier records: `{report['safety_confirmations']['blocked_modifier_count']}`",
        f"- Value normalization: `{report['safety_confirmations']['value_normalization_status']}`",
        f"- Skill identity bridge: `{report['safety_confirmations']['skill_identity_bridge_status']}`",
        "",
        "## Production Entrypoints",
        "",
        f"- Backend planner/runtime entrypoints found: `{len(report['production_inventory']['backend_entrypoints'])}`",
        f"- Frontend planner/runtime entrypoints found: `{len(report['production_inventory']['frontend_entrypoints'])}`",
        f"- Legacy or hardcoded data sources found: `{len(report['hardcoded_and_legacy_data_sources'])}`",
        "",
        "Key backend entrypoints include production reference routes, craft routes, simulate routes,",
        "stat aggregation engines, crafting engines, combat simulation engines, and legacy game-data loaders.",
        "",
        "## Dependency Classifications",
        "",
    ]
    for item in report["dependency_classifications"]:
        blockers = ", ".join(item["blockers"])
        lines.append(f"- `{item['category']}`: `{item['classification']}` ({blockers})")

    lines.extend(
        [
            "",
            "## Future Remap Sequence",
            "",
        ]
    )
    for phase in report["future_remap_sequence"]:
        lines.append(f"{phase['order']}. **{phase['name']}** - {phase['goal']}")
        lines.append(f"   - Required tests: {', '.join(phase['required_tests'])}")

    lines.extend(
        [
            "",
            "## Planner Shape Gaps",
            "",
        ]
    )
    for gap in report["gaps_between_current_planner_and_v2"]:
        lines.append(f"- `{gap['id']}`: {gap['description']} Impact: {gap['impact']}")

    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
            "- Value scale is still audit-only; source-unit and unknown-scale values cannot feed planner math.",
            "- Stable-calculable modifier count is still zero.",
            "- Remaining skill identity gaps stay unbridged.",
            "- Unsupported, text-only, and scripted mechanics remain debug/display-only.",
            "- Current production engines use legacy schemas and hardcoded/manual mappings that need golden baselines before replacement.",
            "",
            "## Non-Goals Confirmed",
            "",
            "- No production planner consumption was added.",
            "- No planner output changed.",
            "- No crafting, simulation, or stat engine behavior changed.",
            "- No value scale was promoted.",
            "- No skill identity bridge was added.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _inventory_production_dependencies(repo_root: Path) -> dict[str, Any]:
    scanned_files: list[dict[str, Any]] = []
    backend_entrypoints: list[dict[str, str]] = []
    frontend_entrypoints: list[dict[str, str]] = []

    for relative_root, kind in PRODUCTION_SCAN_ROOTS:
        root = repo_root / relative_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in {".py", ".ts", ".tsx", ".json"}:
                continue
            relative = path.relative_to(repo_root).as_posix()
            text = _read_text(path)
            lowered = text.lower()
            matched = sorted({keyword for keyword in PLANNER_KEYWORDS if keyword in lowered or keyword in relative.lower()})
            if not matched and relative not in ENTRYPOINT_HINTS:
                continue
            record = {
                "path": relative,
                "kind": kind,
                "matched_keywords": matched[:12],
                "entrypoint_hint": ENTRYPOINT_HINTS.get(relative, ""),
            }
            scanned_files.append(record)
            if relative in ENTRYPOINT_HINTS:
                if relative.startswith("frontend/"):
                    frontend_entrypoints.append({"path": relative, "role": ENTRYPOINT_HINTS[relative]})
                else:
                    backend_entrypoints.append({"path": relative, "role": ENTRYPOINT_HINTS[relative]})

    return {
        "backend_entrypoints": backend_entrypoints,
        "frontend_entrypoints": frontend_entrypoints,
        "scanned_dependency_file_count": len(scanned_files),
        "scanned_dependency_files": scanned_files[:200],
        "scan_note": "Static inventory only; future remap phases need behavioral golden tests before production switching.",
    }


def _hardcoded_and_legacy_sources(repo_root: Path) -> list[dict[str, str]]:
    candidates = [
        ("backend/app/routes/ref.py", "CLASS_META and slot aliases are hardcoded production reference metadata."),
        ("backend/app/game_data/constants.json", "Legacy runtime constants consumed by stat and combat engines."),
        ("backend/app/game_data/classes.json", "Legacy class metadata source."),
        ("backend/app/game_data/skills.json", "Legacy skill metadata source."),
        ("backend/app/game_data/game_data_loader.py", "Legacy JSON and DB loader for affixes, blessings, and reference data."),
        ("backend/app/constants/crafting.py", "Manual crafting constants."),
        ("backend/app/engines/stat_engine.py", "Manual BuildStats field schema and stat aggregation mappings."),
        ("backend/app/engines/stat_resolution_pipeline.py", "Manual layer ordering and blessing stat conversion."),
        ("frontend/src/constants/statLabels.ts", "Frontend stat label map."),
        ("frontend/src/constants/statBenchmarks.ts", "Frontend stat benchmark constants."),
        ("frontend/src/lib/simulation.ts", "Frontend simulation/stat mirror logic."),
        ("frontend/src/lib/crafting.ts", "Frontend crafting helper logic."),
    ]
    return [
        {"path": path, "finding": finding}
        for path, finding in candidates
        if (repo_root / path).exists()
    ]


def _dependency_classifications(planner_adapter: dict[str, Any], skill_identity: dict[str, Any]) -> list[dict[str, Any]]:
    blocked_reason_counts = planner_adapter.get("blocked_reason_counts", {}) if isinstance(planner_adapter, dict) else {}
    unresolved_skill_refs = _nested_int(skill_identity, ["summary", "unresolved_reference_count"])
    ambiguous_skill_refs = _nested_int(skill_identity, ["summary", "ambiguous_match_count"])

    return [
        _dependency("item/base display metadata", "ready_for_adapter_later", ["needs non-calculating API adapter tests"]),
        _dependency("affix display and provenance", "ready_for_adapter_later", ["must stay display-only until value policy is proven"]),
        _dependency("affix modifier math", "blocked_by_value_normalization", ["source_units_value_scale", "unstable_support_status"]),
        _dependency("item implicit modifier math", "blocked_by_value_normalization", ["source_units_value_scale", "unstable_support_status"]),
        _dependency("unique and set mechanics", "blocked_by_unsupported_mechanics", ["unsupported/text-only report remains intentionally visible"]),
        _dependency("idol base and idol affix math", "blocked_by_value_normalization", ["source_units_value_scale", "IDOL_ALTAR warnings remain display-only"]),
        _dependency("class/mastery metadata", "ready_for_adapter_later", ["metadata can be inspected; planner skill ownership remains partially unresolved"]),
        _dependency(
            "skill ownership",
            "blocked_by_identity_resolution",
            [f"unresolved_refs={unresolved_skill_refs}", f"ambiguous_refs={ambiguous_skill_refs}"],
        ),
        _dependency("passive node behavior", "blocked_by_unsupported_mechanics", ["scripted and unsupported passive records remain non-calculable"]),
        _dependency("skill and skill tree behavior", "blocked_by_unsupported_mechanics", ["scripted and unsupported skill records remain non-calculable"]),
        _dependency(
            "stat/modifier adapter math",
            "blocked_by_value_normalization",
            [
                f"unknown_value_scale={blocked_reason_counts.get('unknown_value_scale', 0)}",
                f"source_units_value_scale={blocked_reason_counts.get('source_units_value_scale', 0)}",
            ],
        ),
        _dependency("crafting engine", "blocked_by_behavioral_risk", ["production behavior depends on legacy craft engine and FP constants"]),
        _dependency("simulation/combat engine", "blocked_by_behavioral_risk", ["production behavior depends on legacy stat fields and combat formulas"]),
        _dependency("production reference routes", "manual_only_currently", ["routes expose legacy DB/static data and must not switch without compatibility tests"]),
        _dependency("frontend planner API clients", "blocked_by_missing_tests", ["needs adapter dry-run and UI compatibility tests before remap"]),
    ]


def _dependency(category: str, classification: str, blockers: list[str]) -> dict[str, Any]:
    if classification not in ALLOWED_CLASSIFICATIONS:
        raise ValueError(f"Unknown dependency classification: {classification}")
    return {"category": category, "classification": classification, "blockers": blockers}


def _future_remap_sequence() -> list[dict[str, Any]]:
    return [
        {
            "order": 1,
            "name": "Read-only planner diagnostics using v2 adapter",
            "goal": "Expose v2 adapter explanations beside current planner output without changing calculations.",
            "required_tests": ["production non-consumption", "adapter read-only", "no output delta"],
        },
        {
            "order": 2,
            "name": "Non-calculating metadata remap",
            "goal": "Use v2 IDs, provenance, support status, and debug labels only.",
            "required_tests": ["API compatibility", "frontend rendering", "unsupported visibility"],
        },
        {
            "order": 3,
            "name": "Item/base display metadata remap",
            "goal": "Remap item base display and restriction metadata without stat math.",
            "required_tests": ["item compatibility fixtures", "legacy route comparison", "no stat output delta"],
        },
        {
            "order": 4,
            "name": "Affix display and provenance remap",
            "goal": "Show v2 affix identity/provenance while legacy math remains authoritative.",
            "required_tests": ["affix list comparison", "crafting UI compatibility", "blocked reason visibility"],
        },
        {
            "order": 5,
            "name": "Passive/skill identity-only remap where safe",
            "goal": "Use resolved identities for inspection only and keep unresolved skill references blocked.",
            "required_tests": ["identity audit", "unresolved bridge guard", "tree layout comparison"],
        },
        {
            "order": 6,
            "name": "Stat/modifier adapter dry-run comparison",
            "goal": "Compare v2 adapter rows against legacy stat outputs without consumption.",
            "required_tests": ["golden build fixtures", "blocked reason snapshots", "value-scale guard"],
        },
        {
            "order": 7,
            "name": "Golden baseline test creation",
            "goal": "Create stable expected outputs for representative builds and crafting flows.",
            "required_tests": ["golden planner outputs", "crafting baselines", "simulation baselines"],
        },
        {
            "order": 8,
            "name": "Limited opt-in experimental planner adapter mode",
            "goal": "Add explicitly opt-in experimental comparison mode after stable gates pass.",
            "required_tests": ["feature flag guard", "default-off production guard", "route contract tests"],
        },
        {
            "order": 9,
            "name": "Production remap after stable-calculable gates pass",
            "goal": "Switch production only after value scale, identity, support, and behavior gates are proven.",
            "required_tests": ["full planner regression", "crafting regression", "simulation regression", "rollback checks"],
        },
    ]


def _tests_required_before_remap() -> list[dict[str, str]]:
    return [
        {"area": "planner output", "requirement": "golden baseline tests for representative builds"},
        {"area": "crafting", "requirement": "legacy versus v2 dry-run comparison fixtures"},
        {"area": "simulation", "requirement": "combat/stat output parity tests before any consumption"},
        {"area": "value scale", "requirement": "source contracts or golden baselines for every promoted family"},
        {"area": "skill identity", "requirement": "guards that unresolved/ambiguous refs remain blocked"},
        {"area": "unsupported mechanics", "requirement": "tests that text-only/scripted behavior never enters stable math"},
        {"area": "API compatibility", "requirement": "frontend debug and route envelope compatibility tests"},
    ]


def _planner_shape_gaps() -> list[dict[str, str]]:
    return [
        {
            "id": "legacy_stat_fields_vs_canonical_stats",
            "description": "Production BuildStats uses fixed Python/TypeScript fields while v2 has canonical stat IDs.",
            "impact": "Needs an audited stat field adapter before planner math can consume v2 modifiers.",
        },
        {
            "id": "source_units_value_scale",
            "description": "Many v2 modifier rows preserve raw source units.",
            "impact": "Planner-normalized values must not be inferred without scale evidence.",
        },
        {
            "id": "unsupported_scripted_mechanics",
            "description": "Unique, passive, and skill records include scripted/text-only mechanics.",
            "impact": "These must remain display/debug-only until explicitly modeled.",
        },
        {
            "id": "skill_identity_gap",
            "description": "A small number of class/mastery skill references remain unresolved or ambiguous.",
            "impact": "Skill ownership-sensitive calculations cannot depend on those links.",
        },
        {
            "id": "legacy_routes_and_db_models",
            "description": "Production reference routes still use legacy DB/static sources.",
            "impact": "Route-level remap requires compatibility wrappers and regression fixtures.",
        },
    ]


def _safety_confirmations(
    planner_adapter: dict[str, Any],
    validation_ci: dict[str, Any],
    modifier_validation: dict[str, Any],
    value_policy: dict[str, Any],
    skill_identity: dict[str, Any],
) -> dict[str, Any]:
    adapter_summary = planner_adapter.get("summary", {}) if isinstance(planner_adapter, dict) else {}
    validation_safety = validation_ci.get("safety", {}) if isinstance(validation_ci, dict) else {}
    value_summary = value_policy.get("summary", {}) if isinstance(value_policy, dict) else {}
    skill_summary = skill_identity.get("summary", {}) if isinstance(skill_identity, dict) else {}
    stable_count = _nested_int(modifier_validation, ["summary", "stable_calculable_count"])

    return {
        "production_consumed": False,
        "planner_remap_performed": False,
        "planner_output_changed": False,
        "crafting_behavior_changed": False,
        "simulation_behavior_changed": False,
        "stat_aggregation_behavior_changed": False,
        "value_normalization_promoted": False,
        "skill_identity_bridge_added": False,
        "stable_calculable_count": stable_count,
        "eligible_planner_calculable_count": int(adapter_summary.get("eligible_planner_calculable_count", 0) or 0),
        "blocked_modifier_count": int(adapter_summary.get("blocked_modifier_count", 0) or 0),
        "value_normalization_status": validation_safety.get("value_normalization_policy_status")
        or value_summary.get("policy_status")
        or "audit_only",
        "safe_normalization_family_count": int(value_summary.get("safe_normalization_family_count", 0) or 0),
        "skill_identity_bridge_status": validation_safety.get("skill_identity_bridge_status") or "unbridged",
        "unresolved_skill_reference_count": skill_summary.get("unresolved_reference_count")
        or skill_summary.get("unresolved_references")
        or skill_summary.get("unresolved_count"),
        "ambiguous_skill_reference_count": skill_summary.get("ambiguous_match_count")
        or skill_summary.get("ambiguous_matches")
        or skill_summary.get("ambiguous_count"),
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _nested_int(payload: dict[str, Any], path: list[str]) -> int:
    value: Any = payload
    for part in path:
        if not isinstance(value, dict):
            return 0
        value = value.get(part)
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=f"docs/generated/{REPORT_FILENAME}")
    parser.add_argument("--markdown-output", default=f"docs/migration/{DOC_FILENAME}")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    report = build_v2_planner_remap_readiness_report(root=repo_root)
    write_report(report, repo_root / args.output)
    write_markdown(report, repo_root / args.markdown_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
