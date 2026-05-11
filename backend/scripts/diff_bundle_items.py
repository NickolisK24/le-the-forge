"""Developer command for read-only bundle item family diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.game_data.bundle_compat import resolve_bundle_dir  # noqa: E402
from app.game_data.bundle_item_diff import (  # noqa: E402
    STATUS_FAIL,
    run_item_bundle_diff,
)


def _print_examples(examples: list[object]) -> None:
    for example in examples:
        print(f"    - {example}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff bundle item_types/base_items against current Forge data sources.")
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        help="Bundle directory. Defaults to FORGE_DATA_BUNDLE_DIR or D:\\Forge\\last-epoch-data\\data_bundle.",
    )
    parser.add_argument("--json", action="store_true", help="Print the diagnostic result as JSON.")
    args = parser.parse_args()

    bundle_dir = resolve_bundle_dir(args.bundle_dir)
    result = run_item_bundle_diff(bundle_dir)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"Bundle path: {result.bundle_dir}")
        print(f"Status: {result.status}")
        print(f"Bundle item_types: {result.bundle_item_types_count}")
        print(f"Bundle base_items: {result.bundle_base_items_count}")
        print("")
        print("Forge sources inspected")
        for source in result.forge_sources_inspected:
            print(f"  - {source}")
        print("")
        print("Comparison methods")
        for method in result.comparison_methods:
            print(f"  - {method}")
        print("")
        print("Item type summary")
        for key, value in result.item_type_summary.items():
            print(f"  {key}: {value}")
        print("")
        print("Base item summary")
        for key, value in result.base_item_summary.items():
            print(f"  {key}: {value}")
        print("")
        print("Findings")
        if result.findings:
            for finding in result.findings:
                print(f"  {finding.status}: {finding.message}")
                _print_examples(finding.examples)
        else:
            print("  none")
        print("")
        print("Subtype identity risks")
        if result.subtype_identity_risks:
            for risk in result.subtype_identity_risks:
                print(f"  - {risk}")
        else:
            print("  none")
        print("")
        print(f"Recommendation: {result.recommendation}")

    return 1 if result.status == STATUS_FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
