"""Generate the Phase 2 canonical contract report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.data_contracts import SupportStatus, TrustLevel
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "v2_canonical_contract_report.json"
DEFAULT_MARKDOWN_OUTPUT = ROOT / "docs" / "migration" / "V2_CANONICAL_DATA_CONTRACT.md"

BACKEND_MODULES = [
    "backend/app/data_contracts/trust_status.py",
    "backend/app/data_contracts/trust_level.py",
    "backend/app/data_contracts/source_provenance.py",
    "backend/app/data_contracts/canonical_id.py",
    "backend/app/data_contracts/canonical_modifier.py",
    "backend/app/data_contracts/canonical_affix.py",
    "backend/app/data_contracts/canonical_item.py",
    "backend/app/data_contracts/canonical_idol.py",
    "backend/app/data_contracts/canonical_unique.py",
    "backend/app/data_contracts/canonical_set.py",
    "backend/app/data_contracts/canonical_class_mastery.py",
    "backend/app/data_contracts/canonical_passive.py",
    "backend/app/data_contracts/canonical_skill.py",
    "backend/app/data_contracts/validation.py",
]

FRONTEND_TYPES = [
    "frontend/src/types/trustStatus.ts",
    "frontend/src/types/sourceProvenance.ts",
    "frontend/src/types/canonicalBase.ts",
    "frontend/src/types/canonicalModifier.ts",
    "frontend/src/types/canonicalAffix.ts",
    "frontend/src/types/canonicalItem.ts",
    "frontend/src/types/canonicalIdol.ts",
    "frontend/src/types/canonicalUnique.ts",
    "frontend/src/types/canonicalSet.ts",
    "frontend/src/types/canonicalClassMastery.ts",
    "frontend/src/types/canonicalPassive.ts",
    "frontend/src/types/canonicalSkill.ts",
]

CANONICAL_MODELS = [
    "CanonicalRecord",
    "CanonicalModifierReference",
    "CanonicalModifier",
    "CanonicalAffix",
    "CanonicalImplicit",
    "CanonicalItemBase",
    "CanonicalIdol",
    "CanonicalUnique",
    "CanonicalSetItem",
    "CanonicalSet",
    "CanonicalClass",
    "CanonicalMastery",
    "CanonicalPassiveNode",
    "CanonicalPassiveTree",
    "CanonicalSkill",
    "CanonicalSkillTreeNode",
    "CanonicalSkillTree",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the v2 canonical contract report.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    return parser.parse_args()


def build_report() -> dict[str, Any]:
    return {
        "summary": {
            "support_status_count": len(SupportStatus),
            "trust_level_count": len(TrustLevel),
            "backend_contract_module_count": len(BACKEND_MODULES),
            "frontend_type_file_count": len(FRONTEND_TYPES),
            "canonical_model_count": len(CANONICAL_MODELS),
            "production_consumed": False,
        },
        "support_statuses": [status.value for status in SupportStatus],
        "trust_levels": [level.value for level in TrustLevel],
        "backend_contract_modules": BACKEND_MODULES,
        "frontend_type_files": FRONTEND_TYPES,
        "canonical_models": CANONICAL_MODELS,
        "stable_calculation_policy": {
            "stable_calculable_support_statuses": ["trusted"],
            "blocked_support_statuses": [
                "unknown",
                "unsupported",
                "text_only",
                "experimental",
            ],
            "blocked_trust_levels": ["placeholder", "inferred", "deprecated", "manual_bridge"],
            "partial_requires_policy": True,
            "manual_bridge_requires_explicit_marking": True,
        },
        "deferred_until_later_phases": [
            "bundle generation",
            "backend repository loading",
            "API route changes",
            "frontend runtime consumption",
            "planner remapping",
            "crafting remapping",
            "stat aggregation remapping",
            "simulation remapping",
        ],
        "metadata": {
            "phase": "phase_2_canonical_data_contract",
            "generated_on": date.today().isoformat(),
            "read_only_report": True,
            "production_safe": False,
            "checkpoint": "checkpoint_2",
            "source": "canonical_contract_modules",
        },
    }


def render_markdown(report: dict[str, Any], *, command: str) -> str:
    support_rows = "\n".join(
        f"| `{status}` | {meaning} |"
        for status, meaning in [
            ("trusted", "Structured, validated, and allowed for stable use."),
            ("partial", "Structured in part, but requires explicit policy before calculation."),
            ("text_only", "Displayable only; not calculated."),
            ("unsupported", "Known but not supported for calculation."),
            ("experimental", "Isolated from stable behavior."),
            ("unknown", "Not classified enough for stable calculation."),
        ]
    )
    trust_rows = "\n".join(
        f"| `{level}` | {meaning} |"
        for level, meaning in [
            ("game_extracted", "Direct accepted game-data extract."),
            ("generated_from_game_data", "Deterministically generated from accepted extracts."),
            ("manual_bridge", "Explicit temporary compatibility bridge."),
            ("inferred", "Derived from incomplete evidence; not silently trusted."),
            ("placeholder", "Temporary scaffold; never stable planner eligible."),
            ("deprecated", "Retained only for compatibility or audit history."),
        ]
    )
    backend_rows = "\n".join(f"| `{path}` |" for path in report["backend_contract_modules"])
    frontend_rows = "\n".join(f"| `{path}` |" for path in report["frontend_type_files"])
    model_rows = "\n".join(f"| `{model}` |" for model in report["canonical_models"])
    return f"""# v2 Canonical Data Contract

## Purpose

The canonical contract defines the shared language later v2 phases must use for trusted data. It establishes support status, trust level, provenance, stable IDs, modifier references, and canonical shapes for major Last Epoch data categories.

This phase does not generate gameplay bundles, remap planner behavior, change crafting behavior, alter stat aggregation, or change simulation.

## Generation Command

```powershell
{command}
```

## Support Statuses

| Status | Meaning |
| --- | --- |
{support_rows}

## Trust Levels

| Trust level | Meaning |
| --- | --- |
{trust_rows}

## Provenance Requirements

Every canonical record requires `provenance`. Generated records must identify source path, source type, extraction method, schema version, and patch/version when available. Manual bridges must remain explicitly marked as `manual_bridge`.

## Stable vs Experimental Rules

- Stable calculation eligibility defaults to `trusted` plus `game_extracted` or `generated_from_game_data`.
- `unknown`, `unsupported`, `text_only`, and `experimental` records are displayable but not stable-calculable.
- `partial` records require later policy before stable calculation.
- `placeholder`, `inferred`, `deprecated`, and `manual_bridge` records are not stable planner eligible by default.
- Tooltip text must not be used to infer mechanics.

## Backend Contract Modules

| Module |
| --- |
{backend_rows}

## Frontend Type Files

| Type file |
| --- |
{frontend_rows}

## Canonical Models

| Model |
| --- |
{model_rows}

## How Later Phases Should Use This

Later phases should build ingestion, generated bundles, repositories, APIs, frontend consumers, and planner/debug behavior on these contracts. Any generated bundle should validate canonical IDs, support status, trust level, and provenance before becoming a candidate for consumption.

## Deferred Until Later Phases

- Bundle generation.
- Backend repository loading.
- Runtime API route changes.
- Frontend runtime consumption.
- Planner, crafting, stat aggregation, and simulation remapping.
- Item, affix, passive, skill, unique, set, and idol generation.

## Checkpoint 2

Checkpoint 2 is ready for review when the contract modules, frontend types, report, and focused tests pass.
"""


def main() -> None:
    args = parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    command = (
        ".\\backend\\.venv\\Scripts\\python.exe backend\\scripts\\report_v2_canonical_contract.py "
        f"--output {_display_path(args.output)} "
        f"--markdown-output {_display_path(args.markdown_output)}"
    )
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(report, command=command), encoding="utf-8")


def _display_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix().replace("/", "\\")


if __name__ == "__main__":
    main()
