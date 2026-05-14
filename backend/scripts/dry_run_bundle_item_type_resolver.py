"""Developer command for dry-running reviewed bundle item type mappings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.bundle_item_type_dry_run_resolver import (  # noqa: E402
    BundleItemTypeDryRunResolver,
    DryRunResolution,
    summarize_resolutions,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run reviewed bundle item type resolver diagnostics.")
    parser.add_argument(
        "--sample",
        action="append",
        default=[],
        help="Sample input as forge_item_type or forge_item_type:base_type_id. Can be repeated.",
    )
    parser.add_argument(
        "--current-forge",
        action="store_true",
        help="Dry-run current BASE_TYPE_ID_TO_ITEM_TYPE_ID constants.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path. Refuses production data paths.",
    )
    args = parser.parse_args()

    resolver = BundleItemTypeDryRunResolver()
    samples = _build_samples(args.sample, args.current_forge)
    results = [resolver.resolve(item_type, base_type_id) for item_type, base_type_id in samples]
    summary = summarize_resolutions(results)
    content = json.dumps(summary, indent=2, sort_keys=True) if args.json else _render_summary(summary, results)

    if args.output:
        try:
            validate_output_path(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote dry-run resolver report: {args.output}")
    else:
        print(content)
    return 0


def _build_samples(raw_samples: list[str], include_current_forge: bool) -> list[tuple[str, int | None]]:
    samples: list[tuple[str, int | None]] = []
    for raw in raw_samples:
        if ":" in raw:
            item_type, raw_base_type_id = raw.split(":", 1)
            samples.append((item_type, int(raw_base_type_id)))
        else:
            samples.append((raw, None))
    if include_current_forge or not samples:
        from app.constants.base_type_id_to_item_type_id import BASE_TYPE_ID_TO_ITEM_TYPE_ID
        from app.constants.item_type_ids import ITEM_TYPE_IDS

        samples.extend(
            (forge_item_type, int(base_type_id))
            for base_type_id, forge_item_type in sorted(BASE_TYPE_ID_TO_ITEM_TYPE_ID.items())
        )
        mapped_types = {forge_item_type for _base_type_id, forge_item_type in samples}
        samples.extend((forge_item_type, None) for forge_item_type in sorted(set(ITEM_TYPE_IDS) - mapped_types))
    return samples


def _render_summary(summary: dict, results: list[DryRunResolution]) -> str:
    lines = [
        "# Bundle Item Type Dry-Run Resolver",
        "",
        f"Total attempted: {summary['total_attempted']}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in summary["counts"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            f"subtype_id-only matching attempted: {summary['subtype_id_only_matching_attempted']}",
            f"subtype_id context warnings seen: {summary['subtype_id_context_warnings_seen']}",
            "",
            "## Examples",
            "",
        ]
    )
    by_status: dict[str, list[DryRunResolution]] = {}
    for result in results:
        by_status.setdefault(result.status, []).append(result)
    for status, status_results in by_status.items():
        lines.append(f"### {status}")
        for result in status_results[:10]:
            lines.append(
                f"- forge={result.forge_item_type} base_type_id={result.base_type_id} "
                f"bundle={result.bundle_item_type_id or 'null'} source={result.match_source} "
                "production_safe=false"
            )
            for warning in result.warnings:
                lines.append(f"  - WARN: {warning}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
