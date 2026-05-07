"""Developer command for proposed bundle item_type adapter mappings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_compat import resolve_bundle_dir  # noqa: E402
from app.game_data.bundle_item_adapter_report import (  # noqa: E402
    generate_adapter_report,
    render_adapter_report,
    validate_output_path,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose developer-only item_type adapter mappings.")
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        help="Bundle directory. Defaults to FORGE_DATA_BUNDLE_DIR or D:\\Forge\\last-epoch-data\\data_bundle.",
    )
    parser.add_argument("--json", action="store_true", help="Print report as JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for the report. Refuses production data paths.",
    )
    args = parser.parse_args()

    bundle_dir = resolve_bundle_dir(args.bundle_dir)
    report = generate_adapter_report(bundle_dir)
    content = (
        json.dumps(report.to_dict(), indent=2, sort_keys=True)
        if args.json
        else render_adapter_report(report)
    )

    if args.output:
        try:
            validate_output_path(args.output)
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content + "\n", encoding="utf-8")
        print(f"Wrote adapter report: {args.output}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
