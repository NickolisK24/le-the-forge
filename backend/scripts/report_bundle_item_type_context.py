"""Developer command for bundle item type context coverage diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.bundle_item_type_context_report import (  # noqa: E402
    build_context_coverage_report,
    render_context_coverage_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report bundle item type base_type_id context coverage.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path. Refuses production data paths.",
    )
    args = parser.parse_args()

    report = build_context_coverage_report()
    content = (
        json.dumps(report, indent=2, sort_keys=True)
        if args.json
        else render_context_coverage_report(report)
    )

    if args.output:
        try:
            validate_output_path(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote context coverage report: {args.output}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
