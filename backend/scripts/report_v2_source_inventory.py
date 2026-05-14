"""Generate the EpochForge v2 source inventory report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "v2_source_inventory.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_SOURCE_INVENTORY.md"

TEXT_EXTENSIONS = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".ps1",
    ".ts",
    ".tsx",
    ".txt",
    ".yml",
    ".yaml",
}
SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "le-parser.worktrees",
}

CATEGORY_TERMS = {
    "affixes": ("affix",),
    "items": ("item", "gear", "equipment"),
    "item_bases": ("base_type", "base-type", "baseitem", "base_item", "bases"),
    "implicits": ("implicit",),
    "idols": ("idol",),
    "uniques": ("unique",),
    "sets": ("set_", "sets", "set item"),
    "passive_trees": ("passive", "char-tree", "weaver"),
    "skill_trees": ("skill-tree", "skill_tree"),
    "skills": ("skill",),
    "classes_masteries": ("class", "classes", "mastery", "masteries"),
    "stats_modifiers": ("stat", "modifier", "damage", "resistance", "ward", "health", "mana"),
    "planner_constants": ("planner", "constant", "craft", "simulation", "optimizer", "bis"),
    "frontend_mappings": ("frontend", "src/data", "src/constants", "src/logic"),
    "backend_mappings": ("backend", "app/constants", "src/constants", "mappers", "registries"),
    "generated_files": ("docs/generated",),
    "static_json_files": (".json",),
    "fixtures": ("fixture", "fixtures"),
    "fallback_data": ("fallback", "sample", "sentinel"),
    "debug_demo_data": ("debug", "demo", "mock", "harness"),
    "tests_with_runtime_assumptions": ("test_", "__tests__", "tests"),
}

RUNTIME_CATEGORIES = {
    "affixes",
    "items",
    "item_bases",
    "implicits",
    "idols",
    "uniques",
    "sets",
    "passive_trees",
    "skill_trees",
    "skills",
    "classes_masteries",
    "stats_modifiers",
    "planner_constants",
    "frontend_mappings",
    "backend_mappings",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the v2 trusted data source inventory."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def discover_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if is_inventory_candidate(relative):
            paths.append(path)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def is_inventory_candidate(relative_path: Path) -> bool:
    rel = relative_path.as_posix().lower()
    name = relative_path.name.lower()
    if rel.startswith(("docs/generated/", "docs/migration/")):
        return True
    if rel.startswith(("data/", "backend/app/game_data/")):
        return True
    if rel.startswith(("backend/tests/", "frontend/src/__tests__/")):
        return True
    if rel.startswith(("frontend/src/data/", "frontend/src/constants/", "frontend/src/logic/")):
        return True
    if rel.startswith(("backend/app/constants/", "backend/src/constants/")):
        return True
    if rel.startswith(("backend/data/", "backend/integration/mapping/")):
        return True
    if rel.startswith("backend/scripts/") and (
        name.startswith(("generate_", "report_", "validate_", "compare_", "dry_run_"))
        or "data" in name
    ):
        return True
    terms = (
        "affix",
        "item",
        "passive",
        "skill",
        "class",
        "mastery",
        "stat",
        "modifier",
        "planner",
        "craft",
        "fixture",
        "fallback",
        "debug",
        "demo",
    )
    return any(term in rel for term in terms)


def read_text_limited(path: Path, *, limit: int = 500_000) -> str:
    try:
        if path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def build_inventory(root: Path, paths: list[Path] | None = None) -> dict[str, Any]:
    files = paths if paths is not None else discover_files(root)
    text_by_path = {
        path.relative_to(root).as_posix(): read_text_limited(path)
        for path in files
    }
    sources = []
    for path in files:
        relative = path.relative_to(root)
        text = text_by_path.get(relative.as_posix(), "")
        source = classify_source(relative, text)
        source["current_consumer_paths"] = find_consumers(relative, text_by_path)
        sources.append(source)

    summary = {
        "source_count": len(sources),
        "by_data_category": _counter_summary(source["data_category"] for source in sources),
        "by_source_kind": _counter_summary(source["source_kind"] for source in sources),
        "by_current_trust_status": _counter_summary(
            source["current_trust_status"] for source in sources
        ),
        "by_migration_priority": _counter_summary(
            source["migration_priority"] for source in sources
        ),
        "replace_or_remap_count": sum(
            1 for source in sources if source["should_be_replaced_or_remapped"]
        ),
        "runtime_category_count": sum(
            1 for source in sources if source["data_category"] in RUNTIME_CATEGORIES
        ),
    }
    return {
        "summary": summary,
        "sources": sources,
        "metadata": {
            "phase": "phase_1_source_inventory",
            "generated_on": date.today().isoformat(),
            "read_only": True,
            "production_safe": False,
            "checkpoint": "checkpoint_1",
            "source": "repository_file_inventory",
            "classification_policy": "path_name_and_reference_heuristics_no_gameplay_inference",
        },
    }


def classify_source(relative_path: Path, text: str = "") -> dict[str, Any]:
    rel = relative_path.as_posix()
    rel_lower = rel.lower()
    haystack = f"{rel_lower}\n{text[:50_000].lower()}"
    category = classify_category(rel_lower, haystack)
    source_kind = classify_source_kind(rel_lower)
    trust_status = classify_trust_status(category, source_kind, rel_lower)
    replace_or_remap = should_replace_or_remap(category, source_kind, rel_lower)
    should_remain = should_remain_for_v2(source_kind, replace_or_remap, rel_lower)
    return {
        "source_path": rel,
        "data_category": category,
        "current_consumer_paths": [],
        "current_trust_status": trust_status,
        "source_kind": source_kind,
        "should_remain_for_v2": should_remain,
        "should_be_replaced_or_remapped": replace_or_remap,
        "migration_priority": migration_priority(category, source_kind, rel_lower),
        "notes_risk": notes_for(category, source_kind, rel_lower),
    }


def classify_category(rel_lower: str, haystack: str) -> str:
    if rel_lower.startswith("docs/generated/"):
        return "generated_files"
    if "fixture" in rel_lower or "fixtures" in rel_lower:
        return "fixtures"
    if "fallback" in rel_lower or "sentinel" in rel_lower or "sample" in rel_lower:
        return "fallback_data"
    if "debug" in rel_lower or "demo" in rel_lower or "mock" in rel_lower:
        return "debug_demo_data"
    if rel_lower.startswith(("backend/tests/", "frontend/src/__tests__/")):
        return "tests_with_runtime_assumptions"
    if rel_lower.endswith(".json") and rel_lower.startswith(("data/", "backend/app/game_data/", "frontend/src/data/")):
        return "static_json_files"
    for category, terms in CATEGORY_TERMS.items():
        if category in {"generated_files", "static_json_files"}:
            continue
        if any(term in haystack for term in terms):
            return category
    return "unknown"


def classify_source_kind(rel_lower: str) -> str:
    if rel_lower.startswith("docs/generated/"):
        return "generated"
    if "fixture" in rel_lower or "fixtures" in rel_lower:
        return "fixture"
    if "fallback" in rel_lower or "sentinel" in rel_lower or "sample" in rel_lower:
        return "fallback"
    if "debug" in rel_lower or "demo" in rel_lower or "mock" in rel_lower:
        return "debug_demo"
    if rel_lower.startswith(("data/", "backend/app/game_data/")) and rel_lower.endswith(".json"):
        return "extracted"
    if rel_lower.endswith(".json"):
        return "static_json"
    if rel_lower.startswith(("backend/app/constants/", "backend/src/constants/", "frontend/src/constants/")):
        return "manual"
    if rel_lower.startswith("backend/scripts/"):
        return "manual"
    return "unknown"


def classify_trust_status(category: str, source_kind: str, rel_lower: str) -> str:
    if source_kind == "generated":
        return "partial"
    if source_kind == "extracted":
        return "partial"
    if source_kind in {"fixture", "fallback", "debug_demo"}:
        return "unsupported"
    if category in {"frontend_mappings", "backend_mappings", "planner_constants"}:
        return "unknown"
    if rel_lower.startswith("docs/migration/"):
        return "text_only"
    return "unknown"


def should_replace_or_remap(category: str, source_kind: str, rel_lower: str) -> bool:
    if source_kind in {"fixture", "debug_demo"}:
        return False
    if rel_lower.startswith("docs/"):
        return False
    return category in RUNTIME_CATEGORIES or source_kind in {"manual", "static_json", "fallback"}


def should_remain_for_v2(source_kind: str, replace_or_remap: bool, rel_lower: str) -> str:
    if rel_lower.startswith("docs/"):
        return "yes_audit_record"
    if source_kind == "fixture":
        return "test_only"
    if source_kind == "debug_demo":
        return "debug_only"
    if source_kind == "fallback":
        return "temporary_fallback_only"
    if replace_or_remap:
        return "temporary_until_remapped"
    return "review"


def migration_priority(category: str, source_kind: str, rel_lower: str) -> str:
    if rel_lower.startswith("docs/"):
        return "low"
    if source_kind in {"fixture", "debug_demo"}:
        return "medium"
    if category in {
        "affixes",
        "items",
        "item_bases",
        "implicits",
        "idols",
        "uniques",
        "sets",
        "passive_trees",
        "skill_trees",
        "skills",
        "classes_masteries",
        "stats_modifiers",
    }:
        return "critical"
    if category in {"planner_constants", "frontend_mappings", "backend_mappings", "static_json_files"}:
        return "high"
    return "medium"


def notes_for(category: str, source_kind: str, rel_lower: str) -> str:
    notes = []
    if category in RUNTIME_CATEGORIES:
        notes.append("Runtime-adjacent data or mapping must be reconciled with trusted v2 contracts.")
    if source_kind == "manual":
        notes.append("Manual bridge data needs provenance review before v2 consumption.")
    if source_kind == "fixture":
        notes.append("Fixture may hide runtime assumptions; keep test-only.")
    if source_kind == "fallback":
        notes.append("Fallback data must not become silent trusted runtime data.")
    if source_kind == "debug_demo":
        notes.append("Debug/demo data must remain outside stable planner behavior.")
    if rel_lower.startswith("docs/generated/"):
        notes.append("Generated diagnostic output is useful for audit history but not a runtime source.")
    return " ".join(notes) if notes else "Review provenance and consumers before v2 use."


def find_consumers(relative_path: Path, text_by_path: dict[str, str]) -> list[str]:
    rel = relative_path.as_posix()
    rel_lower = rel.lower()
    name = relative_path.name
    stem = relative_path.stem
    tokens = {
        rel,
        rel.replace("/", "\\"),
        name,
    }
    if len(stem) >= 6:
        tokens.add(stem)
    consumers = []
    for path, text in text_by_path.items():
        if path == rel or not text:
            continue
        path_lower = path.lower()
        if path_lower.startswith("docs/"):
            continue
        text_lower = text.lower()
        if any(token.lower() in text_lower for token in tokens):
            consumers.append(path)
        if len(consumers) >= 20:
            break
    return consumers


def render_markdown(report: dict[str, Any], *, command: str) -> str:
    summary = report["summary"]
    sources = report["sources"]
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    top_sources = sorted(
        sources,
        key=lambda item: (
            priority_order.get(item["migration_priority"], 9),
            item["data_category"],
            item["source_path"],
        ),
    )[:80]
    category_rows = _markdown_count_rows(summary["by_data_category"])
    kind_rows = _markdown_count_rows(summary["by_source_kind"])
    trust_rows = _markdown_count_rows(summary["by_current_trust_status"])
    priority_rows = _markdown_count_rows(summary["by_migration_priority"])
    top_rows = "\n".join(
        "| {source_path} | {data_category} | {source_kind} | {current_trust_status} | {migration_priority} | {should_remain_for_v2} | {should_be_replaced_or_remapped} |".format(
            **source
        )
        for source in top_sources
    )
    return f"""# EpochForge v2 Source Inventory

## Purpose

This Phase 1 report inventories current data sources, mappings, fixtures, fallback paths, and generated diagnostics that may affect the trusted data rebuild. It is read-only and does not define v2 contracts.

## Generation Command

```powershell
{command}
```

## Summary

- Source count: {summary["source_count"]}
- Runtime-adjacent source count: {summary["runtime_category_count"]}
- Replace or remap count: {summary["replace_or_remap_count"]}
- Generated on: {report["metadata"]["generated_on"]}
- Checkpoint: {report["metadata"]["checkpoint"]}

## Data Category Counts

| Data category | Count |
| --- | ---: |
{category_rows}

## Source Kind Counts

| Source kind | Count |
| --- | ---: |
{kind_rows}

## Current Trust Status Counts

| Trust status | Count |
| --- | ---: |
{trust_rows}

## Migration Priority Counts

| Priority | Count |
| --- | ---: |
{priority_rows}

## High-Priority Inventory Slice

| Source path | Data category | Source kind | Trust status | Priority | v2 disposition | Replace/remap |
| --- | --- | --- | --- | --- | --- | --- |
{top_rows}

## Important Findings

- The repo contains both extracted/static JSON and manual mapping/constants paths. v2 needs explicit provenance before any runtime path treats them as trusted.
- Existing generated diagnostics are valuable audit records, but they are not runtime sources.
- Fixtures, samples, fallback records, and debug/demo paths are widespread enough that tests may currently encode behavior that should remain test-only.
- Planner, crafting, stat, and simulation paths depend on manual constants and mapping layers that need contract review before replacement.

## Remaining Risks

- Consumer detection is path and token based; it should be treated as an inventory aid, not a dependency graph.
- Trust status is conservative. Unknown and partial sources need source-specific validation in later phases.
- This report does not approve any data contract, gameplay calculation, adapter, or runtime behavior change.

## Checkpoint 1

Checkpoint 1 is ready for review when the JSON report validates, this markdown report is reviewed, and no Phase 2 contract work has started.
"""


def _counter_summary(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _markdown_count_rows(counts: dict[str, int]) -> str:
    return "\n".join(f"| {key} | {value} |" for key, value in sorted(counts.items()))


def main() -> None:
    args = parse_args()
    report = build_inventory(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_source_inventory.py "
        f"--output {_display_path(args.output)} "
        f"--markdown-output {_display_path(args.markdown_output)}"
    )
    markdown = render_markdown(report, command=command)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(markdown, encoding="utf-8")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix().replace("/", "\\")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
