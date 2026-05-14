"""Inspect a Forge-safe canonical affix export.

Developer-only command. This script validates an explicit export path through
the controlled Forge-safe affix loader and prints a small summary. It does not
wire the export into production loaders, APIs, frontend behavior, crafting, or
simulation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from data.loaders.forge_safe_affixes_loader import (  # noqa: E402
    ForgeSafeAffixLoader,
    ForgeSafeAffixLoaderError,
)


def build_inspection_summary(path: str | Path, *, limit: int = 5) -> dict[str, Any]:
    """Load a Forge-safe affix export and return a serializable summary."""

    result = ForgeSafeAffixLoader().load(path)
    sample_limit = max(0, limit)
    return {
        "success": True,
        "source_path": str(result.source_path),
        "count": result.count,
        "warning_count": len(result.warnings),
        "warnings": list(result.warnings),
        "export_policy": result.export_policy,
        "summary": result.summary,
        "sample_records": [_sample_record(record) for record in result.records[:sample_limit]],
    }


def render_inspection_summary(summary: dict[str, Any]) -> str:
    """Render a human-readable inspection summary."""

    lines = [
        "Forge-safe canonical affix export inspection",
        f"source_path: {summary['source_path']}",
        f"loaded_record_count: {summary['count']}",
        f"warning_count: {summary['warning_count']}",
        f"export_policy: {summary.get('export_policy') or 'n/a'}",
        "",
        "Export summary:",
    ]
    export_summary = summary.get("summary") or {}
    if export_summary:
        for key in sorted(export_summary):
            lines.append(f"- {key}: {export_summary[key]}")
    else:
        lines.append("- none")

    lines.extend(["", "Warnings:"])
    if summary["warnings"]:
        lines.extend(f"- {warning}" for warning in summary["warnings"])
    else:
        lines.append("- none")

    lines.extend(["", "Sample records:"])
    if summary["sample_records"]:
        for record in summary["sample_records"]:
            lines.append(
                "- "
                f"affix_id={record['affix_id']} "
                f"name={record.get('name') or 'n/a'} "
                f"source_type={record.get('source_type') or 'n/a'}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a Forge-safe canonical affix export without wiring it into production."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to forge_safe_canonical_affixes.json.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum sample records to print.")
    args = parser.parse_args(argv)

    try:
        summary = build_inspection_summary(args.input, limit=args.limit)
    except (FileNotFoundError, ForgeSafeAffixLoaderError) as exc:
        if args.json:
            print(json.dumps({"success": False, "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_inspection_summary(summary))
    return 0


def _sample_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "affix_id": record.get("affix_id"),
        "name": record.get("affix_name") or record.get("display_name"),
        "source_type": record.get("source_type"),
        "item_type": record.get("item_type"),
        "eligible_item_types": record.get("eligible_item_types") or [],
    }


if __name__ == "__main__":
    raise SystemExit(main())
