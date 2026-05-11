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
    assert_report_safety_invariants,
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
        "--assert-current-report",
        action="store_true",
        help="Assert broad diagnostic safety invariants for the current report.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path for the report. Refuses production data paths.",
    )
    args = parser.parse_args()

    bundle_dir = resolve_bundle_dir(args.bundle_dir)
    report = generate_adapter_report(bundle_dir)
    if args.assert_current_report:
        errors, warnings = assert_report_safety_invariants(report)
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "FAIL" if errors else "PASS",
                        "errors": errors,
                        "warnings": warnings,
                        "readiness_counts": report.readiness_counts,
                        "match_method_counts": report.match_method_counts,
                        "unmapped_forge_types": report.unmapped_forge_types,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(f"Bundle path: {bundle_dir}")
            print(f"Adapter invariant status: {'FAIL' if errors else 'PASS'}")
            print("")
            print("Safety invariants checked:")
            print("- production_safe is false for all records")
            print("- subtype_id-only mappings are not used")
            print("- Ready candidate mappings exist")
            print("- Needs adapter mappings exist")
            print("- Deferred or Needs review mappings exist")
            print("- readiness and match method counts are present")
            print("")
            print("Errors:")
            for error in errors or ["none"]:
                print(f"- {error}")
            print("")
            print("Warnings:")
            for warning in warnings or ["none"]:
                print(f"- {warning}")
        return 1 if errors else 0

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
