"""Developer command for LE Tools raw-stage vs mapped-output context diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_item_adapter_report import validate_output_path  # noqa: E402
from app.game_data.le_tools_import_stage_context_report import (  # noqa: E402
    DEFAULT_STAGE_FIXTURE,
    build_stage_context_report,
    load_stage_fixture,
    render_stage_context_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare LET raw and mapped item type context.")
    parser.add_argument("--fixture", type=Path, default=DEFAULT_STAGE_FIXTURE)
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path.")
    args = parser.parse_args()

    try:
        report = build_stage_context_report(load_stage_fixture(args.fixture))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    content = (
        json.dumps(report, indent=2, sort_keys=True)
        if args.json
        else render_stage_context_report(report)
    )
    if args.output:
        try:
            validate_output_path(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote LE Tools stage context report: {args.output}")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
